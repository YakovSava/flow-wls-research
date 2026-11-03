import collections
import dataclasses
import json
from typing import Any

import numpy as np

from _bootstrap import module

harness = module("harness")
metrics = module("metrics")
sweep = module("sweep")

STATIC_PAIR: tuple[str, str] = ("ab3", "dynamic")
SCALE_FLOOR: float = 1e-30


def load(name: str) -> np.ndarray:
    return np.load(harness.latent_path(name))


def cosine_distance(latent: np.ndarray, reference: np.ndarray) -> float:
    first, second = latent.reshape(-1).astype(np.float64), reference.reshape(-1).astype(np.float64)
    return 1.0 - float(first @ second / max(np.linalg.norm(first) * np.linalg.norm(second), SCALE_FLOOR))


def norm_ratio(latent: np.ndarray, reference: np.ndarray) -> float:
    return float(np.linalg.norm(latent) / max(np.linalg.norm(reference), SCALE_FLOOR))


FIELDS: dict[str, Any] = {
    "total": (metrics.total_error, "truth"),
    "solver": (metrics.total_error, "own"),
    "geometry": (metrics.geometry_error, "truth"),
    "detail": (metrics.detail_error, "truth"),
    "cosine": (cosine_distance, "truth"),
    "norm": (norm_ratio, "truth"),
}


def complete_units(cells, units, methods, budgets) -> list[tuple[str, int]]:
    ready = []
    for prompt, seed in units:
        names = []
        for cell in cells:
            names += sweep.needed_tags(cell, prompt, seed, methods, budgets)
            names.append(sweep.reference_tag(cell.truth, prompt, seed))
        if all(harness.latent_path(name).exists() for name in names):
            ready.append((prompt, seed))
    return ready


def collect(cells, units, methods, budgets) -> dict[str, Any]:
    ready = complete_units(cells, units, methods, budgets)
    table: dict[str, Any] = {"units": ready, "floor": {}, **{field: {} for field in FIELDS}}
    for cell in cells:
        table["floor"][cell.name] = []
        for prompt, seed in ready:
            truth = load(sweep.reference_tag(cell.truth, prompt, seed))
            own = load(sweep.reference_tag(cell, prompt, seed))
            table["floor"][cell.name].append(metrics.total_error(own, truth))
            for method in methods:
                for budget in budgets:
                    latent = load(sweep.tag(cell, prompt, seed, method, budget))
                    key = f"{cell.name}|{method}|{budget}"
                    for field, (function, anchor) in FIELDS.items():
                        target = truth if anchor == "truth" else own
                        table[field].setdefault(key, []).append(function(latent, target))
    return table


def mean_error(values: list[float]) -> tuple[float, float]:
    array = np.asarray(values, dtype=np.float64)
    error = float(array.std(ddof=1) / np.sqrt(len(array))) if len(array) > 1 else 0.0
    return float(array.mean()), error


def interval(first: list[float], second: list[float]) -> str:
    point, low, high = metrics.paired_difference(first, second)
    flag = "*" if (low > 0 or high < 0) else " "
    return f"{point:+.4f} [{low:+.4f}, {high:+.4f}]{flag}"


def significant(first: list[float], second: list[float]) -> int:
    _, low, high = metrics.paired_difference(first, second)
    if high < 0:
        return -1
    return 1 if low > 0 else 0


def observed_order(table: dict[str, Any], cell_name: str, method: str, budgets: list[int]) -> tuple[float, float]:
    errors = np.array([table["solver"][f"{cell_name}|{method}|{budget}"] for budget in budgets])
    slopes = [-np.polyfit(np.log(budgets), np.log(errors[:, unit]), 1)[0] for unit in range(errors.shape[1])]
    return mean_error(slopes)


