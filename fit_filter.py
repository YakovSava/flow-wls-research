import argparse
import json
from typing import Any

import numpy as np

from _bootstrap import module

harness = module("harness")
history_filter = module("history_filter")
run_diagnostics = module("run_diagnostics")
run_velocities = module("run_velocities")

RESULTS = harness.ROOT / "results"
ORDERS: list[int] = [2, 3, 4]
FIRST_STEP: int = 3
RIDGE: float = 1e-9


def load_units(cfg: float, steps: int, prompts, seeds) -> list[dict[str, Any]]:
    units = []
    for seed in seeds:
        for prompt in prompts:
            path = run_velocities.path_for(cfg, steps, prompt, seed)
            if path.exists():
                data = np.load(path)
                units.append({"v": data["guided"].astype(np.float64), "sigmas": [float(s) for s in data["sigmas"]]})
    return units


def step_indices(steps: int) -> range:
    return range(FIRST_STEP, steps - 1)


def normal_equations(unit: dict[str, Any], order: int, steps: int) -> tuple[np.ndarray, np.ndarray]:
    velocity = unit["v"]
    gram = np.zeros((order - 1, order - 1))
    target_dot = np.zeros(order - 1)
    for index in step_indices(steps):
        features = np.stack([velocity[index - lag] - velocity[index] for lag in range(1, order)])
        target = 0.5 * (velocity[index + 1] - velocity[index])
        gram += features @ features.T
        target_dot += features @ target
    return gram, target_dot


def relative_error(unit: dict[str, Any], steps: int, increment_of) -> list[float]:
    velocity, sigmas = unit["v"], unit["sigmas"]
    errors = []
    for index in step_indices(steps):
        oracle = 0.5 * (velocity[index] + velocity[index + 1])
        errors.append(float(np.linalg.norm(increment_of(index) - oracle) / np.linalg.norm(oracle)))
    return errors


def rule_increment(unit: dict[str, Any], spec: Any):
    velocity, sigmas = unit["v"], unit["sigmas"]

    def increment(index: int) -> np.ndarray:
        weights = history_filter.step_weights(sigmas, index, spec) / (sigmas[index + 1] - sigmas[index])
        return sum(float(weight) * velocity[index - lag] for lag, weight in enumerate(weights))

    return increment


def fitted_increment(unit: dict[str, Any], coefficients: np.ndarray):
    velocity = unit["v"]

    def increment(index: int) -> np.ndarray:
        result = velocity[index].copy()
        for lag, value in enumerate(coefficients, start=1):
            result = result + value * (velocity[index - lag] - velocity[index])
        return result

    return increment


def analyse(units: list[dict[str, Any]], steps: int) -> dict[str, Any]:
    result: dict[str, Any] = {"units": len(units), "rules": {}, "fitted": {}}
    rules = {name: spec for name, spec in run_diagnostics.RULES.items()}
    for name, spec in rules.items():
        errors = [np.median(relative_error(unit, steps, rule_increment(unit, spec))) for unit in units]
        result["rules"][name] = float(np.mean(errors))
    system = [normal_equations(unit, 4, steps) for unit in units]
    for order in ORDERS:
        held_out = []
        coefficients = []
        for left_out, unit in enumerate(units):
            train = [item for position, item in enumerate(system) if position != left_out]
            gram = sum(item[0][: order - 1, : order - 1] for item in train)
            target = sum(item[1][: order - 1] for item in train)
            solution = np.linalg.solve(gram + RIDGE * np.trace(gram) * np.eye(order - 1), target)
            coefficients.append(solution)
            held_out.append(np.median(relative_error(unit, steps, fitted_increment(unit, solution))))
        result["fitted"][str(order)] = {"error": float(np.mean(held_out)), "coefficients": np.mean(coefficients, axis=0).tolist()}
    return result


def format_report(summary: dict[str, Any]) -> str:
    lines = ["### Held-out one-step consistency error of fitted linear history filters (leave-one-unit-out)\n"]
    names = list(run_diagnostics.RULES)
    lines.append("| cfg | steps | units | " + " | ".join(names) + " | " + " | ".join(f"fit K={k}" for k in ORDERS) + " | best fit vs euler | fitted weights on v_n-1, v_n-2, v_n-3 (K=4) |")
    lines.append("| --- | --- | --- |" + " --- |" * (len(names) + len(ORDERS) + 2))
    for key, value in summary.items():
        cfg, steps = key.split("|")
        euler = value["rules"]["euler"]
        best = min(value["fitted"][str(k)]["error"] for k in ORDERS)
        weights = ", ".join(f"{w:+.3f}" for w in value["fitted"]["4"]["coefficients"])
        lines.append(
            f"| {cfg} | {steps} | {value['units']} | " + " | ".join(f"{value['rules'][n]:.4f}" for n in names) + " | "
            + " | ".join(f"{value['fitted'][str(k)]['error']:.4f}" for k in ORDERS) + f" | {best / euler - 1:+.1%} | {weights} |"
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cfgs", nargs="+", type=float, default=[1.0, 3.0, 5.0])
    parser.add_argument("--steps", nargs="+", type=int, default=[8, 12, 16, 24])
    parser.add_argument("--prompts", nargs="+", default=list(harness.PROMPTS))
    parser.add_argument("--seeds", nargs="+", type=int, default=[42, 1337])
    parser.add_argument("--name", default="e6_filter")
    arguments = parser.parse_args()
    summary: dict[str, Any] = {}
    for cfg in arguments.cfgs:
        for steps in arguments.steps:
            units = load_units(cfg, steps, arguments.prompts, arguments.seeds)
            if len(units) > 1:
                summary[f"{cfg:g}|{steps}"] = analyse(units, steps)
                print(f"cfg {cfg:g} steps {steps} analysed on {len(units)} units", flush=True)
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / f"{arguments.name}.json").write_text(json.dumps(summary), encoding="utf-8")
    text = format_report(summary)
    (RESULTS / f"{arguments.name}.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
