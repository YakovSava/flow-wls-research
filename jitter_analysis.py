import argparse
import json
import math

import numpy as np

from _bootstrap import module

harness = module("harness")
run_velocities = module("run_velocities")

RESULTS = harness.ROOT / "results"
MAX_ORDER: int = 4
FIRST_STEP: int = 1


def difference_profile(velocity: np.ndarray) -> list[float]:
    body = velocity[FIRST_STEP:-1]
    energy = float(np.mean(np.sum(body**2, axis=1)))
    profile = []
    current = body
    for order in range(1, MAX_ORDER + 1):
        current = np.diff(current, axis=0)
        scale = math.comb(2 * order, order)
        profile.append(float(np.mean(np.sum(current**2, axis=1)) / scale / energy))
    return profile


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cfgs", nargs="+", type=float, default=[1.0, 3.0, 5.0])
    parser.add_argument("--steps", nargs="+", type=int, default=[8, 12, 16, 24])
    parser.add_argument("--prompts", nargs="+", default=list(harness.PROMPTS))
    parser.add_argument("--seeds", nargs="+", type=int, default=[42, 1337])
    parser.add_argument("--name", default="e6_jitter")
    arguments = parser.parse_args()
    lines = [
        "### Normalised difference energy of the guided velocity along Euler trajectories",
        "",
        "rho_k = mean ||Delta^k v||^2 / (C(2k, k) ||v||^2); white jitter of relative variance s^2 gives rho_k = s^2 for every k,",
        "a smooth field gives values that fall quickly with k. Mean over units.",
        "",
        "| cfg | steps | rho_1 | rho_2 | rho_3 | rho_4 | rho_4 / rho_1 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    summary = {}
    for cfg in arguments.cfgs:
        for steps in arguments.steps:
            profiles = []
            for seed in arguments.seeds:
                for prompt in arguments.prompts:
                    path = run_velocities.path_for(cfg, steps, prompt, seed)
                    if path.exists():
                        profiles.append(difference_profile(np.load(path)["guided"].astype(np.float64)))
            if not profiles:
                continue
            mean = np.mean(profiles, axis=0)
            summary[f"{cfg:g}|{steps}"] = mean.tolist()
            lines.append(
                f"| {cfg:g} | {steps} | " + " | ".join(f"{value:.5f}" for value in mean) + f" | {mean[-1] / mean[0]:.2f} |"
            )
    text = "\n".join(lines)
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / f"{arguments.name}.json").write_text(json.dumps(summary), encoding="utf-8")
    (RESULTS / f"{arguments.name}.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
