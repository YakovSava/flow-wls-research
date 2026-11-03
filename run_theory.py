import json
import pathlib

import numpy as np

from _bootstrap import module

history_filter = module("history_filter")

RESULTS: pathlib.Path = pathlib.Path(__file__).resolve().parent / "results"
SHIFT: float = 3.0
BUDGETS: list[int] = [8, 10, 12, 16, 20, 30]
FREQUENCIES: np.ndarray = np.array([0.0, np.pi / 4, np.pi / 2, 3 * np.pi / 4, np.pi])


def shifted_sigmas(steps: int, shift: float = SHIFT) -> list[float]:
    grid = np.linspace(1.0, 0.0, steps + 1)
    return list(shift * grid / (1.0 + (shift - 1.0) * grid))


def methods() -> dict[str, history_filter.FilterSpec]:
    hf = history_filter
    return {
        "euler": hf.euler_spec(),
        "ab2": hf.adams_bashforth_spec(2),
        "ab3 (= wls3)": hf.adams_bashforth_spec(3),
        "ab4": hf.adams_bashforth_spec(4),
        "ab5": hf.adams_bashforth_spec(5),
        "ab6": hf.adams_bashforth_spec(6),
        "wls4": hf.wls_spec(4),
        "wls5": hf.wls_spec(5),
        "wls6": hf.wls_spec(6),
        "wls8": hf.wls_spec(8),
        "wls8 g=1.0": hf.wls_spec(8, 1.0),
        "wls8 d=1": hf.wls_spec(8, 0.85, 1),
    }


def gain_table() -> tuple[str, dict[str, dict[str, float]]]:
    table: dict[str, dict[str, float]] = {}
    lines = ["| method | " + " | ".join(f"N={n}" for n in BUDGETS) + " |", "| --- |" + " --- |" * len(BUDGETS)]
    for name, spec in methods().items():
        gains = {str(n): history_filter.white_noise_gain(shifted_sigmas(n), spec) for n in BUDGETS}
        table[name] = gains
        lines.append(f"| {name} | " + " | ".join(f"{gains[str(n)]:.2f}" for n in BUDGETS) + " |")
    return "\n".join(lines), table


def response_table(steps: int = 20) -> str:
    sigmas = [float(1 - k / steps) for k in range(steps + 1)]
    index = steps - 4
    step = sigmas[index + 1] - sigmas[index]
    lines = [
        "| method | " + " | ".join(f"w={w / np.pi:.2f} pi" for w in FREQUENCIES) + " |",
        "| --- |" + " --- |" * len(FREQUENCIES),
    ]
    for name, spec in methods().items():
        weights = history_filter.step_weights(sigmas, index, spec)
        response = history_filter.frequency_response(weights, step, FREQUENCIES)
        lines.append(f"| {name} | " + " | ".join(f"{value:.2f}" for value in response) + " |")
    return "\n".join(lines)


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    gains, raw = gain_table()
    text = (
        "### White-noise accumulation gain (shift-3 schedule)\n\n"
        "Ratio of the standard deviation of the final-state error caused by independent velocity errors of equal size, "
        "to the same quantity for Euler. A constant (fully correlated) error always has gain 1.\n\n"
        + gains
        + "\n\n### Frequency response of the one-step increment (uniform grid, N=20, step 16)\n\n"
        "Gain on a velocity-error component that alternates with frequency w across steps (w = 0 is a constant bias).\n\n"
        + response_table()
        + "\n"
    )
    (RESULTS / "theory.md").write_text(text, encoding="utf-8")
    (RESULTS / "theory.json").write_text(json.dumps(raw, indent=1), encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
