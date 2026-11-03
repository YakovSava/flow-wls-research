import argparse

import numpy as np

from _bootstrap import module

harness = module("harness")
run_diagnostics = module("run_diagnostics")

STORE = harness.DUMPS / "velocities_raw"


def path_for(cfg: float, steps: int, prompt: str, seed: int):
    return STORE / f"c{cfg:g}_n{steps:03d}_{prompt}_s{seed}.npz"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, choices=list(harness.MODEL_CONFIGS))
    parser.add_argument("--mode", required=True)
    parser.add_argument("--cfgs", nargs="+", type=float, required=True)
    parser.add_argument("--steps", nargs="+", type=int, required=True)
    parser.add_argument("--prompts", nargs="+", default=list(harness.PROMPTS))
    parser.add_argument("--seeds", nargs="+", type=int, default=[42, 1337])
    arguments = parser.parse_args()

    STORE.mkdir(parents=True, exist_ok=True)
    harness.limit_gpu_memory()
    rig = harness.Rig(harness.MODEL_CONFIGS[arguments.model])
    rig.use(arguments.mode)
    for seed in arguments.seeds:
        for prompt in arguments.prompts:
            for cfg in arguments.cfgs:
                for steps in arguments.steps:
                    path = path_for(cfg, steps, prompt, seed)
                    if path.exists():
                        continue
                    record = run_diagnostics.record_trajectory(rig, prompt, seed, steps, cfg)
                    guided = run_diagnostics.velocity_components(record)["guided"]
                    np.savez_compressed(path, guided=guided.astype(np.float32), sigmas=np.array(record["sigmas"]))
            print(f"velocities {prompt} s{seed} done", flush=True)
    rig.release()


if __name__ == "__main__":
    main()
