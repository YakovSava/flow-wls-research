import dataclasses
import pathlib
from typing import Any, Callable

import numpy as np
import torch

from _bootstrap import module

import comfy.model_management
import comfy.sample
import comfy.samplers
import comfy.sd

fakequant = module("fakequant")

ROOT: pathlib.Path = pathlib.Path(__file__).resolve().parent
MODELS: pathlib.Path = pathlib.Path("D:/ComfyUI/models")
DUMPS: pathlib.Path = ROOT / "dumps"
NEGATIVE: str = "worst quality, low quality,"

PROMPTS: dict[str, str] = {
    "flat": "1girl, flat color illustration, plain pastel background, simple shading",
    "face": "extreme close-up portrait of a girl's face, soft skin, detailed eyes",
    "fur": "dense forest foliage, fur texture, thousands of leaves",
    "grid": "checkerboard tiled floor, perspective grid, geometric architecture",
}

SamplerFunction = Callable[..., torch.Tensor]


@dataclasses.dataclass(frozen=True)
class RigConfig:
    unet: str = "anima_aestheticV11(1).safetensors"
    clip: str = "anima_baseV10_txt.safetensors"
    clip_type: str = "STABLE_DIFFUSION"
    width: int = 576
    height: int = 768
    cfg: float = 5.0
    scheduler: str = "normal"


class Rig:
    def __init__(self, config: RigConfig = RigConfig(), prompts: dict[str, str] = PROMPTS) -> None:
        self.config: RigConfig = config
        self.patcher = comfy.sd.load_diffusion_model(
            str(MODELS / "diffusion_models" / config.unet), disable_dynamic=True
        )
        clip = comfy.sd.load_clip(
            [str(MODELS / "clip" / config.clip)],
            clip_type=getattr(comfy.sd.CLIPType, config.clip_type),
        )
        self.conditioning: dict[str, tuple[Any, Any]] = {
            name: (self.encode(clip, text), self.encode(clip, NEGATIVE)) for name, text in prompts.items()
        }
        del clip
        comfy.model_management.soft_empty_cache()
        self.weights = fakequant.QuantizedWeights(self.patcher.model.diffusion_model)

    @staticmethod
    def encode(clip: Any, text: str) -> Any:
        return clip.encode_from_tokens_scheduled(clip.tokenize(text))

    def use(self, name: str) -> None:
        self.weights.apply(fakequant.SPECS[name])

    def sigmas(self, steps: int) -> torch.Tensor:
        sampling = self.patcher.get_model_object("model_sampling")
        return comfy.samplers.calculate_sigmas(sampling, self.config.scheduler, steps)

    def empty_latent(self) -> torch.Tensor:
        latent = torch.zeros([1, 4, self.config.height // 8, self.config.width // 8])
        return comfy.sample.fix_empty_latent_channels(self.patcher, latent)

    def sample(self, prompt: str, seed: int, steps: int, sampler: SamplerFunction) -> np.ndarray:
        latent = self.empty_latent()
        noise = comfy.sample.prepare_noise(latent, seed)
        positive, negative = self.conditioning[prompt]
        guider = comfy.samplers.CFGGuider(self.patcher)
        guider.set_conds(positive, negative)
        guider.set_cfg(self.config.cfg)
        result = guider.sample(
            noise,
            latent,
            comfy.samplers.KSAMPLER(sampler),
            self.sigmas(steps),
            seed=seed,
            disable_pbar=True,
        )
        return result.detach().float().cpu().numpy().reshape(result.shape[1], *result.shape[-2:])


def latent_path(tag: str) -> pathlib.Path:
    return DUMPS / "latents" / f"{tag}.npy"


def cached(tag: str, produce: Callable[[], np.ndarray]) -> np.ndarray:
    path = latent_path(tag)
    if path.exists():
        return np.load(path)
    value = produce()
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, value.astype(np.float32))
    return value
