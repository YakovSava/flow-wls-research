import dataclasses
from typing import Sequence

import numpy as np

from _bootstrap import module

history_filter = module("history_filter")

SCALE_FLOOR: float = 1e-30


def flatten(series: Sequence[np.ndarray]) -> np.ndarray:
    return np.stack([np.asarray(item, dtype=np.float64).reshape(-1) for item in series])


def relative_size(errors: np.ndarray, signal: np.ndarray) -> np.ndarray:
    return np.linalg.norm(errors, axis=1) / np.maximum(np.linalg.norm(signal, axis=1), SCALE_FLOOR)


def lagged_cosine(errors: np.ndarray, lag: int) -> np.ndarray:
    head, tail = errors[lag:], errors[:-lag]
    numerator = np.sum(head * tail, axis=1)
    scale = np.linalg.norm(head, axis=1) * np.linalg.norm(tail, axis=1)
    return numerator / np.maximum(scale, SCALE_FLOOR)


def second_difference_ratio(errors: np.ndarray) -> float:
    curvature = errors[2:] - 2.0 * errors[1:-1] + errors[:-2]
    return float(np.sum(curvature**2) / (6.0 * np.sum(errors**2)))


def spatial_high_fraction(field: np.ndarray, cutoff: float = 0.5) -> float:
    channels, height, width = field.shape
    spectrum = np.abs(np.fft.fft2(field, axes=(-2, -1))) ** 2
    ky = np.fft.fftfreq(height)[:, None] * 2.0
    kx = np.fft.fftfreq(width)[None, :] * 2.0
    radius = np.sqrt(ky**2 + kx**2) / np.sqrt(2.0)
    mask = radius >= cutoff
    return float(spectrum[:, mask].sum() / spectrum.sum())


@dataclasses.dataclass(frozen=True)
class Response:
    realised: float
    white: float


def accumulated_response(
    errors: np.ndarray,
    sigmas: Sequence[float],
    spec: "history_filter.FilterSpec",
) -> Response:
    steps = errors.shape[0]
    composite = history_filter.composite_weights(sigmas[: steps + 1], spec)
    reference = np.diff(np.asarray(sigmas[: steps + 1], dtype=np.float64))
    euler_total = np.einsum("j,jk->k", reference, errors)
    total = np.einsum("j,jk->k", composite, errors)
    norms = np.sum(errors**2, axis=1)
    return Response(
        realised=float(np.linalg.norm(total) / np.linalg.norm(euler_total)),
        white=float(np.sqrt(np.sum(composite**2 * norms) / np.sum(reference**2 * norms))),
    )


def mean_and_error(values: Sequence[float]) -> tuple[float, float]:
    array = np.asarray(values, dtype=np.float64)
    if array.size == 0:
        return float("nan"), float("nan")
    return float(array.mean()), float(array.std(ddof=1) / np.sqrt(array.size)) if array.size > 1 else 0.0
