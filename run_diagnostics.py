import argparse
import functools
import json
from typing import Any

import numpy as np
import torch

from _bootstrap import module

harness = module("harness")
samplers = module("samplers")
history_filter = module("history_filter")
error_stats = module("error_stats")
run_error_structure = module("run_error_structure")

RESULTS = harness.ROOT / "results"
SIGMA_FLOOR: float = 1e-4
RULES: dict[str, Any] = {
    "euler": history_filter.euler_spec(),
    "ab2": history_filter.adams_bashforth_spec(2),
    "ab3": history_filter.adams_bashforth_spec(3),
    "ab4": history_filter.adams_bashforth_spec(4),
    "wls5": history_filter.wls_spec(5),
    "wls8": history_filter.wls_spec(8),
}
COMPONENTS: tuple[str, ...] = ("guided", "cond", "uncond", "guidance")


def to_numpy(value: torch.Tensor) -> np.ndarray:
    return value.detach().float().cpu().numpy().astype(np.float64).reshape(-1)


def record_trajectory(rig: Any, prompt: str, seed: int, steps: int, cfg: float) -> dict[str, Any]:
    taps: list[dict[str, Any]] = []

    def tap(arguments: dict[str, Any]) -> None:
        uncond = arguments["uncond_denoised"]
        taps.append(
            {
                "x": to_numpy(arguments["input"]),
                "sigma": float(arguments["sigma"].reshape(-1)[0]),
                "cond": to_numpy(arguments["cond_denoised"]),
                "uncond": None if uncond is None else to_numpy(uncond),
            }
        )

    sampler = functools.partial(samplers.sample_history, spec=history_filter.euler_spec(), disable=True)
    latent = rig.sample(prompt, seed, steps, sampler, cfg=cfg, tap=tap)
    sigmas = [float(value) for value in rig.sigmas(steps)]
    return {"taps": taps, "sigmas": sigmas, "shape": latent.shape, "cfg": cfg}


def velocity_components(record: dict[str, Any]) -> dict[str, np.ndarray]:
    taps, cfg = record["taps"], record["cfg"]
    levels = np.array([max(tap["sigma"], SIGMA_FLOOR) for tap in taps])[:, None]
    x = np.stack([tap["x"] for tap in taps])
    cond = (x - np.stack([tap["cond"] for tap in taps])) / levels
    components = {"cond": cond}
    if taps[0]["uncond"] is not None:
        uncond = (x - np.stack([tap["uncond"] for tap in taps])) / levels
        components["uncond"] = uncond
        components["guidance"] = cfg * (cond - uncond)
        components["guided"] = uncond + cfg * (cond - uncond)
    else:
        components["guided"] = cond
    return components


def consistency(series: np.ndarray, sigmas: list[float], spec: Any) -> list[float]:
    errors = []
    for index in range(1, series.shape[0] - 1):
        weights = history_filter.step_weights(sigmas, index, spec)
        increment = sum(float(weight) * series[index - lag] for lag, weight in enumerate(weights))
        oracle = (sigmas[index + 1] - sigmas[index]) * 0.5 * (series[index] + series[index + 1])
        errors.append(float(np.linalg.norm(increment - oracle) / max(np.linalg.norm(oracle), 1e-30)))
    return errors


def component_stats(series: np.ndarray, shape: tuple[int, ...]) -> dict[str, float]:
    norms = np.linalg.norm(series, axis=1)
    consecutive = np.sum(series[1:] * series[:-1], axis=1) / np.maximum(norms[1:] * norms[:-1], 1e-30)
    change = np.linalg.norm(series[1:] - series[:-1], axis=1) / np.maximum(norms[:-1], 1e-30)
    body = series[:-1]
    return {
        "cosine_consecutive": float(consecutive[:-1].mean()),
        "relative_change": float(change[:-1].mean()),
        "second_difference": error_stats.second_difference_ratio(body),
        "spatial_high": float(np.mean([error_stats.spatial_high_fraction(row.reshape(shape)) for row in body])),
        "norm_mean": float(norms[:-1].mean()),
    }


