import argparse
import dataclasses
import json
import pathlib
from typing import Any, Callable

import numpy as np
import torch

from _bootstrap import module

history_filter = module("history_filter")
samplers = module("samplers")

RESULTS: pathlib.Path = pathlib.Path(__file__).resolve().parent / "results"
DIMENSION: int = 256
SHIFT: float = 3.0
REFERENCE_STEPS: int = 600
SIGMA_FLOOR: float = 1e-4


def shifted_sigmas(steps: int, shift: float = SHIFT) -> torch.Tensor:
    grid: torch.Tensor = torch.linspace(1.0, 0.0, steps + 1, dtype=torch.float64)
    return shift * grid / (1.0 + (shift - 1.0) * grid)


@dataclasses.dataclass(frozen=True)
class Mixture:
    means: torch.Tensor
    weights: torch.Tensor
    spread: float

    def denoised(self, x: torch.Tensor, sigma: float) -> torch.Tensor:
        keep: float = 1.0 - sigma
        variance: float = keep**2 * self.spread**2 + sigma**2
        offsets: torch.Tensor = x[None, :] - keep * self.means
        logits: torch.Tensor = torch.log(self.weights) - 0.5 * (offsets**2).sum(-1) / variance
        responsibility: torch.Tensor = torch.softmax(logits, dim=0)
        posterior: torch.Tensor = self.means + keep * self.spread**2 / variance * offsets
        return (responsibility[:, None] * posterior).sum(0)

    def velocity(self, x: torch.Tensor, sigma: float) -> torch.Tensor:
        return (x - self.denoised(x, sigma)) / max(sigma, SIGMA_FLOOR)


def make_mixture(seed: int, dimension: int = DIMENSION) -> Mixture:
    generator: torch.Generator = torch.Generator().manual_seed(seed)
    direction: torch.Tensor = torch.randn(dimension, generator=generator, dtype=torch.float64)
    direction = direction / direction.norm()
    means: torch.Tensor = torch.stack([3.0 * direction, -3.0 * direction])
    return Mixture(means=means, weights=torch.tensor([0.5, 0.5], dtype=torch.float64), spread=0.5)


ErrorModel = Callable[[torch.Tensor, float, torch.Tensor, torch.Generator], torch.Tensor]


def white_error(level: float) -> ErrorModel:
    def apply(x: torch.Tensor, sigma: float, v: torch.Tensor, generator: torch.Generator) -> torch.Tensor:
        noise: torch.Tensor = torch.randn(v.shape, generator=generator, dtype=v.dtype)
        return level * v.norm() / np.sqrt(v.numel()) * noise

    return apply


def smooth_error(level: float, dimension: int, seed: int) -> ErrorModel:
    generator: torch.Generator = torch.Generator().manual_seed(seed)
    matrix: torch.Tensor = torch.randn(dimension, dimension, generator=generator, dtype=torch.float64)
    matrix = matrix / np.sqrt(dimension)

    def apply(x: torch.Tensor, sigma: float, v: torch.Tensor, _: torch.Generator) -> torch.Tensor:
        return level * (matrix @ v)

    return apply


def rounding_error(level: float, dimension: int, seed: int) -> ErrorModel:
    generator: torch.Generator = torch.Generator().manual_seed(seed)
    offsets: torch.Tensor = torch.rand(dimension, generator=generator, dtype=torch.float64)

    def apply(x: torch.Tensor, sigma: float, v: torch.Tensor, _: torch.Generator) -> torch.Tensor:
        cell: float = level * v.norm().item() / np.sqrt(v.numel()) * np.sqrt(12.0)
        shifted: torch.Tensor = v / cell + offsets
        return (torch.floor(shifted) + 0.5 - offsets) * cell - v

    return apply


def build_error(kind: str, level: float, dimension: int, seed: int) -> ErrorModel | None:
    if level == 0.0:
        return None
    if kind == "white":
        return white_error(level)
    if kind == "smooth":
        return smooth_error(level, dimension, seed)
    if kind == "rounding":
        return rounding_error(level, dimension, seed)
    raise ValueError(kind)


def perturbed_model(
    mixture: Mixture,
    error: ErrorModel | None,
    generator: torch.Generator,
) -> Callable[..., torch.Tensor]:
    def model(x: torch.Tensor, sigma: torch.Tensor, **_: Any) -> torch.Tensor:
        level: float = float(sigma.reshape(-1)[0])
        flat: torch.Tensor = x.reshape(-1)
        v: torch.Tensor = mixture.velocity(flat, level)
        if error is not None:
            v = v + error(flat, level, v, generator)
        return (flat - level * v).reshape(x.shape)

    return model