def grid_table(table, field, cells, methods, budget) -> list[str]:
    lines = ["| method | " + " | ".join(cell.name for cell in cells) + " |", "| --- |" + " --- |" * len(cells)]
    for method in methods:
        values = [mean_error(table[field][f"{cell.name}|{method}|{budget}"])[0] for cell in cells]
        lines.append(f"| {method} | " + " | ".join(f"{value:.4f}" for value in values) + " |")
    return lines


def contrast_tables(table, cells, methods, budgets) -> list[str]:
    lines: list[str] = []
    others = [method for method in methods if method != "euler"]
    for cell in cells:
        lines.append(f"\n**{cell.name}**: method - euler, total error (negative = better than euler; * = 95% interval excludes 0)\n")
        lines.append("| method | " + " | ".join(f"{budget} steps" for budget in budgets) + " |")
        lines.append("| --- |" + " --- |" * len(budgets))
        for method in others:
            cells_text = [
                interval(table["total"][f"{cell.name}|{method}|{budget}"], table["total"][f"{cell.name}|euler|{budget}"])
                for budget in budgets
            ]
            lines.append(f"| {method} | " + " | ".join(cells_text) + " |")
    return lines


def order_table(table, cells, methods, budgets) -> list[str]:
    lines = ["| method | " + " | ".join(cell.name for cell in cells) + " |", "| --- |" + " --- |" * len(cells)]
    for method in methods:
        parts = []
        for cell in cells:
            mean, error = observed_order(table, cell.name, method, budgets)
            parts.append(f"{mean:+.2f} +- {error:.2f}")
        lines.append(f"| {method} | " + " | ".join(parts) + " |")
    return lines


def extra_error(table, quantized, reference, method: str, budget: int) -> list[float]:
    first = np.array(table["total"][f"{quantized.name}|{method}|{budget}"])
    second = np.array(table["total"][f"{reference.name}|{method}|{budget}"])
    return list(first - second)


def quantization_effect(table, cells, methods, budgets) -> list[str]:
    lines: list[str] = []
    names = {cell.name: cell for cell in cells}
    pairs = [
        (cell, dataclasses.replace(cell, mode="d"))
        for cell in cells
        if cell.mode == "q" and dataclasses.replace(cell, mode="d").name in names
    ]
    for quantized, reference in pairs:
        lines.append(f"\n**{quantized.name} against {reference.name}**: extra total error of the real INT8 path, same method\n")
        lines.append("| method | " + " | ".join(f"{budget} steps" for budget in budgets) + " |")
        lines.append("| --- |" + " --- |" * len(budgets))
        for method in methods:
            parts = []
            for budget in budgets:
                first = table["total"][f"{quantized.name}|{method}|{budget}"]
                second = table["total"][f"{reference.name}|{method}|{budget}"]
                parts.append(interval(first, second))
            lines.append(f"| {method} | " + " | ".join(parts) + " |")
        if "ab4" in methods and "wls8" in methods:
            lines.append("\nab4 extra - wls8 extra (H14):\n")
            for budget in budgets:
                ab4_extra = extra_error(table, quantized, reference, "ab4", budget)
                wls8_extra = extra_error(table, quantized, reference, "wls8", budget)
                lines.append(f"* {budget} steps: {interval(ab4_extra, wls8_extra)}")
    return lines


def replication_counts(table, cells, budgets) -> list[str]:
    cells_total = 0
    euler_not_worse = 0
    history_helps = []
    for cell in cells:
        for budget in budgets:
            euler = table["total"].get(f"{cell.name}|euler|{budget}")
            wls8 = table["total"].get(f"{cell.name}|wls8|{budget}")
            if euler is None or wls8 is None:
                continue
            cells_total += 1
            euler_not_worse += float(np.mean(euler)) <= float(np.mean(wls8))
            candidates = [m for m in STATIC_PAIR if f"{cell.name}|{m}|{budget}" in table["total"]]
            if candidates:
                best = min(candidates, key=lambda m: float(np.mean(table["total"][f"{cell.name}|{m}|{budget}"])))
                verdict = significant(table["total"][f"{cell.name}|{best}|{budget}"], euler)
                history_helps.append((cell.name, budget, best, verdict))
    lines = [f"\nH15 count: euler is not worse than wls8 in {euler_not_worse} of {cells_total} (cell, budget) pairs.\n"]
    lines.append("H7 table: best of ab3/dynamic (by mean) against euler; -1 = significantly better than euler, 0 = inconclusive, +1 = significantly worse\n")
    lines.append("| cell | budget | best | verdict |")
    lines.append("| --- | --- | --- | --- |")
    for name, budget, best, verdict in history_helps:
        lines.append(f"| {name} | {budget} | {best} | {verdict:+d} |")
    return lines