def trajectory_stats(record: dict[str, Any]) -> dict[str, Any]:
    components = velocity_components(record)
    sigmas, shape = record["sigmas"], tuple(record["shape"])
    result: dict[str, Any] = {"components": {}, "consistency": {}, "component_consistency": {}}
    for name, series in components.items():
        result["components"][name] = component_stats(series, shape)
    for rule, spec in RULES.items():
        result["consistency"][rule] = consistency(components["guided"], sigmas, spec)
    for name, series in components.items():
        if name != "guided":
            result["component_consistency"][name] = {"ab3": consistency(series, sigmas, RULES["ab3"]), "euler": consistency(series, sigmas, RULES["euler"])}
    if "guidance" in components:
        result["guidance_share"] = float(
            np.mean(np.linalg.norm(components["guidance"], axis=1) / np.linalg.norm(components["guided"], axis=1))
        )
    return result


def save(path, results: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    path.write_text(json.dumps(results), encoding="utf-8")


def run_trajectories(rig, cells, units, steps_list, results, path) -> None:
    for prompt, seed in units:
        for mode, cfg in cells:
            rig.use(mode)
            for steps in steps_list:
                key = f"trajectory|{mode}|{cfg:g}|{prompt}|{seed}|{steps}"
                if key in results:
                    continue
                results[key] = trajectory_stats(record_trajectory(rig, prompt, seed, steps, cfg))
        save(path, results)
        print(f"trajectories {prompt} s{seed} done", flush=True)


def run_structure(rig, cfgs, units, steps, reference_mode, quantized_mode, results, path) -> None:
    sigma_values = [float(value) for value in rig.sigmas(steps)]
    for prompt, seed in units:
        for cfg in cfgs:
            key = f"structure|{quantized_mode}|{cfg:g}|{prompt}|{seed}"
            if key in results:
                continue
            rig.use(reference_mode)
            trajectory: list = []
            latent = rig.sample(prompt, seed, steps, run_error_structure.recording_sampler(trajectory), cfg=cfg)
            reference_v = run_error_structure.velocities(trajectory, [item[2] for item in trajectory])
            rig.use(quantized_mode)
            outputs: list[torch.Tensor] = []
            rig.sample(prompt, seed, steps, run_error_structure.replay_sampler(trajectory, outputs), cfg=cfg)
            quant_v = run_error_structure.velocities(trajectory, outputs)
            results[key] = run_error_structure.analyse(reference_v, quant_v, sigma_values, latent.shape)
            print(
                f"{key}: rel={results[key]['relative_size_mean']:.4f} cos1={results[key]['cosine_lag1']:.3f} "
                f"resp(ab4)={results[key]['response']['ab4']['realised']:.2f}/{results[key]['response']['ab4']['white']:.2f}",
                flush=True,
            )
        save(path, results)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, choices=list(harness.MODEL_CONFIGS))
    parser.add_argument("--modes", nargs="+", required=True)
    parser.add_argument("--cfgs", nargs="+", type=float, required=True)
    parser.add_argument("--prompts", nargs="+", default=list(harness.PROMPTS))
    parser.add_argument("--seeds", nargs="+", type=int, default=[42, 1337])
    parser.add_argument("--steps", nargs="+", type=int, default=[])
    parser.add_argument("--structure-steps", type=int, default=0)
    parser.add_argument("--name", required=True)
    arguments = parser.parse_args()

    path = RESULTS / f"{arguments.name}.json"
    results: dict[str, Any] = json.loads(path.read_text()) if path.exists() else {}
    units = [(prompt, seed) for seed in arguments.seeds for prompt in arguments.prompts]
    harness.limit_gpu_memory()
    rig = harness.Rig(harness.MODEL_CONFIGS[arguments.model])
    try:
        if arguments.structure_steps:
            run_structure(rig, arguments.cfgs, units, arguments.structure_steps, "d", "q", results, path)
        if arguments.steps:
            cells = [(mode, cfg) for cfg in arguments.cfgs for mode in arguments.modes]
            run_trajectories(rig, cells, units, arguments.steps, results, path)
    finally:
        save(path, results)
    rig.release()


if __name__ == "__main__":
    main()
