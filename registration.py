from typing import Any, Callable

import comfy.k_diffusion.sampling as k_diffusion_sampling
import comfy.samplers

from .history_filter import adams_bashforth_spec
from .samplers import sample_history

ADAMS_BASHFORTH_ORDERS: dict[str, int] = {"flow_ab2": 2, "flow_ab3": 3, "flow_ab4": 4}


def make_sampler(name: str, order: int) -> Callable[..., Any]:
    spec = adams_bashforth_spec(order)

    def sampler(
        model: Any,
        x: Any,
        sigmas: Any,
        extra_args: dict[str, Any] | None = None,
        callback: Any = None,
        disable: bool | None = None,
    ) -> Any:
        return sample_history(model, x, sigmas, extra_args=extra_args, callback=callback, disable=disable, spec=spec)

    sampler.__name__ = f"sample_{name}"
    return sampler


def register_samplers() -> None:
    for name, order in ADAMS_BASHFORTH_ORDERS.items():
        setattr(k_diffusion_sampling, f"sample_{name}", make_sampler(name, order))
        if name not in comfy.samplers.KSAMPLER_NAMES:
            comfy.samplers.KSAMPLER_NAMES.append(name)
        if name not in comfy.samplers.SAMPLER_NAMES:
            comfy.samplers.SAMPLER_NAMES.append(name)
