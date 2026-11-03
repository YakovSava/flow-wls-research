import functools
from typing import Any

import comfy.samplers

from .history_filter import wls_spec
from .samplers import sample_history


class FlowWLSSampler:
    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        return {
            "required": {
                "history_length": ("INT", {"default": 8, "min": 1, "max": 16}),
                "gamma": ("FLOAT", {"default": 0.85, "min": 0.1, "max": 1.0, "step": 0.01}),
                "degree": ("INT", {"default": 2, "min": 0, "max": 4}),
                "ridge": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 100.0, "step": 0.1}),
                "dynamic": ("BOOLEAN", {"default": False}),
                "origins": ("INT", {"default": 3, "min": 1, "max": 6}),
            }
        }

    RETURN_TYPES = ("SAMPLER",)
    FUNCTION = "get_sampler"
    CATEGORY = "sampling/custom_sampling/samplers"

    def get_sampler(
        self,
        history_length: int,
        gamma: float,
        degree: int,
        ridge: float,
        dynamic: bool,
        origins: int,
    ) -> tuple[Any]:
        sampler_function = functools.partial(
            sample_history,
            spec=wls_spec(history_length, gamma, degree, ridge),
            dynamic=dynamic,
            origins=origins,
        )
        return (comfy.samplers.KSAMPLER(sampler_function),)


NODE_CLASS_MAPPINGS: dict[str, Any] = {"FlowWLSSampler": FlowWLSSampler}
NODE_DISPLAY_NAME_MAPPINGS: dict[str, str] = {"FlowWLSSampler": "Flow-WLS Sampler (static / CV-dynamic)"}
