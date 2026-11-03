import argparse
import json

import lpips
import numpy as np
import torch

from _bootstrap import module

import comfy.sd
import comfy.utils

harness = module("harness")
perceptual = module("perceptual")
sweep = module("sweep")
sweep_report = module("sweep_report")

RESULTS = harness.ROOT / "results"


def load_vae(config):
    state = comfy.utils.load_torch_file(str(harness.MODELS / "vae" / config.vae))
    return comfy.sd.VAE(sd=state)


def decode(vae, config, name: str) -> torch.Tensor:
    return perceptual.decode(vae, np.load(harness.latent_path(name)), config.latent_dimensions)


def score(images: torch.Tensor, truth: torch.Tensor, network) -> dict[str, float]:
    with torch.no_grad():
        distance = float(network(perceptual.to_lpips_input(images), perceptual.to_lpips_input(truth)).mean())
    return {"ssim": perceptual.ssim(images, truth), "lpips": distance}


def run(config, cells, units, methods, budgets, path) -> dict[str, dict[str, float]]:
    vae = load_vae(config)
    network = lpips.LPIPS(net="alex", verbose=False)
    results: dict[str, dict[str, float]] = json.loads(path.read_text()) if path.exists() else {}
    for prompt, seed in sweep_report.complete_units(cells, units, methods, budgets):
        truths: dict[str, torch.Tensor] = {}
        for cell in cells:
            truth_name = sweep.reference_tag(cell.truth, prompt, seed)
            if truth_name not in truths:
                truths[truth_name] = decode(vae, config, truth_name)
            for name in sweep.needed_tags(cell, prompt, seed, methods, budgets):
                if name not in results:
                    results[name] = score(decode(vae, config, name), truths[truth_name], network)
        path.write_text(json.dumps(results), encoding="utf-8")
        print(f"{prompt} s{seed} scored", flush=True)
    return results


def format_report(results, cells, units, methods, budgets) -> str:
    lines: list[str] = []
    for key, title in (("ssim", "SSIM against decoded converged truth (higher is better)"), ("lpips", "LPIPS(alex) against decoded converged truth (lower is better)")):
        for budget in budgets:
            lines.append(f"\n### {title}, budget {budget}\n")
            lines.append("| method | " + " | ".join(cell.name for cell in cells) + " |")
            lines.append("| --- |" + " --- |" * len(cells))
            for method in methods:
                row = []
                for cell in cells:
                    values = [
                        results[name][key]
                        for prompt, seed in units
                        if (name := sweep.tag(cell, prompt, seed, method, budget)) in results
                    ]
                    row.append(f"{np.mean(values):.4f}" if values else "n/a")
                lines.append(f"| {method} | " + " | ".join(row) + " |")
    lines.append("\n### Floor in image space (converged own solution against converged truth)\n")
    lines.append("| cell | SSIM | LPIPS |")
    lines.append("| --- | --- | --- |")
    for cell in cells:
        rows = [
            results[name]
            for prompt, seed in units
            if (name := sweep.reference_tag(cell, prompt, seed)) in results
        ]
        if rows:
            lines.append(f"| {cell.name} | {np.mean([r['ssim'] for r in rows]):.4f} | {np.mean([r['lpips'] for r in rows]):.4f} |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, choices=list(harness.MODEL_CONFIGS))
    parser.add_argument("--modes", nargs="+", required=True)
    parser.add_argument("--cfgs", nargs="+", type=float, required=True)
    parser.add_argument("--prompts", nargs="+", default=list(harness.PROMPTS))
    parser.add_argument("--seeds", nargs="+", type=int, default=[42, 1337])
    parser.add_argument("--methods", nargs="+", required=True, choices=list(sweep.METHODS))
    parser.add_argument("--budgets", nargs="+", type=int, required=True)
    parser.add_argument("--name", required=True)
    arguments = parser.parse_args()

    harness.limit_gpu_memory()
    config = harness.MODEL_CONFIGS[arguments.model]
    cells = [sweep.Cell(arguments.model, mode, cfg) for cfg in arguments.cfgs for mode in arguments.modes]
    units = [(prompt, seed) for seed in arguments.seeds for prompt in arguments.prompts]
    path = RESULTS / f"{arguments.name}_perceptual.json"
    results = run(config, cells, units, arguments.methods, arguments.budgets, path)
    text = format_report(results, cells, units, arguments.methods, arguments.budgets)
    (RESULTS / f"{arguments.name}_perceptual.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
