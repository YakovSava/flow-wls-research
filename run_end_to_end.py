import argparse
import collections
import functools
import json
import pathlib
from typing import Any

import numpy as np

from _bootstrap import module

harness = module("harness")
samplers = module("samplers")
history_filter = module("history_filter")
fakequant = module("fakequant")
metrics = module("metrics")

RESULTS: pathlib.Path = harness.ROOT / "results"
SEEDS: list[int] = [42, 1337, 7]
BUDGETS: list[int] = [10, 16]
REFERENCE_METHOD: str = "wls5"
REFERENCE_STEPS: int = 96
BASELINE_SPEC: str = "bf16"
STATIC_METHODS: list[str] = ["ab3", "ab4", "wls5", "wls8"]
METHODS: dict[str, tuple[Any, bool]] = {
    "euler": (history_filter.euler_spec(), False),
    "ab3": (history_filter.adams_bashforth_spec(3), False),
    "ab4": (history_filter.adams_bashforth_spec(4), False),
    "wls5": (history_filter.wls_spec(5), False),
    "wls8": (history_filter.wls_spec(8), False),
    "dynamic": (history_filter.wls_spec(3), True),
}


def tag(spec: str, prompt: str, seed: int, method: str, steps: int) -> str:
    return f"{spec}__{prompt}_s{seed}__{method}_n{steps:03d}"


def selection_path(name: str) -> pathlib.Path:
    return harness.DUMPS / "selections" / f"{name}.json"


def run_one(rig: Any, spec: str, prompt: str, seed: int, method: str, steps: int) -> np.ndarray:
    name = tag(spec, prompt, seed, method, steps)
    filter_spec, dynamic = METHODS[method]
    chosen: list[list[float]] = []

    def observer(index: int, picked: Any) -> None:
        chosen.append([picked.length, picked.gamma, picked.degree])

    sampler = functools.partial(
        samplers.sample_history,
        spec=filter_spec,
        dynamic=dynamic,
        observer=observer if dynamic else None,
        disable=True,
    )

    def produce() -> np.ndarray:
        return rig.sample(prompt, seed, steps, sampler)

    value = harness.cached(name, produce)
    if dynamic and chosen:
        path = selection_path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(chosen), encoding="utf-8")
    return value


def reference_tag(spec: str, prompt: str, seed: int) -> str:
    return tag(spec, prompt, seed, REFERENCE_METHOD, REFERENCE_STEPS)


def needed_tags(spec: str, prompt: str, seed: int, methods: list[str], budgets: list[int]) -> list[str]:
    names = [reference_tag(spec, prompt, seed)]
    names += [tag(spec, prompt, seed, method, steps) for method in methods for steps in budgets]
    return names


def execute(units: list[tuple[str, int]], specs: list[str], methods: list[str], budgets: list[int]) -> None:
    rig = harness.Rig()
    for position, (prompt, seed) in enumerate(units, start=1):
        for spec in specs:
            names = needed_tags(spec, prompt, seed, methods, budgets)
            if all(harness.latent_path(name).exists() for name in names):
                continue
            rig.use(spec)
            run_one(rig, spec, prompt, seed, REFERENCE_METHOD, REFERENCE_STEPS)
            for method in methods:
                for steps in budgets:
                    run_one(rig, spec, prompt, seed, method, steps)
            print(f"unit {position}/{len(units)} {prompt} s{seed} {spec} done", flush=True)
    rig.weights.release()


def load(name: str) -> np.ndarray | None:
    path = harness.latent_path(name)
    return np.load(path) if path.exists() else None


def collect(
    units: list[tuple[str, int]],
    specs: list[str],
    methods: list[str],
    budgets: list[int],
) -> dict[str, Any]:
    complete = []
    for prompt, seed in units:
        names = [n for spec in specs for n in needed_tags(spec, prompt, seed, methods, budgets)]
        if all(harness.latent_path(n).exists() for n in names):
            complete.append((prompt, seed))
    table: dict[str, Any] = {"units": complete, "floor": {}, "total": {}, "solver": {}, "geometry": {}, "detail": {}}
    for spec in specs:
        table["floor"][spec] = []
        for prompt, seed in complete:
            truth = load(reference_tag(BASELINE_SPEC, prompt, seed))
            own = load(reference_tag(spec, prompt, seed))
            table["floor"][spec].append(metrics.total_error(own, truth))
            for method in methods:
                for steps in budgets:
                    latent = load(tag(spec, prompt, seed, method, steps))
                    key = f"{spec}|{method}|{steps}"
                    for field, function, anchor in (
                        ("total", metrics.total_error, truth),
                        ("solver", metrics.total_error, own),
                        ("geometry", metrics.geometry_error, truth),
                        ("detail", metrics.detail_error, truth),
                    ):
                        table[field].setdefault(key, []).append(function(latent, anchor))
    return table


def interval(first: list[float], second: list[float]) -> str:
    point, low, high = metrics.paired_difference(first, second)
    flag = "*" if (low > 0 or high < 0) else " "
    return f"{point:+.4f} [{low:+.4f}, {high:+.4f}]{flag}"


