import dataclasses
import functools
import json
from typing import Any, Callable

import numpy as np

from _bootstrap import module

from comfy.k_diffusion import sampling as k_sampling

harness = module("harness")
samplers = module("samplers")
history_filter = module("history_filter")

REFERENCE_METHOD: str = "wls5"
CONVERGENCE_METHOD: str = "ab3"
REFERENCE_STEPS: dict[str, int] = {"anima": 96, "moss": 160}
DEFAULT_REFERENCE_STEPS: int = 64
TRUTH_MODES: dict[str, str] = {"flux3": "d"}
LEGACY_CELL: tuple[str, str, float] = ("anima", "bf16", 5.0)


@dataclasses.dataclass(frozen=True)
class Method:
    spec: Any | None = None
    dynamic: bool = False
    native: Callable[..., Any] | None = None
    evaluations_per_step: int = 1

    def steps_for(self, budget: int) -> int:
        if self.evaluations_per_step == 2:
            return (budget + 1) // 2
        return budget


METHODS: dict[str, Method] = {
    "euler": Method(history_filter.euler_spec()),
    "ab2": Method(history_filter.adams_bashforth_spec(2)),
    "ab3": Method(history_filter.adams_bashforth_spec(3)),
    "ab4": Method(history_filter.adams_bashforth_spec(4)),
    "wls5": Method(history_filter.wls_spec(5)),
    "wls8": Method(history_filter.wls_spec(8)),
    "dynamic": Method(history_filter.wls_spec(3), dynamic=True),
    "dpmpp2m": Method(native=k_sampling.sample_dpmpp_2m),
    "heun": Method(native=k_sampling.sample_heun, evaluations_per_step=2),
}


@dataclasses.dataclass(frozen=True)
class Cell:
    model: str
    mode: str
    cfg: float

    @property
    def name(self) -> str:
        if (self.model, self.mode, self.cfg) == LEGACY_CELL:
            return "bf16"
        return f"{self.model}-{self.mode}-c{self.cfg:g}"

    @property
    def truth(self) -> "Cell":
        return dataclasses.replace(self, mode=TRUTH_MODES.get(self.model, self.mode))


def tag(cell: Cell, prompt: str, seed: int, method: str, budget: int) -> str:
    return f"{cell.name}__{prompt}_s{seed}__{method}_n{budget:03d}"


def reference_steps(model: str) -> int:
    return REFERENCE_STEPS.get(model, DEFAULT_REFERENCE_STEPS)


def reference_tag(cell: Cell, prompt: str, seed: int, method: str = REFERENCE_METHOD) -> str:
    return tag(cell, prompt, seed, method, reference_steps(cell.model))


def needed_tags(cell: Cell, prompt: str, seed: int, methods: list[str], budgets: list[int]) -> list[str]:
    names = [reference_tag(cell, prompt, seed)]
    names += [tag(cell, prompt, seed, method, budget) for method in methods for budget in budgets]
    return names


def selection_path(name: str):
    return harness.DUMPS / "selections" / f"{name}.json"


def run_one(rig: Any, cell: Cell, prompt: str, seed: int, method: str, budget: int) -> np.ndarray:
    entry = METHODS[method]
    name = tag(cell, prompt, seed, method, budget)
    chosen: list[list[float]] = []

    def observer(index: int, picked: Any) -> None:
        chosen.append([picked.length, picked.gamma, picked.degree])

    if entry.native is not None:
        sampler = functools.partial(entry.native, disable=True)
    else:
        sampler = functools.partial(
            samplers.sample_history,
            spec=entry.spec,
            dynamic=entry.dynamic,
            observer=observer if entry.dynamic else None,
            disable=True,
        )

    def produce() -> np.ndarray:
        return rig.sample(prompt, seed, entry.steps_for(budget), sampler, cfg=cell.cfg)

    value = harness.cached(name, produce)
    if entry.dynamic and chosen:
        path = selection_path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(chosen), encoding="utf-8")
    return value


def is_complete(cell: Cell, prompt: str, seed: int, methods: list[str], budgets: list[int]) -> bool:
    return all(harness.latent_path(name).exists() for name in needed_tags(cell, prompt, seed, methods, budgets))


def execute(
    rig: Any,
    cells: list[Cell],
    units: list[tuple[str, int]],
    methods: list[str],
    budgets: list[int],
    check_convergence: bool,
) -> None:
    for position, (prompt, seed) in enumerate(units, start=1):
        for cell in cells:
            if is_complete(cell, prompt, seed, methods, budgets):
                continue
            rig.use(cell.mode)
            steps = reference_steps(cell.model)
            run_one(rig, cell, prompt, seed, REFERENCE_METHOD, steps)
            if check_convergence and position == 1:
                run_one(rig, cell, prompt, seed, CONVERGENCE_METHOD, steps)
            for method in methods:
                for budget in budgets:
                    run_one(rig, cell, prompt, seed, method, budget)
            print(f"unit {position}/{len(units)} {prompt} s{seed} {cell.name} done", flush=True)
