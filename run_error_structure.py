import argparse
import functools
import json
import pathlib
from typing import Any

import numpy as np
import torch

from _bootstrap import module

harness = module("harness")
samplers = module("samplers")
history_filter = module("history_filter")
fakequant = module("fakequant")
error_stats = module("error_stats")

RESULTS: pathlib.Path = harness.ROOT / "results"
QUANT_NAMES: list[str] = [name for name in fakequant.SPECS if name != "bf16"]
RESPONSE_METHODS: dict[str, Any] = {
    "euler": history_filter.euler_spec(),
    "ab2": history_filter.adams_bashforth_spec(2),
    "ab3": history_filter.adams_bashforth_spec(3),
    "ab4": history_filter.adams_bashforth_spec(4),
    "wls5": history_filter.wls_spec(5),
    "wls8": history_filter.wls_spec(8),
}
SIGMA_FLOOR: float = 1e-4


def recording_sampler(store: list[tuple[torch.Tensor, torch.Tensor, torch.Tensor]]):
    def sampler(model, x, sigmas, extra_args=None, callback=None, disable=None):
        def logged(x_in, sigma, **kwargs):
            denoised = model(x_in, sigma, **kwargs)
            store.append((x_in.detach().clone().cpu(), sigma.detach().clone().cpu(), denoised.detach().clone().cpu()))
            return denoised

        return samplers.sample_history(
            logged, x, sigmas, extra_args=extra_args, callback=callback, disable=disable,
            spec=history_filter.wls_spec(5),
        )

    return sampler


def replay_sampler(
    trajectory: list[tuple[torch.Tensor, torch.Tensor, torch.Tensor]],
    outputs: list[torch.Tensor],
):
    def sampler(model, x, sigmas, extra_args=None, callback=None, disable=None):
        extra_args = {} if extra_args is None else extra_args
        for stored_x, stored_sigma, _ in trajectory:
            device_x = stored_x.to(x.device)
            ones = x.new_ones([x.shape[0]])
            outputs.append(model(device_x, stored_sigma.to(x.device)[0] * ones, **extra_args).detach().cpu())
        return x

    return sampler


def velocities(trajectory, denoised: list[torch.Tensor]) -> np.ndarray:
    rows = []
    for (x, sigma, _), out in zip(trajectory, denoised):
        level = max(float(sigma.reshape(-1)[0]), SIGMA_FLOOR)
        rows.append(((x - out) / level).float().numpy().reshape(-1).astype(np.float64))
    return np.stack(rows)


def save_velocities(key: str, reference_v: np.ndarray, quant_v: np.ndarray) -> None:
    path = harness.DUMPS / "velocities" / (key.replace("|", "__") + ".npz")
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, reference=reference_v.astype(np.float32), quantized=quant_v.astype(np.float32))


def analyse(
    reference_v: np.ndarray,
    quant_v: np.ndarray,
    sigmas: list[float],
    shape: tuple[int, ...],
) -> dict[str, Any]:
    errors = quant_v - reference_v
    body_errors, body_signal = errors[:-1], reference_v[:-1]
    sizes = error_stats.relative_size(errors, reference_v)
    result: dict[str, Any] = {
        "relative_size_mean": float(sizes[:-1].mean()),
        "relative_size_last": float(sizes[-1]),
        "relative_size_by_step": sizes.tolist(),
        "cosine_lag1": float(error_stats.lagged_cosine(body_errors, 1).mean()),
        "cosine_lag2": float(error_stats.lagged_cosine(body_errors, 2).mean()),
        "cosine_lag1_by_step": error_stats.lagged_cosine(body_errors, 1).tolist(),
        "second_difference_ratio": error_stats.second_difference_ratio(body_errors),
        "second_difference_ratio_signal": error_stats.second_difference_ratio(body_signal),
        "spatial_high_error": float(np.mean([error_stats.spatial_high_fraction(e.reshape(shape)) for e in body_errors])),
        "spatial_high_signal": float(np.mean([error_stats.spatial_high_fraction(v.reshape(shape)) for v in body_signal])),
        "response": {},
    }
    for name, spec in RESPONSE_METHODS.items():
        response = error_stats.accumulated_response(errors, sigmas, spec)
        result["response"][name] = {"realised": response.realised, "white": response.white}
    return result


def run(prompts: list[str], seeds: list[int], steps: int) -> dict[str, Any]:
    rig = harness.Rig()
    summary: dict[str, Any] = {}
    sigma_values = [float(value) for value in rig.sigmas(steps)]
    for prompt in prompts:
        for seed in seeds:
            rig.weights.release()
            trajectory: list = []
            latent = rig.sample(prompt, seed, steps, recording_sampler(trajectory))
            shape = latent.shape
            reference_v = velocities(trajectory, [item[2] for item in trajectory])
            for name in QUANT_NAMES:
                rig.use(name)
                outputs: list[torch.Tensor] = []
                rig.sample(prompt, seed, steps, replay_sampler(trajectory, outputs))
                quant_v = velocities(trajectory, outputs)
                key = f"{name}|{prompt}|{seed}"
                save_velocities(key, reference_v, quant_v)
                summary[key] = analyse(reference_v, quant_v, sigma_values, shape)
                print(
                    f"{key}: rel={summary[key]['relative_size_mean']:.4f} "
                    f"cos1={summary[key]['cosine_lag1']:.3f} "
                    f"resp(ab4)={summary[key]['response']['ab4']['realised']:.2f}"
                    f"/{summary[key]['response']['ab4']['white']:.2f}",
                    flush=True,
                )
            rig.weights.release()
    return summary


def aggregate(summary: dict[str, Any]) -> str:
    lines: list[str] = []
    header = (
        "spec      | rel.size | cos lag1 | cos lag2 | 2nd-diff | sp.HF err/sig | "
        + " | ".join(f"{m}: real/white" for m in RESPONSE_METHODS)
    )
    lines.append(header)
    for name in QUANT_NAMES:
        rows = [value for key, value in summary.items() if key.startswith(f"{name}|")]
        if not rows:
            continue

        def mean(path):
            return np.mean([path(r) for r in rows])

        cells = [
            f"{name:<9}",
            f"{mean(lambda r: r['relative_size_mean']):8.4f}",
            f"{mean(lambda r: r['cosine_lag1']):8.3f}",
            f"{mean(lambda r: r['cosine_lag2']):8.3f}",
            f"{mean(lambda r: r['second_difference_ratio']):8.3f}",
            f"{mean(lambda r: r['spatial_high_error']):.3f}/{mean(lambda r: r['spatial_high_signal']):.3f}",
        ]
        for method in RESPONSE_METHODS:
            real = mean(lambda r: r["response"][method]["realised"])
            white = mean(lambda r: r["response"][method]["white"])
            cells.append(f"{real:5.2f}/{white:5.2f}")
        lines.append(" | ".join(cells))
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompts", nargs="+", default=list(harness.PROMPTS))
    parser.add_argument("--seeds", nargs="+", type=int, default=[42, 1337])
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--output", type=pathlib.Path, default=RESULTS / "error_structure.json")
    arguments = parser.parse_args()
    RESULTS.mkdir(exist_ok=True)
    summary = run(arguments.prompts, arguments.seeds, arguments.steps)
    arguments.output.write_text(json.dumps(summary), encoding="utf-8")
    print(aggregate(summary))


if __name__ == "__main__":
    main()