def format_report(table: dict[str, Any], specs: list[str], methods: list[str], budgets: list[int]) -> str:
    lines: list[str] = []
    count = len(table["units"])
    lines.append(f"units (prompt, seed): {count}\n")
    lines.append("### Quantization floor (converged quantized model vs converged bf16), relative error\n")
    lines.append("| spec | floor mean | se |")
    lines.append("| --- | --- | --- |")
    for spec in specs:
        mean, error = metrics_mean_error(table["floor"][spec])
        lines.append(f"| {spec} | {mean:.4f} | {error:.4f} |")
    for field, title in (
        ("total", "Total error vs converged bf16 (relative RMS of the final latent)"),
        ("solver", "Solver error vs the same model's own converged solution"),
        ("geometry", "Geometry (8x8 low-pass) error vs converged bf16"),
        ("detail", "Detail (high-pass) error vs converged bf16"),
    ):
        for steps in budgets:
            lines.append(f"\n### {title}, {steps} steps\n")
            lines.append("| method | " + " | ".join(specs) + " |")
            lines.append("| --- |" + " --- |" * len(specs))
            for method in methods:
                cells = []
                for spec in specs:
                    mean, _ = metrics_mean_error(table[field][f"{spec}|{method}|{steps}"])
                    cells.append(f"{mean:.4f}")
                lines.append(f"| {method} | " + " | ".join(cells) + " |")

    lines.append("\n### Paired contrasts on total error (negative = first is better; * = 95% interval excludes 0)\n")
    for steps in budgets:
        lines.append(f"\n**{steps} steps**\n")
        lines.append("| spec | wls8 - ab4 | wls8 - euler | ab4 - euler | dynamic - best static | best static |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for spec in specs:
            def series(method: str) -> list[float]:
                return table["total"][f"{spec}|{method}|{steps}"]

            best = min(STATIC_METHODS, key=lambda m: float(np.mean(series(m))))
            lines.append(
                f"| {spec} | {interval(series('wls8'), series('ab4'))} | {interval(series('wls8'), series('euler'))} "
                f"| {interval(series('ab4'), series('euler'))} | {interval(series('dynamic'), series(best))} | {best} |"
            )

    lines.append("\n### Extra error caused by quantization: (error with format) - (error in bf16), same sampler\n")
    for steps in budgets:
        lines.append(f"\n**{steps} steps**\n")
        lines.append("| spec | euler | ab4 | wls8 | dynamic | ab4 - wls8 |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for spec in specs:
            if spec == BASELINE_SPEC:
                continue

            def extra(method: str) -> list[float]:
                quant = np.array(table["total"][f"{spec}|{method}|{steps}"])
                base = np.array(table["total"][f"{BASELINE_SPEC}|{method}|{steps}"])
                return list(quant - base)

            cells = [f"{np.mean(extra(m)):+.4f}" for m in ("euler", "ab4", "wls8", "dynamic")]
            lines.append(f"| {spec} | " + " | ".join(cells) + f" | {interval(extra('ab4'), extra('wls8'))} |")

    lines.append("\n### Floor versus 16-step discretization error (best static)\n")
    lines.append("| spec | floor | solver error of best static at 16 steps | ratio |")
    lines.append("| --- | --- | --- | --- |")
    steps = 16 if 16 in budgets else budgets[-1]
    for spec in specs:
        solver = min(float(np.mean(table["solver"][f"{spec}|{m}|{steps}"])) for m in STATIC_METHODS)
        floor = float(np.mean(table["floor"][spec]))
        lines.append(f"| {spec} | {floor:.4f} | {solver:.4f} | {floor / solver:.2f} |")
    return "\n".join(lines)


def metrics_mean_error(values: list[float]) -> tuple[float, float]:
    array = np.asarray(values, dtype=np.float64)
    error = float(array.std(ddof=1) / np.sqrt(len(array))) if len(array) > 1 else 0.0
    return float(array.mean()), error


def selection_summary(specs: list[str], units: list[tuple[str, int]], budgets: list[int]) -> str:
    lines = ["\n### What the dynamic rule chose (share of steps)\n", "| spec | steps | length | degree | gamma |", "| --- | --- | --- | --- | --- |"]
    for spec in specs:
        for steps in budgets:
            lengths, degrees, gammas = collections.Counter(), collections.Counter(), collections.Counter()
            for prompt, seed in units:
                path = selection_path(tag(spec, prompt, seed, "dynamic", steps))
                if not path.exists():
                    continue
                for length, gamma, degree in json.loads(path.read_text(encoding="utf-8")):
                    lengths[int(length)] += 1
                    degrees[int(degree)] += 1
                    gammas[gamma] += 1
            total = sum(lengths.values())
            if not total:
                continue

            def share(counter: collections.Counter) -> str:
                return ", ".join(f"{k}:{v / total:.0%}" for k, v in sorted(counter.items()))

            lines.append(f"| {spec} | {steps} | {share(lengths)} | {share(degrees)} | {share(gammas)} |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompts", nargs="+", default=list(harness.PROMPTS))
    parser.add_argument("--seeds", nargs="+", type=int, default=SEEDS)
    parser.add_argument("--specs", nargs="+", default=list(fakequant.SPECS))
    parser.add_argument("--methods", nargs="+", default=list(METHODS))
    parser.add_argument("--budgets", nargs="+", type=int, default=BUDGETS)
    parser.add_argument("--report-only", action="store_true")
    arguments = parser.parse_args()
    units = [(prompt, seed) for seed in arguments.seeds for prompt in arguments.prompts]
    if not arguments.report_only:
        execute(units, arguments.specs, arguments.methods, arguments.budgets)
    table = collect(units, arguments.specs, arguments.methods, arguments.budgets)
    RESULTS.mkdir(exist_ok=True)
    text = format_report(table, arguments.specs, arguments.methods, arguments.budgets)
    text += selection_summary(arguments.specs, table["units"], arguments.budgets)
    (RESULTS / "end_to_end.md").write_text(text, encoding="utf-8")
    (RESULTS / "end_to_end.json").write_text(json.dumps(table), encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