def integrate(
    mixture: Mixture,
    start: torch.Tensor,
    steps: int,
    error: ErrorModel | None,
    spec: Any,
    dynamic: bool,
    generator: torch.Generator,
    grid: Any = None,
) -> torch.Tensor:
    model = perturbed_model(mixture, error, generator)
    return samplers.sample_history(
        model,
        start.clone().reshape(1, -1),
        shifted_sigmas(steps),
        spec=spec,
        dynamic=dynamic,
        grid=history_filter.DEFAULT_GRID if grid is None else grid,
        disable=True,
    ).reshape(-1)


def method_table() -> dict[str, tuple[Any, bool, Any]]:
    hf = history_filter
    return {
        "euler": (hf.euler_spec(), False, None),
        "ab2": (hf.adams_bashforth_spec(2), False, None),
        "ab3": (hf.adams_bashforth_spec(3), False, None),
        "ab4": (hf.adams_bashforth_spec(4), False, None),
        "wls5": (hf.wls_spec(5), False, None),
        "wls8": (hf.wls_spec(8), False, None),
        "wls8_g95": (hf.wls_spec(8, 0.95), False, None),
        "wls8_d1": (hf.wls_spec(8, 0.85, 1), False, None),
        "dyn_d2": (hf.wls_spec(3), True, hf.QUADRATIC_GRID),
        "dynamic": (hf.wls_spec(3), True, hf.DEFAULT_GRID),
    }


def reference_solutions(trials: int) -> list[tuple[Mixture, torch.Tensor, torch.Tensor]]:
    solutions: list[tuple[Mixture, torch.Tensor, torch.Tensor]] = []
    for trial in range(trials):
        mixture = make_mixture(trial)
        generator = torch.Generator().manual_seed(1000 + trial)
        start = torch.randn(DIMENSION, generator=generator, dtype=torch.float64)
        reference = integrate(
            mixture, start, REFERENCE_STEPS, None, history_filter.adams_bashforth_spec(4), False, generator
        )
        solutions.append((mixture, start, reference))
    return solutions


def run(kind: str, levels: list[float], budgets: list[int], trials: int) -> dict[str, Any]:
    methods = method_table()
    solutions = reference_solutions(trials)
    summary: dict[str, Any] = {}
    for level in levels:
        for steps in budgets:
            errors: dict[str, list[float]] = {name: [] for name in methods}
            for trial, (mixture, start, reference) in enumerate(solutions):
                error = build_error(kind, level, DIMENSION, 500 + trial)
                for name, (spec, dynamic, grid) in methods.items():
                    noise_generator = torch.Generator().manual_seed(2000 + trial)
                    final = integrate(mixture, start, steps, error, spec, dynamic, noise_generator, grid)
                    errors[name].append(float((final - reference).norm() / reference.norm()))
            summary[f"{kind}|{level}|{steps}"] = {
                name: [float(np.mean(values)), float(np.std(values) / np.sqrt(len(values)))]
                for name, values in errors.items()
            }
    return summary


def format_table(summary: dict[str, Any], kind: str, levels: list[float], budgets: list[int]) -> str:
    names = list(next(iter(summary.values())))
    lines: list[str] = []
    for steps in budgets:
        lines.append(f"\n{kind} error, NFE={steps}: relative final error (mean over trials)")
        lines.append("level | " + " | ".join(f"{name:>8}" for name in names))
        for level in levels:
            row = summary[f"{kind}|{level}|{steps}"]
            lines.append(f"{level:5.2f} | " + " | ".join(f"{row[name][0]:8.4f}" for name in names))
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kinds", nargs="+", default=["white", "smooth", "rounding"])
    parser.add_argument("--levels", nargs="+", type=float, default=[0.0, 0.02, 0.05, 0.1, 0.2])
    parser.add_argument("--budgets", nargs="+", type=int, default=[10, 20])
    parser.add_argument("--trials", type=int, default=24)
    arguments = parser.parse_args()
    RESULTS.mkdir(exist_ok=True)
    combined: dict[str, Any] = {}
    for kind in arguments.kinds:
        summary = run(kind, arguments.levels, arguments.budgets, arguments.trials)
        combined.update(summary)
        print(format_table(summary, kind, arguments.levels, arguments.budgets), flush=True)
    (RESULTS / "synthetic.json").write_text(json.dumps(combined, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
