import dataclasses
from typing import Callable

import torch
from torch import nn

FP8_MAX: dict[str, float] = {"e4m3": 448.0, "e5m2": 57344.0}
FP8_DTYPE: dict[str, torch.dtype] = {
    "e4m3": torch.float8_e4m3fn,
    "e5m2": torch.float8_e5m2,
}
FP4_GRID: tuple[float, ...] = (0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0)
FP4_BOUNDARIES: tuple[float, ...] = (0.25, 0.75, 1.25, 1.75, 2.5, 3.5, 5.0)
NVFP4_BLOCK: int = 16
SCALE_FLOOR: float = 1e-12
QUANTIZED_PREFIX: str = "blocks."


def fake_fp8(tensor: torch.Tensor, fmt: str = "e4m3") -> torch.Tensor:
    work: torch.Tensor = tensor.float()
    scale: torch.Tensor = work.abs().amax().clamp(min=SCALE_FLOOR) / FP8_MAX[fmt]
    rounded: torch.Tensor = (work / scale).to(FP8_DTYPE[fmt]).float() * scale
    return rounded.to(tensor.dtype)


def fake_int(tensor: torch.Tensor, bits: int, group: int | None) -> torch.Tensor:
    work: torch.Tensor = tensor.float()
    width: int = work.shape[-1]
    size: int = width if group is None or width % group else group
    grouped: torch.Tensor = work.reshape(*work.shape[:-1], width // size, size)
    top: int = 2 ** (bits - 1) - 1
    scale: torch.Tensor = grouped.abs().amax(dim=-1, keepdim=True).clamp(min=SCALE_FLOOR) / top
    rounded: torch.Tensor = torch.round(grouped / scale).clamp(-top, top) * scale
    return rounded.reshape(work.shape).to(tensor.dtype)


def fake_nvfp4(tensor: torch.Tensor) -> torch.Tensor:
    work: torch.Tensor = tensor.float()
    width: int = work.shape[-1]
    if width % NVFP4_BLOCK:
        return fake_int(tensor, 4, None)
    grouped: torch.Tensor = work.reshape(*work.shape[:-1], width // NVFP4_BLOCK, NVFP4_BLOCK)
    global_scale: torch.Tensor = work.abs().amax().clamp(min=SCALE_FLOOR) / (FP4_GRID[-1] * FP8_MAX["e4m3"])
    block_scale: torch.Tensor = grouped.abs().amax(dim=-1, keepdim=True) / FP4_GRID[-1]
    stored: torch.Tensor = (block_scale / global_scale).clamp(max=FP8_MAX["e4m3"]).to(torch.float8_e4m3fn).float()
    effective: torch.Tensor = (stored * global_scale).clamp(min=SCALE_FLOOR)
    magnitude: torch.Tensor = (grouped / effective).abs()
    boundaries: torch.Tensor = torch.tensor(FP4_BOUNDARIES, device=work.device)
    grid: torch.Tensor = torch.tensor(FP4_GRID, device=work.device)
    snapped: torch.Tensor = grid[torch.bucketize(magnitude, boundaries)]
    result: torch.Tensor = torch.sign(grouped) * snapped * effective
    return result.reshape(work.shape).to(tensor.dtype)


def per_token_int(tensor: torch.Tensor, bits: int) -> torch.Tensor:
    return fake_int(tensor, bits, None)


@dataclasses.dataclass(frozen=True)
class QuantSpec:
    name: str
    weight: Callable[[torch.Tensor], torch.Tensor] | None
    activation: Callable[[torch.Tensor], torch.Tensor] | None


def build_specs() -> dict[str, QuantSpec]:
    return {
        "bf16": QuantSpec("bf16", None, None),
        "fp8_w": QuantSpec("fp8_w", fake_fp8, None),
        "fp8_wa": QuantSpec("fp8_wa", fake_fp8, fake_fp8),
        "int8_wa": QuantSpec(
            "int8_wa",
            lambda t: fake_int(t, 8, None),
            lambda t: per_token_int(t, 8),
        ),
        "int4_w": QuantSpec("int4_w", lambda t: fake_int(t, 4, 64), None),
        "int4_wa8": QuantSpec(
            "int4_wa8",
            lambda t: fake_int(t, 4, 64),
            lambda t: per_token_int(t, 8),
        ),
        "nvfp4_w": QuantSpec("nvfp4_w", fake_nvfp4, None),
    }


SPECS: dict[str, QuantSpec] = build_specs()


def quantizable_layers(model: nn.Module, prefix: str = QUANTIZED_PREFIX) -> dict[str, nn.Linear]:
    return {
        name: module
        for name, module in model.named_modules()
        if isinstance(module, nn.Linear) and name.startswith(prefix)
    }


class QuantizedWeights:
    def __init__(self, model: nn.Module, prefix: str = QUANTIZED_PREFIX) -> None:
        self.layers: dict[str, nn.Linear] = quantizable_layers(model, prefix)
        self.originals: dict[str, torch.Tensor] = {
            name: layer.weight.detach().to("cpu", copy=True)
            for name, layer in self.layers.items()
        }
        self.handles: list[torch.utils.hooks.RemovableHandle] = []
        self.active: str = "bf16"
        self.compute_device: torch.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def apply(self, spec: QuantSpec) -> None:
        self.release()
        for name, layer in self.layers.items():
            source: torch.Tensor = self.originals[name].to(self.compute_device)
            target: torch.Tensor = source if spec.weight is None else spec.weight(source)
            layer.weight.data.copy_(target)
            if spec.activation is not None:
                self.handles.append(layer.register_forward_pre_hook(activation_hook(spec.activation)))
        self.active = spec.name

    def release(self) -> None:
        for handle in self.handles:
            handle.remove()
        self.handles = []
        for name, layer in self.layers.items():
            layer.weight.data.copy_(self.originals[name])
        self.active = "bf16"


def activation_hook(
    quantizer: Callable[[torch.Tensor], torch.Tensor],
) -> Callable[[nn.Module, tuple[torch.Tensor, ...]], tuple[torch.Tensor, ...]]:
    def hook(module: nn.Module, args: tuple[torch.Tensor, ...]) -> tuple[torch.Tensor, ...]:
        return (quantizer(args[0]),) + tuple(args[1:])

    return hook
