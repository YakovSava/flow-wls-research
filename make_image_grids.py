import json
import pathlib
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from _bootstrap import module

harness = module("harness")
sweep = module("sweep")
perceptual = module("perceptual")
run_sweep_perceptual = module("run_sweep_perceptual")

FIGURES = harness.ROOT / "figures"
RESULTS = harness.ROOT / "results"
FONT_PATH: str = "C:/Windows/Fonts/arial.ttf"
TILE_WIDTH: int = 300
LABEL_WIDTH: int = 210
HEADER_HEIGHT: int = 44
ROWS: list[tuple[str, str]] = [
    ("euler", "Euler (default)"),
    ("dpmpp2m", "DPM++ 2M"),
    ("ab2", "AB-2 (new)"),
    ("ab3", "AB-3"),
    ("wls8", "WLS-8 (my old idea)"),
]
GRIDS: list[dict[str, Any]] = [
    {"model": "anima", "mode": "bf16", "cfg": 5.0, "prompt": "face", "seed": 42, "budgets": [8, 12, 16],
     "scores": "e4_anima_perceptual.json", "title": "Anima, CFG 5", "file": "grid_anima_face_cfg5.jpg"},
    {"model": "anima", "mode": "bf16", "cfg": 5.0, "prompt": "fur", "seed": 42, "budgets": [8, 12, 16],
     "scores": "e4_anima_perceptual.json", "title": "Anima, CFG 5", "file": "grid_anima_fur_cfg5.jpg"},
    {"model": "flux3", "mode": "q", "cfg": 1.0, "prompt": "face", "seed": 42, "budgets": [8, 12],
     "scores": "e5_flux3_c1_perceptual.json", "title": "Flux3-Klein INT8, CFG 1", "file": "grid_flux3_face_cfg1.jpg"},
    {"model": "krea2", "mode": "q", "cfg": 1.0, "prompt": "face", "seed": 42, "budgets": [8, 12],
     "scores": "e5_krea2_c1_perceptual.json", "title": "Krea 2 INT8, CFG 1", "file": "grid_krea2_face_cfg1.jpg"},
]


def to_image(tensor) -> Image.Image:
    array = (tensor[0].numpy() * 255.0).round().clip(0, 255).astype(np.uint8)
    image = Image.fromarray(array)
    height = round(image.height * TILE_WIDTH / image.width)
    return image.resize((TILE_WIDTH, height), Image.LANCZOS)


def build(spec: dict[str, Any], vae, config, font, small) -> Image.Image:
    cell = sweep.Cell(spec["model"], spec["mode"], spec["cfg"])
    scores = json.loads((RESULTS / spec["scores"]).read_text())
    columns = [(f"{budget} steps", budget) for budget in spec["budgets"]] + [("reference", None)]
    tiles: dict[tuple[int, int], Image.Image] = {}
    for column, (_, budget) in enumerate(columns):
        for row, (method, _) in enumerate(ROWS):
            if budget is None:
                name = sweep.reference_tag(cell.truth, spec["prompt"], spec["seed"])
            else:
                name = sweep.tag(cell, spec["prompt"], spec["seed"], method, budget)
            image = to_image(run_sweep_perceptual.decode(vae, config, name))
            if budget is not None and name in scores:
                draw = ImageDraw.Draw(image)
                text = f"LPIPS {scores[name]['lpips']:.2f}"
                box = draw.textbbox((0, 0), text, font=small)
                draw.rectangle((0, image.height - box[3] - 8, box[2] + 10, image.height), fill=(0, 0, 0))
                draw.text((5, image.height - box[3] - 5), text, fill=(255, 255, 255), font=small)
            tiles[(row, column)] = image
    tile_height = tiles[(0, 0)].height
    width = LABEL_WIDTH + TILE_WIDTH * len(columns)
    height = HEADER_HEIGHT + tile_height * len(ROWS)
    sheet = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    draw.text((10, 10), f"{spec['title']} - prompt '{spec['prompt']}', seed {spec['seed']}; LPIPS = distance to the reference (lower is closer)", fill=(0, 0, 0), font=small)
    for column, (label, _) in enumerate(columns):
        draw.text((LABEL_WIDTH + column * TILE_WIDTH + 8, 26), label, fill=(0, 0, 0), font=small)
    for row, (_, label) in enumerate(ROWS):
        draw.text((8, HEADER_HEIGHT + row * tile_height + tile_height // 2 - 10), label, fill=(0, 0, 0), font=font)
        for column in range(len(columns)):
            sheet.paste(tiles[(row, column)], (LABEL_WIDTH + column * TILE_WIDTH, HEADER_HEIGHT + row * tile_height))
    return sheet


def main() -> None:
    harness.limit_gpu_memory()
    font = ImageFont.truetype(FONT_PATH, 20)
    small = ImageFont.truetype(FONT_PATH, 15)
    FIGURES.mkdir(exist_ok=True)
    vaes: dict[str, Any] = {}
    for spec in GRIDS:
        config = harness.MODEL_CONFIGS[spec["model"]]
        if config.vae not in vaes:
            vaes[config.vae] = run_sweep_perceptual.load_vae(config)
        sheet = build(spec, vaes[config.vae], config, font, small)
        path: pathlib.Path = FIGURES / spec["file"]
        sheet.save(path, quality=90)
        print("wrote", path.name, sheet.size, flush=True)


if __name__ == "__main__":
    main()
