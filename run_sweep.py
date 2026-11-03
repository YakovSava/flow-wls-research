import argparse
import json

from _bootstrap import module

harness = module("harness")
sweep = module("sweep")
sweep_report = module("sweep_report")

RESULTS = harness.ROOT / "results"
DEFAULT_SEEDS: list[int] = [42, 1337]
DEFAULT_BUDGETS: list[int] = [8, 12]
DEFAULT_METHODS: list[str] = ["euler", "ab3", "ab4", "wls5", "wls8", "dynamic"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, choices=list(harness.MODEL_CONFIGS))
    parser.add_argument("--modes", nargs="+", required=True)
    parser.add_argument("--cfgs", nargs="+", type=float, required=True)
    parser.add_argument("--prompts", nargs="+", default=list(harness.PROMPTS))
    parser.add_argument("--seeds", nargs="+", type=int, default=DEFAULT_SEEDS)
    parser.add_argument("--methods", nargs="+", default=DEFAULT_METHODS, choices=list(sweep.METHODS))
    parser.add_argument("--budgets", nargs="+", type=int, default=DEFAULT_BUDGETS)
    parser.add_argument("--name", required=True)
    parser.add_argument("--check-convergence", action="store_true")
    parser.add_argument("--report-only", action="store_true")
    arguments = parser.parse_args()

    cells = [sweep.Cell(arguments.model, mode, cfg) for cfg in arguments.cfgs for mode in arguments.modes]
    units = [(prompt, seed) for seed in arguments.seeds for prompt in arguments.prompts]
    if not arguments.report_only:
        harness.limit_gpu_memory()
        rig = harness.Rig(harness.MODEL_CONFIGS[arguments.model])
        sweep.execute(rig, cells, units, arguments.methods, arguments.budgets, arguments.check_convergence)
        rig.release()
    table = sweep_report.collect(cells, units, arguments.methods, arguments.budgets)
    text = sweep_report.format_report(table, cells, arguments.methods, arguments.budgets)
    text += "\n" + "\n".join(sweep_report.convergence_check(cells, table["units"]))
    text += "\n" + "\n".join(sweep_report.selection_summary(cells, table["units"], arguments.budgets))
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / f"{arguments.name}.md").write_text(text, encoding="utf-8")
    (RESULTS / f"{arguments.name}.json").write_text(json.dumps(table), encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
