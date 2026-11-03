import dataclasses
import itertools
from typing import Sequence

import numpy as np
import torch

CONDITION_FLOOR: float = 1e-12


@dataclasses.dataclass(frozen=True)
class FilterSpec:
    length: int
    gamma: float = 0.85
    degree: int = 2
    ridge: float = 0.0


def euler_spec() -> FilterSpec:
    return FilterSpec(length=1, gamma=1.0, degree=0)


def adams_bashforth_spec(order: int) -> FilterSpec:
    return FilterSpec(length=order, gamma=1.0, degree=order - 1)


def wls_spec(length: int, gamma: float = 0.85, degree: int = 2, ridge: float = 0.0) -> FilterSpec:
    return FilterSpec(length=length, gamma=gamma, degree=degree, ridge=ridge)


def nodes_from_sigmas(sigmas: Sequence[float], index: int, length: int) -> np.ndarray:
    count: int = min(length, index + 1)
    current: float = float(sigmas[index])
    return np.array([float(sigmas[index - k]) - current for k in range(count)])


def polynomial_coefficients(nodes: np.ndarray, spec: FilterSpec) -> tuple[np.ndarray, float]:
    count: int = len(nodes)
    degree: int = min(spec.degree, count - 1)
    scale: float = max(float(np.max(np.abs(nodes))), CONDITION_FLOOR)
    normalized: np.ndarray = nodes / scale
    design: np.ndarray = np.vander(normalized, degree + 1, increasing=True)
    memory: np.ndarray = spec.gamma ** np.arange(count)
    penalty: np.ndarray = np.diag([0.0] + [spec.ridge] * degree)
    normal: np.ndarray = design.T @ (memory[:, None] * design) + penalty
    return np.linalg.pinv(normal) @ (design.T * memory), scale


def integral_weights(nodes: np.ndarray, step: float, spec: FilterSpec) -> np.ndarray:
    projection, scale = polynomial_coefficients(nodes, spec)
    degree: int = projection.shape[0] - 1
    ratio: float = step / scale
    integral: np.ndarray = np.array([scale * ratio ** (m + 1) / (m + 1) for m in range(degree + 1)])
    return integral @ projection


def point_weights(nodes: np.ndarray, target: float, spec: FilterSpec) -> np.ndarray:
    projection, scale = polynomial_coefficients(nodes, spec)
    degree: int = projection.shape[0] - 1
    powers: np.ndarray = np.array([(target / scale) ** m for m in range(degree + 1)])
    return powers @ projection


def step_weights(sigmas: Sequence[float], index: int, spec: FilterSpec) -> np.ndarray:
    nodes: np.ndarray = nodes_from_sigmas(sigmas, index, spec.length)
    step: float = float(sigmas[index + 1]) - float(sigmas[index])
    return integral_weights(nodes, step, spec)


def composite_weights(sigmas: Sequence[float], spec: FilterSpec) -> np.ndarray:
    steps: int = len(sigmas) - 1
    total: np.ndarray = np.zeros(steps)
    for index in range(steps):
        if index == steps - 1 and float(sigmas[-1]) == 0.0:
            total[index] += float(sigmas[index + 1]) - float(sigmas[index])
            continue
        weights: np.ndarray = step_weights(sigmas, index, spec)
        for lag, weight in enumerate(weights):
            total[index - lag] += weight
    return total


def white_noise_gain(sigmas: Sequence[float], spec: FilterSpec) -> float:
    composite: np.ndarray = composite_weights(sigmas, spec)
    reference: np.ndarray = np.diff(np.asarray(sigmas, dtype=np.float64))
    return float(np.sqrt(np.sum(composite**2) / np.sum(reference**2)))


