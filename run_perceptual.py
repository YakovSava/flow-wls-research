import argparse
import json
import pathlib

import lpips
import numpy as np
import torch

from _bootstrap import module

import comfy.sd
import comfy.utils

harness = module("harness")
perceptual = module("perceptual")
run_end_to_end = module("run_end_to_end")
metrics = module("metrics")

RESULTS: pathlib.Path = harness.ROOT / "results"
VAE_FILE: str = "qwenImage_qwenImageVAE.safetensors"
BASELINE: str = "bf16"
MEMORY_FRACTION: float = 0.5


def load_vae():
    state = comfy.utils.load_torch_file(str(harness.MODELS / "vae" / VAE_FILE))
    return comfy.sd.VAE(sd=state)


def score(vae, network, name: str, truth_images: torch.Tensor) -> dict[str, float]:
    images = perceptual.decode(vae, np.load(harness.latent_path(name)))
    with torch.no_grad():
        distance = float(network(perceptual.to_lpips_input(images), perceptual.to_lpips_input(truth_images)).mean())
    return {"ssim": perceptual.ssim(images, truth_images), "lpips": distance}


def run(units, specs, methods, budgets) -> dict[str, dict[str, float]]:
    vae = load_vae()
    network = lpips.LPIPS(net="alex", verbose=False)
    path = RESULTS / "perceptual.json"
    results: dict[str, dict[str, float]] = json.loads(path.read_text()) if path.exists() else {}
    for prompt, seed in units:
        truth_name = run_end_to_end.reference_tag(BASELINE, prompt, seed)
        if not harness.latent_path(truth_name).exists():
            continue
        truth = perceptual.decode(vae, np.load(harness.latent_path(truth_name)))
        for spec in specs:
            names = [run_end_to_end.reference_tag(spec, prompt, seed)]
            names += [run_end_to_end.tag(spec, prompt, seed, m, n) for m in methods for n in budgets]
            for name in names:
                if name in results or not harness.latent_path(name).exists():
                    continue
                results[name] = score(vae, network, name, truth)
        path.write_text(json.dumps(results), encoding="utf-8")
        print(f"{prompt} s{seed} scored", flush=True)
    return results


def report(results, units, specs, methods, budgets) -> str:
    lines: list[str] = []
    for key, title, better in (("ssim", "SSIM vs decoded converged bf16 (higher is better)", "max"),
                               ("lpips", "LPIPS(alex) vs decoded converged bf16 (lower is better)", "min")):
        for steps in budgets:
            lines.append(f"\n### {title}, {steps} steps\n")
            lines.append("| method | " + " | ".join(specs) + " |")
            lines.append("| --- |" + " --- |" * len(specs))
            for method in methods:
                cells = []
                for spec in specs:
                    values = [
                        results[run_end_to_end.tag(spec, p, s, method, steps)][key]
                        for p, s in units
                        if run_end_to_end.tag(spec, p, s, method, steps) in results
                    ]
                    cells.append(f"{np.mean(values):.4f}" if values else "n/a")
                lines.append(f"| {method} | " + " | ".join(cells) + " |")
    lines.append("\n### Quantization floor in image space (converged quantized vs converged bf16)\n")
    lines.append("| spec | SSIM | LPIPS |")
    lines.append("| --- | --- | --- |")
    for spec in specs:
        rows = [
            results[run_end_to_end.reference_tag(spec, p, s)]
            for p, s in units
            if run_end_to_end.reference_tag(spec, p, s) in results
        ]
        if rows:
            lines.append(f"| {spec} | {np.mean([r['ssim'] for r in rows]):.4f} | {np.mean([r['lpips'] for r in rows]):.4f} |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompts", nargs="+", default=list(harness.PROMPTS))
    parser.add_argument("--seeds", nargs="+", type=int, default=run_end_to_end.SEEDS)
    parser.add_argument("--specs", nargs="+", default=list(run_end_to_end.fakequant.SPECS))
    parser.add_argument("--methods", nargs="+", default=list(run_end_to_end.METHODS))
    parser.add_argument("--budgets", nargs="+", type=int, default=run_end_to_end.BUDGETS)
    parser.add_argument("--report-only", action="store_true")
    parser.add_argument("--name", default="perceptual")
    arguments = parser.parse_args()
    torch.cuda.set_per_process_memory_fraction(MEMORY_FRACTION)
    units = [(p, s) for s in arguments.seeds for p in arguments.prompts]
    if arguments.report_only:
        results = json.loads((RESULTS / "perceptual.json").read_text())
    else:
        results = run(units, arguments.specs, arguments.methods, arguments.budgets)
    text = report(results, units, arguments.specs, arguments.methods, arguments.budgets)
    (RESULTS / f"{arguments.name}.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
