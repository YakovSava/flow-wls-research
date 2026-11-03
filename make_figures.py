import json
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT: pathlib.Path = pathlib.Path(__file__).resolve().parent
RESULTS: pathlib.Path = ROOT / "results"
FIGURES: pathlib.Path = ROOT / "figures"
END_TO_END_RUNS: list[str] = ["end_to_end_10_16", "end_to_end_8_12"]
SPECS: list[str] = ["fp8_w", "fp8_wa", "int8_wa", "int4_w", "int4_wa8", "nvfp4_w"]
COLORS: dict[str, str] = {
    "euler": "#7f7f7f",
    "ab3": "#1f77b4",
    "ab4": "#d62728",
    "wls5": "#2ca02c",
    "wls8": "#006d2c",
    "dynamic": "#ff7f0e",
}


def load(name: str) -> dict:
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def structure_figure() -> None:
    data = load("error_structure.json")
    figure, axes = plt.subplots(1, 3, figsize=(15, 4.2))
    positions = np.arange(len(SPECS))

    cosines = [[v["cosine_lag1"] for k, v in data.items() if k.startswith(spec + "|")] for spec in SPECS]
    axes[0].bar(positions, [np.mean(c) for c in cosines], yerr=[np.std(c) for c in cosines], color="#4c72b0")
    axes[0].axhline(0.5, color="k", ls="--", lw=0.8)
    axes[0].set_xticks(positions, SPECS, rotation=30)
    axes[0].set_ylabel("lag-1 cosine of quantization error")
    axes[0].set_title("Temporal correlation of the velocity error")

    width = 0.2
    for offset, (method, kind) in enumerate((("ab4", "realised"), ("ab4", "white"), ("wls8", "realised"), ("wls8", "white"))):
        values = [
            np.mean([v["response"][method][kind] for k, v in data.items() if k.startswith(spec + "|")])
            for spec in SPECS
        ]
        hatch = "//" if kind == "white" else None
        axes[1].bar(positions + (offset - 1.5) * width, values, width, label=f"{method} {kind}",
                    color=COLORS[method], hatch=hatch, alpha=0.9 if kind == "realised" else 0.45)
    axes[1].axhline(1.0, color="k", lw=0.8)
    axes[1].set_xticks(positions, SPECS, rotation=30)
    axes[1].set_ylabel("accumulated error relative to Euler")
    axes[1].set_title("Realised vs white-noise prediction")
    axes[1].legend(fontsize=8)

    for spec in ("fp8_wa", "int8_wa", "int4_w", "nvfp4_w"):
        rows = [v["cosine_lag1_by_step"] for k, v in data.items() if k.startswith(spec + "|")]
        axes[2].plot(np.mean(rows, axis=0), label=spec)
    axes[2].set_xlabel("step index (0 = pure noise)")
    axes[2].set_ylabel("lag-1 cosine")
    axes[2].set_title("Correlation along the trajectory")
    axes[2].legend(fontsize=8)
    figure.tight_layout()
    figure.savefig(FIGURES / "error_structure.png", dpi=140)
    plt.close(figure)


def synthetic_figure() -> None:
    data = load("synthetic.json")
    figure, axes = plt.subplots(1, 3, figsize=(15, 4.2), sharey=True)
    levels = sorted({float(key.split("|")[1]) for key in data})
    for axis, kind in zip(axes, ("white", "smooth", "rounding")):
        for method in COLORS:
            if method not in next(iter(data.values())):
                continue
            values = [data[f"{kind}|{level}|12"][method][0] for level in levels]
            axis.plot(levels, values, marker="o", label=method, color=COLORS[method])
        axis.set_title(f"{kind} velocity error, 12 steps")
        axis.set_xlabel("relative size of the error")
    axes[0].set_ylabel("relative final error")
    axes[0].legend(fontsize=8)
    figure.tight_layout()
    figure.savefig(FIGURES / "synthetic.png", dpi=140)
    plt.close(figure)


def end_to_end_figure(name: str) -> None:
    data = load(f"{name}.json")
    budgets = sorted({int(key.split("|")[2]) for key in data["total"]})
    specs = ["bf16"] + SPECS
    specs = [s for s in specs if f"{s}|euler|{budgets[0]}" in data["total"]]
    methods = list(COLORS)
    figure, axes = plt.subplots(1, len(budgets), figsize=(7.5 * len(budgets), 4.5), sharey=True)
    axes = np.atleast_1d(axes)
    width = 0.8 / len(methods)
    positions = np.arange(len(specs))
    for axis, steps in zip(axes, budgets):
        for offset, method in enumerate(methods):
            values = [np.mean(data["total"][f"{spec}|{method}|{steps}"]) for spec in specs]
            errors = [
                np.std(data["total"][f"{spec}|{method}|{steps}"], ddof=1) / np.sqrt(len(data["units"]))
                for spec in specs
            ]
            axis.bar(positions + (offset - len(methods) / 2 + 0.5) * width, values, width, yerr=errors,
                     label=method, color=COLORS[method])
        floors = [np.mean(data["floor"][spec]) for spec in specs]
        axis.plot(positions, floors, "k_", markersize=30, markeredgewidth=2, label="quantization floor")
        axis.set_xticks(positions, specs, rotation=30)
        axis.set_title(f"{steps} steps")
        axis.set_ylim(0, min(1.2, axis.get_ylim()[1]))
    axes[0].set_ylabel("relative error vs converged bf16")
    axes[-1].legend(fontsize=8, ncol=2)
    figure.tight_layout()
    figure.savefig(FIGURES / f"{name}.png", dpi=140)
    plt.close(figure)


def main() -> None:
    FIGURES.mkdir(exist_ok=True)
    for name, function in (
        ("error_structure.json", structure_figure),
        ("synthetic.json", synthetic_figure),
    ):
        if (RESULTS / name).exists():
            function()
            print("wrote figure from", name)
    for name in END_TO_END_RUNS:
        if (RESULTS / f"{name}.json").exists():
            end_to_end_figure(name)
            print("wrote figure from", name)


if __name__ == "__main__":
    main()