def per_step_gain(sigmas: Sequence[float], spec: FilterSpec) -> np.ndarray:
    steps: int = len(sigmas) - 1
    gains: np.ndarray = np.zeros(steps)
    for index in range(steps):
        weights: np.ndarray = step_weights(sigmas, index, spec)
        gains[index] = np.sqrt(np.sum(weights**2)) / abs(sigmas[index + 1] - sigmas[index])
    return gains


def frequency_response(weights: np.ndarray, step: float, frequencies: np.ndarray) -> np.ndarray:
    lags: np.ndarray = np.arange(len(weights))
    phases: np.ndarray = np.exp(-1j * np.outer(frequencies, lags))
    return np.abs(phases @ weights) / abs(step)


def build_grid(
    lengths: Sequence[int],
    gammas: Sequence[float],
    degrees: Sequence[int],
    ridges: Sequence[float] = (0.0,),
) -> tuple[FilterSpec, ...]:
    return tuple(
        FilterSpec(length=length, gamma=gamma, degree=degree, ridge=ridge)
        for length, gamma, degree, ridge in itertools.product(lengths, gammas, degrees, ridges)
    )


DEFAULT_GRID: tuple[FilterSpec, ...] = build_grid((4, 5, 6, 8), (0.7, 0.85, 1.0), (2, 3))
QUADRATIC_GRID: tuple[FilterSpec, ...] = build_grid((3, 4, 5, 6, 8), (0.7, 0.85, 1.0), (2,))


class HistoryGram:
    def __init__(self, capacity: int) -> None:
        self.capacity: int = capacity
        self.values: list[torch.Tensor] = []
        self.gram: np.ndarray = np.zeros((0, 0))

    def push(self, value: torch.Tensor) -> None:
        flat = value.reshape(-1).float()
        if self.values:
            stack = self.stack()
            inner = (stack @ flat).double().cpu().numpy()
        else:
            inner = np.zeros(0)
        own: float = float(flat.double().dot(flat.double()).cpu())
        size: int = len(self.values)
        grown: np.ndarray = np.zeros((size + 1, size + 1))
        grown[:size, :size] = self.gram
        grown[size, :size] = inner
        grown[:size, size] = inner
        grown[size, size] = own
        self.values.append(flat)
        self.gram = grown
        if len(self.values) > self.capacity:
            self.values.pop(0)
            self.gram = self.gram[1:, 1:]

    def stack(self) -> torch.Tensor:
        return torch.stack(self.values)

    def newest_first_gram(self) -> np.ndarray:
        return self.gram[::-1, ::-1]


def validation_score(
    gram_newest_first: np.ndarray,
    sigmas: Sequence[float],
    index: int,
    spec: FilterSpec,
    origins: int,
) -> float:
    score: float = 0.0
    used: int = 0
    available: int = gram_newest_first.shape[0]
    for back in range(origins):
        target_position: int = index - back
        history_end: int = target_position - 1
        if history_end < 1:
            continue
        nodes: np.ndarray = nodes_from_sigmas(sigmas, history_end, spec.length)
        offset: float = float(sigmas[target_position]) - float(sigmas[history_end])
        weights: np.ndarray = point_weights(nodes, offset, spec)
        coefficients: np.ndarray = np.concatenate(([1.0], -weights))
        first: int = back
        last: int = first + len(coefficients)
        if last > available:
            continue
        block: np.ndarray = gram_newest_first[first:last, first:last]
        score += float(coefficients @ block @ coefficients)
        used += 1
    return score / used if used else float("inf")


def select_spec(
    history: HistoryGram,
    sigmas: Sequence[float],
    index: int,
    grid: Sequence[FilterSpec],
    origins: int,
    fallback: FilterSpec,
) -> FilterSpec:
    gram: np.ndarray = history.newest_first_gram()
    best: FilterSpec = fallback
    best_score: float = validation_score(gram, sigmas, index, fallback, origins)
    for spec in grid:
        score: float = validation_score(gram, sigmas, index, spec, origins)
        if score < best_score:
            best, best_score = spec, score
    return best