def convergence_check(cells, ready) -> list[str]:
    lines = ["\n### Reference convergence (ab3 and wls5 at the reference step count, relative difference)\n"]
    lines.append("| cell | unit | difference |")
    lines.append("| --- | --- | --- |")
    for cell in cells:
        for prompt, seed in ready[:1]:
            first = sweep.reference_tag(cell, prompt, seed)
            second = sweep.reference_tag(cell, prompt, seed, sweep.CONVERGENCE_METHOD)
            if harness.latent_path(second).exists():
                lines.append(f"| {cell.name} | {prompt} s{seed} | {metrics.total_error(load(second), load(first)):.4f} |")
    return lines


def share(counter: collections.Counter, total: int) -> str:
    return ", ".join(f"{key}:{value / total:.0%}" for key, value in sorted(counter.items()))


def selection_summary(cells, ready, budgets) -> list[str]:
    lines = ["\n### What the dynamic rule chose (share of steps)\n", "| cell | steps | length | degree | gamma |", "| --- | --- | --- | --- | --- |"]
    for cell in cells:
        for budget in budgets:
            lengths, degrees, gammas = collections.Counter(), collections.Counter(), collections.Counter()
            for prompt, seed in ready:
                path = sweep.selection_path(sweep.tag(cell, prompt, seed, "dynamic", budget))
                if not path.exists():
                    continue
                for length, gamma, degree in json.loads(path.read_text(encoding="utf-8")):
                    lengths[int(length)] += 1
                    degrees[int(degree)] += 1
                    gammas[gamma] += 1
            total = sum(lengths.values())
            if total:
                cells_text = [share(counter, total) for counter in (lengths, degrees, gammas)]
                lines.append(f"| {cell.name} | {budget} | " + " | ".join(cells_text) + " |")
    return lines


def format_report(table, cells, methods, budgets) -> str:
    lines = [f"units (prompt, seed): {len(table['units'])}\n", "### Kernel / quantization floor (converged own solution against converged truth), relative error\n"]
    lines += ["| cell | floor mean | se |", "| --- | --- | --- |"]
    for cell in cells:
        mean, error = mean_error(table["floor"][cell.name])
        lines.append(f"| {cell.name} | {mean:.4f} | {error:.4f} |")
    titles = {
        "total": "Total error against converged truth (relative RMS of the final latent)",
        "solver": "Solver error against the cell's own converged solution",
        "geometry": "Geometry (8x8 low-pass) error against converged truth",
        "detail": "Detail (high-pass) error against converged truth",
        "cosine": "Cosine distance of the final latent to converged truth",
        "norm": "Norm ratio of the final latent to converged truth (1 = same energy)",
    }
    for field, title in titles.items():
        for budget in budgets:
            lines.append(f"\n### {title}, budget {budget}\n")
            lines += grid_table(table, field, cells, methods, budget)
    lines.append("\n### Observed convergence order (slope of log solver error against log budget)\n")
    lines += order_table(table, cells, methods, budgets)
    lines.append("\n### Paired contrasts against euler\n")
    lines += contrast_tables(table, cells, methods, budgets)
    effect = quantization_effect(table, cells, methods, budgets)
    if effect:
        lines.append("\n### Effect of the real INT8 kernels (Q - D)\n")
        lines += effect
    lines += replication_counts(table, cells, budgets)
    return "\n".join(lines)
