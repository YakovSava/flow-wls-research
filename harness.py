import dataclasses
import pathlib
from typing import Any, Callable

import numpy as np
import torch

from _bootstrap import module

import comfy.model_management
import comfy.ops
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
    clip_dir: str = "clip"
    clip_type: str = "STABLE_DIFFUSION"
    vae: str = "qwenImage_qwenImageVAE.safetensors"
    width: int = 576
    height: int = 768
    cfg: float = 5.0
    scheduler: str = "normal"
    simulate: bool = True


REAL_INT8_MODES: tuple[str, ...] = ("q", "d")
MEMORY_FRACTION: float = 0.93
FLUX2_VAE: str = "flux2-vae.safetensors"
MODEL_CONFIGS: dict[str, RigConfig] = {
    "anima": RigConfig(),
    "flux3": RigConfig(
        unet="flux3Klein_klein_pruned_int8.safetensors",
        clip="flux3Klein_klein_txt_3299383.safetensors",
        clip_type="FLUX3",
        vae=FLUX2_VAE,
        width=768,
        height=768,
        cfg=4.0,
        scheduler="simple",
        simulate=False,
    ),
    "moss": RigConfig(
        unet="mossImage_sft_pruned_int8.safetensors",
        clip="mossImage_sft_txt_int8.safetensors",
        clip_dir="text_encoders",
        clip_type="MOSS_IMAGE",
        vae=FLUX2_VAE,
        width=768,
        height=768,
        cfg=4.0,
        scheduler="simple",
        simulate=False,
    ),
    "krea2": RigConfig(
        unet="kromaKrea2_opd.safetensors",
        clip="qwen3vl_4b_bf16.safetensors",
        clip_type="KREA2",
        width=768,
        height=768,
        cfg=4.0,
        scheduler="simple",
        simulate=False,
    ),
}


def limit_gpu_memory(fraction: float = MEMORY_FRACTION) -> None:
    torch.cuda.set_per_process_memory_fraction(fraction)


class Rig:
    def __init__(self, config: RigConfig = RigConfig(), prompts: dict[str, str] = PROMPTS) -> None:
        self.config: RigConfig = config
        self.patcher = comfy.sd.load_diffusion_model(
            str(MODELS / "diffusion_models" / config.unet), disable_dynamic=True
        )
        clip = comfy.sd.load_clip(
            [str(MODELS / config.clip_dir / config.clip)],
            clip_type=getattr(comfy.sd.CLIPType, config.clip_type),
        )
        self.conditioning: dict[str, tuple[Any, Any]] = {
            name: (self.encode(clip, text), self.encode(clip, NEGATIVE)) for name, text in prompts.items()
        }
        del clip
        comfy.model_management.soft_empty_cache()
        self.weights = fakequant.QuantizedWeights(self.patcher.model.diffusion_model) if config.simulate else None

    @staticmethod
    def encode(clip: Any, text: str) -> Any:
        return clip.encode_from_tokens_scheduled(clip.tokenize(text))

    def use(self, name: str) -> None:
        if self.config.simulate:
            self.weights.apply(fakequant.SPECS[name])
            return
        for layer in self.patcher.model.modules():
            if isinstance(layer, comfy.ops.MixedPrecisionOp):
                layer._full_precision_mm = name == "d" or layer._full_precision_mm_config

    def release(self) -> None:
        if self.config.simulate:
            self.weights.release()

    @property
    def latent_dimensions(self) -> int:
        return self.patcher.get_model_object("latent_format").latent_dimensions

    def sigmas(self, steps: int) -> torch.Tensor:
        sampling = self.patcher.get_model_object("model_sampling")
        return comfy.samplers.calculate_sigmas(sampling, self.config.scheduler, steps)

    def empty_latent(self) -> torch.Tensor:
        latent = torch.zeros([1, 4, self.config.height // 8, self.config.width // 8])
        return comfy.sample.fix_empty_latent_channels(self.patcher, latent, downscale_ratio_spacial=8)

    def sample(self, prompt: str, seed: int, steps: int, sampler: SamplerFunction, cfg: float | None = None) -> np.ndarray:
        latent = self.empty_latent()
        noise = comfy.sample.prepare_noise(latent, seed)
        positive, negative = self.conditioning[prompt]
        guider = comfy.samplers.CFGGuider(self.patcher)
        guider.set_conds(positive, negative)
        guider.set_cfg(self.config.cfg if cfg is None else cfg)
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
