from typing import Any, Callable, Sequence

import torch
from comfy.utils import model_trange as trange

from .history_filter import (
    DEFAULT_GRID,
    FilterSpec,
    HistoryGram,
    select_spec,
    step_weights,
    wls_spec,
)

SIGMA_FLOOR: float = 1e-4
StepObserver = Callable[[int, FilterSpec], None]


@torch.no_grad()
def sample_history(
    model: Any,
    x: torch.Tensor,
    sigmas: torch.Tensor,
    extra_args: dict[str, Any] | None = None,
    callback: Callable[..., Any] | None = None,
    disable: bool | None = None,
    spec: FilterSpec | None = None,
    dynamic: bool = False,
    grid: Sequence[FilterSpec] = DEFAULT_GRID,
    origins: int = 3,
    observer: StepObserver | None = None,
) -> torch.Tensor:
    if len(sigmas) <= 1:
        return x

    base: FilterSpec = spec if spec is not None else wls_spec(6)
    extra_args = {} if extra_args is None else extra_args
    s_in: torch.Tensor = x.new_ones([x.shape[0]])
    schedule: list[float] = [float(value) for value in sigmas.detach().cpu()]
    longest: int = max([base.length] + [candidate.length for candidate in grid])
    history: list[torch.Tensor] = []
    gram: HistoryGram = HistoryGram(longest + origins)

    for index in trange(len(sigmas) - 1, disable=disable):
        denoised: torch.Tensor = model(x, sigmas[index] * s_in, **extra_args)
        if callback is not None:
            callback({"x": x, "i": index, "sigma": sigmas[index], "sigma_hat": sigmas[index], "denoised": denoised})

        if schedule[index + 1] == 0:
            x = denoised
            break

        velocity: torch.Tensor = (x - denoised) / max(schedule[index], SIGMA_FLOOR)
        history.insert(0, velocity)
        del history[longest:]

        chosen: FilterSpec = base
        if dynamic:
            gram.push(velocity)
            chosen = select_spec(gram, schedule, index, grid, origins, base)
        if observer is not None:
            observer(index, chosen)

        weights = step_weights(schedule, index, chosen)
        increment: torch.Tensor = torch.zeros_like(x)
        for weight, past in zip(weights, history):
            increment = increment + float(weight) * past
        x = x + increment

    return x
