import argparse
import collections
import json
from typing import Any

import numpy as np

from _bootstrap import module

harness = module("harness")
run_diagnostics = module("run_diagnostics")

RESULTS = harness.ROOT / "results"
RULES: list[str] = list(run_diagnostics.RULES)
RESPONSE_METHODS: list[str] = ["euler", "ab2", "ab3", "ab4", "wls5", "wls8"]


def group(results: dict[str, Any], kind: str) -> dict[tuple, list[Any]]:
    grouped: dict[tuple, list[Any]] = collections.defaultdict(list)
    for key, value in results.items():
        parts = key.split("|")
        if parts[0] != kind:
            continue
        if kind == "trajectory":
            _, mode, cfg, _, _, steps = parts
            grouped[(mode, float(cfg), int(steps))].append(value)
        else:
            _, mode, cfg, _, _ = parts
            grouped[(mode, float(cfg))].append(value)
    return grouped


def mean_stat(rows: list[Any], component: str, name: str) -> float:
    return float(np.mean([row["components"][component][name] for row in rows]))


def mean_field(rows: list[Any], getter) -> float:
    return float(np.mean([getter(row) for row in rows]))


def trajectory_report(results: dict[str, Any]) -> list[str]:
    grouped = group(results, "trajectory")
    if not grouped:
        return []
    lines = ["### Velocity along the Euler trajectory (mean over units)\n"]
    lines.append("| mode | cfg | steps | units | cos(v_n, v_n+1) | rel. change | 2nd-diff ratio | spatial HF | guidance share |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for key in sorted(grouped):
        rows = grouped[key]
        share = [row["guidance_share"] for row in rows if "guidance_share" in row]
        share_text = f"{np.mean(share):.3f}" if share else "n/a"
        lines.append(
            f"| {key[0]} | {key[1]:g} | {key[2]} | {len(rows)} | {mean_stat(rows, 'guided', 'cosine_consecutive'):.4f} "
            f"| {mean_stat(rows, 'guided', 'relative_change'):.4f} | {mean_stat(rows, 'guided', 'second_difference'):.4f} "
            f"| {mean_stat(rows, 'guided', 'spatial_high'):.3f} | {share_text} |"
        )

    lines.append("\n### Roughness of the components (2nd-difference ratio; relative change between consecutive steps)\n")
    lines.append("| mode | cfg | steps | cond 2nd | uncond 2nd | guidance 2nd | cond change | uncond change | guidance change | units with guidance rougher than cond |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for key in sorted(grouped):
        rows = [row for row in grouped[key] if "guidance" in row["components"]]
        if not rows:
            continue
        rougher = sum(
            row["components"]["guidance"]["second_difference"] > row["components"]["cond"]["second_difference"]
            for row in rows
        )
        values = [
            mean_stat(rows, component, name)
            for name in ("second_difference", "relative_change")
            for component in ("cond", "uncond", "guidance")
        ]
        lines.append(f"| {key[0]} | {key[1]:g} | {key[2]} | " + " | ".join(f"{value:.4f}" for value in values) + f" | {rougher}/{len(rows)} |")

    lines.append("\n### One-step local consistency error (median over steps and units; lower is better)\n")
    lines.append("| mode | cfg | steps | " + " | ".join(RULES) + " | share of steps ab3 < euler | share wls5 < euler | share wls8 < euler |")
    lines.append("| --- | --- | --- |" + " --- |" * (len(RULES) + 3))
    for key in sorted(grouped):
        rows = grouped[key]
        medians = [float(np.median(np.concatenate([row["consistency"][rule] for row in rows]))) for rule in RULES]
        euler = np.concatenate([row["consistency"]["euler"] for row in rows])
        shares = [float(np.mean(np.concatenate([row["consistency"][rule] for row in rows]) < euler)) for rule in ("ab3", "wls5", "wls8")]
        lines.append(
            f"| {key[0]} | {key[1]:g} | {key[2]} | " + " | ".join(f"{value:.4f}" for value in medians) + " | "
            + " | ".join(f"{value:.2f}" for value in shares) + " |"
        )

    lines.append("\n### Local consistency of ab3 and euler on the separate components (median)\n")
    lines.append("| mode | cfg | steps | cond ab3 | cond euler | uncond ab3 | uncond euler | guidance ab3 | guidance euler |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for key in sorted(grouped):
        rows = [row for row in grouped[key] if row["component_consistency"]]
        if not rows:
            continue
        cells = []
        for component in ("cond", "uncond", "guidance"):
            for rule in ("ab3", "euler"):
                cells.append(f"{np.median(np.concatenate([row['component_consistency'][component][rule] for row in rows])):.4f}")
        lines.append(f"| {key[0]} | {key[1]:g} | {key[2]} | " + " | ".join(cells) + " |")
    return lines


def structure_report(results: dict[str, Any]) -> list[str]:
    grouped = group(results, "structure")
    if not grouped:
        return []
    lines = ["\n### Structure of the real INT8 error e = v_Q - v_D (mean over units)\n"]
    header = "| mode | cfg | units | rel. size | lag-1 cos | lag-2 cos | 2nd-diff | spatial HF err/sig | " + " | ".join(f"{m} real/white" for m in RESPONSE_METHODS) + " |"
    lines.append(header)
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |" + " --- |" * len(RESPONSE_METHODS))
    sizes: dict[float, float] = {}
    for key in sorted(grouped):
        rows = grouped[key]
        sizes[key[1]] = mean_field(rows, lambda row: row["relative_size_mean"])
        responses = [
            f"{mean_field(rows, lambda row: row['response'][method]['realised']):.2f}"
            f"/{mean_field(rows, lambda row: row['response'][method]['white']):.2f}"
            for method in RESPONSE_METHODS
        ]
        lines.append(
            f"| {key[0]} | {key[1]:g} | {len(rows)} | {sizes[key[1]]:.4f} "
            f"| {mean_field(rows, lambda row: row['cosine_lag1']):.3f} "
            f"| {mean_field(rows, lambda row: row['cosine_lag2']):.3f} "
            f"| {mean_field(rows, lambda row: row['second_difference_ratio']):.3f} "
            f"| {mean_field(rows, lambda row: row['spatial_high_error']):.3f}"
            f"/{mean_field(rows, lambda row: row['spatial_high_signal']):.3f} | " + " | ".join(responses) + " |"
        )
    if 1.0 in sizes and 4.0 in sizes:
        lines.append(f"\nSize ratio cfg 4 / cfg 1 (H13): {sizes[4.0] / sizes[1.0]:.2f}")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    arguments = parser.parse_args()
    results = json.loads((RESULTS / f"{arguments.name}.json").read_text())
    text = "\n".join(trajectory_report(results) + structure_report(results))
    (RESULTS / f"{arguments.name}.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
