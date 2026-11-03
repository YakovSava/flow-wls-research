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
OBJECTIVES: tuple[str, ...] = ("step", "accumulated")
RULE_NAMES: list[str] = list(run_diagnostics.RULES)


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


def oracle_increment(unit: dict[str, Any], index: int) -> np.ndarray:
    sigmas, velocity = unit["sigmas"], unit["v"]
    return (sigmas[index + 1] - sigmas[index]) * 0.5 * (velocity[index] + velocity[index + 1])


def rule_increment(unit: dict[str, Any], index: int, spec: Any) -> np.ndarray:
    weights = history_filter.step_weights(unit["sigmas"], index, spec)
    return sum(float(weight) * unit["v"][index - lag] for lag, weight in enumerate(weights))


def fitted_increment(unit: dict[str, Any], index: int, coefficients: np.ndarray) -> np.ndarray:
    sigmas, velocity = unit["sigmas"], unit["v"]
    combination = velocity[index].copy()
    for lag, value in enumerate(coefficients, start=1):
        combination = combination + value * (velocity[index - lag] - velocity[index])
    return (sigmas[index + 1] - sigmas[index]) * combination


def step_error(unit: dict[str, Any], steps: int, increment_of) -> float:
    errors = []
    for index in step_indices(steps):
        oracle = oracle_increment(unit, index)
        errors.append(np.linalg.norm(increment_of(index) - oracle) / np.linalg.norm(oracle))
    return float(np.sqrt(np.mean(np.square(errors))))


def accumulated_error(unit: dict[str, Any], steps: int, increment_of) -> float:
    difference = sum(increment_of(index) - oracle_increment(unit, index) for index in step_indices(steps))
    total = sum(oracle_increment(unit, index) for index in step_indices(steps))
    return float(np.linalg.norm(difference) / np.linalg.norm(total))


def normal_equations(unit: dict[str, Any], steps: int, objective: str) -> tuple[np.ndarray, np.ndarray]:
    velocity, sigmas = unit["v"], unit["sigmas"]
    size = max(ORDERS) - 1
    gram = np.zeros((size, size))
    target_dot = np.zeros(size)
    accumulated_features = np.zeros((size, velocity.shape[1]))
    accumulated_target = np.zeros(velocity.shape[1])
    for index in step_indices(steps):
        step = sigmas[index + 1] - sigmas[index]
        features = np.stack([step * (velocity[index - lag] - velocity[index]) for lag in range(1, size + 1)])
        target = step * 0.5 * (velocity[index + 1] - velocity[index])
        if objective == "step":
            scale = np.linalg.norm(oracle_increment(unit, index))
            features, target = features / scale, target / scale
            gram += features @ features.T
            target_dot += features @ target
        else:
            accumulated_features += features
            accumulated_target += target
    if objective == "accumulated":
        gram = accumulated_features @ accumulated_features.T
        target_dot = accumulated_features @ accumulated_target
    return gram, target_dot


def analyse(units: list[dict[str, Any]], steps: int) -> dict[str, Any]:
    result: dict[str, Any] = {"units": len(units)}
    metric = {"step": step_error, "accumulated": accumulated_error}
    for objective in OBJECTIVES:
        block: dict[str, Any] = {"rules": {}, "fitted": {}}
        for name, spec in run_diagnostics.RULES.items():
            values = [metric[objective](unit, steps, lambda i, u=unit, s=spec: rule_increment(u, i, s)) for unit in units]
            block["rules"][name] = values
        system = [normal_equations(unit, steps, objective) for unit in units]
        for order in ORDERS:
            held_out, coefficients = [], []
            for left_out, unit in enumerate(units):
                train = [item for position, item in enumerate(system) if position != left_out]
                gram = sum(item[0][: order - 1, : order - 1] for item in train)
                target = sum(item[1][: order - 1] for item in train)
                solution = np.linalg.solve(gram + RIDGE * np.trace(gram) * np.eye(order - 1), target)
                coefficients.append(solution)
                held_out.append(metric[objective](unit, steps, lambda i, u=unit, c=solution: fitted_increment(u, i, c)))
            block["fitted"][str(order)] = {"errors": held_out, "coefficients": np.mean(coefficients, axis=0).tolist()}
        result[objective] = block
    return result


def rank_agreement(summary: dict[str, Any], end_to_end: dict[str, Any]) -> dict[str, float]:
    agreement: dict[str, float] = {}
    for key, value in summary.items():
        cfg, steps = key.split("|")
        cell = "bf16" if float(cfg) == 5.0 else f"anima-bf16-c{float(cfg):g}"
        proxy = [float(np.mean(value["accumulated"]["rules"][name])) for name in RULE_NAMES if name in ("euler", "ab2", "ab3", "ab4", "wls5", "wls8")]
        actual = [float(np.mean(end_to_end["total"][f"{cell}|{name}|{steps}"])) for name in RULE_NAMES if name in ("euler", "ab2", "ab3", "ab4", "wls5", "wls8")]
        ranks_proxy, ranks_actual = np.argsort(np.argsort(proxy)), np.argsort(np.argsort(actual))
        agreement[key] = float(np.corrcoef(ranks_proxy, ranks_actual)[0, 1])
    return agreement


def format_report(summary: dict[str, Any], agreement: dict[str, float]) -> str:
    lines: list[str] = []
    titles = {
        "step": "Held-out relative one-step consistency error (RMS over steps; fit minimises the same quantity)",
        "accumulated": "Held-out accumulated consistency error (norm of the summed local errors over the trajectory)",
    }
    for objective in OBJECTIVES:
        lines.append(f"\n### {titles[objective]}\n")
        header = "| cfg | steps | units | " + " | ".join(RULE_NAMES) + " | " + " | ".join(f"fit K={k}" for k in ORDERS)
        lines.append(header + " | best fit vs best rule | weights on v_n-1, v_n-2, v_n-3 (K=4) |")
        lines.append("| --- | --- | --- |" + " --- |" * (len(RULE_NAMES) + len(ORDERS) + 2))
        for key, value in summary.items():
            cfg, steps = key.split("|")
            block = value[objective]
            rules = {name: float(np.mean(block["rules"][name])) for name in RULE_NAMES}
            fits = {k: float(np.mean(block["fitted"][str(k)]["errors"])) for k in ORDERS}
            best_rule = min(rules.values())
            weights = ", ".join(f"{w:+.3f}" for w in block["fitted"]["4"]["coefficients"])
            lines.append(
                f"| {cfg} | {steps} | {value['units']} | " + " | ".join(f"{rules[n]:.4f}" for n in RULE_NAMES) + " | "
                + " | ".join(f"{fits[k]:.4f}" for k in ORDERS) + f" | {min(fits.values()) / best_rule - 1:+.1%} | {weights} |"
            )
    lines.append("\n### Agreement of the accumulated metric with the end-to-end ranking of E4 (Spearman rho over the six rules)\n")
    lines.append("| cfg | steps | rho |")
    lines.append("| --- | --- | --- |")
    for key, value in agreement.items():
        cfg, steps = key.split("|")
        lines.append(f"| {cfg} | {steps} | {value:+.2f} |")
    lines.append(f"\nmean rho: {np.mean(list(agreement.values())):+.2f}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cfgs", nargs="+", type=float, default=[1.0, 3.0, 5.0])
    parser.add_argument("--steps", nargs="+", type=int, default=[8, 12, 16, 24])
    parser.add_argument("--prompts", nargs="+", default=list(harness.PROMPTS))
    parser.add_argument("--seeds", nargs="+", type=int, default=[42, 1337])
    parser.add_argument("--end-to-end", default="e4_anima")
    parser.add_argument("--name", default="e6_filter")
    arguments = parser.parse_args()
    summary: dict[str, Any] = {}
    for cfg in arguments.cfgs:
        for steps in arguments.steps:
            units = load_units(cfg, steps, arguments.prompts, arguments.seeds)
            if len(units) > 1:
                summary[f"{cfg:g}|{steps}"] = analyse(units, steps)
                print(f"cfg {cfg:g} steps {steps} analysed on {len(units)} units", flush=True)
    end_to_end = json.loads((RESULTS / f"{arguments.end_to_end}.json").read_text())
    agreement = rank_agreement(summary, end_to_end)
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / f"{arguments.name}.json").write_text(json.dumps({"summary": summary, "agreement": agreement}), encoding="utf-8")
    text = format_report(summary, agreement)
    (RESULTS / f"{arguments.name}.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
