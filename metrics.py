from typing import Callable, Sequence

import numpy as np

POOL: int = 8
SCALE_FLOOR: float = 1e-30


def lowpass(latent: np.ndarray, pool: int = POOL) -> np.ndarray:
    height, width = latent.shape[-2], latent.shape[-1]
    trimmed = latent[..., : height // pool * pool, : width // pool * pool]
    shape = trimmed.shape[:-2] + (
        trimmed.shape[-2] // pool,
        pool,
        trimmed.shape[-1] // pool,
        pool,
    )
    return trimmed.reshape(shape).mean(axis=(-3, -1))


def detail(latent: np.ndarray, pool: int = POOL) -> np.ndarray:
    coarse = lowpass(latent, pool)
    expanded = np.repeat(np.repeat(coarse, pool, axis=-2), pool, axis=-1)
    height, width = expanded.shape[-2], expanded.shape[-1]
    return latent[..., :height, :width] - expanded


def rms(value: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.asarray(value, dtype=np.float64) ** 2)))


def total_error(latent: np.ndarray, reference: np.ndarray) -> float:
    return rms(latent - reference) / max(rms(reference), SCALE_FLOOR)


def geometry_error(latent: np.ndarray, reference: np.ndarray, pool: int = POOL) -> float:
    return rms(lowpass(latent, pool) - lowpass(reference, pool)) / max(rms(reference), SCALE_FLOOR)


def detail_error(latent: np.ndarray, reference: np.ndarray, pool: int = POOL) -> float:
    return rms(detail(latent, pool) - detail(reference, pool)) / max(rms(reference), SCALE_FLOOR)


def bootstrap(
    statistic: Callable[[np.ndarray], float],
    count: int,
    resamples: int = 4000,
    seed: int = 0,
) -> tuple[float, float, float]:
    generator = np.random.default_rng(seed)
    draws = generator.integers(0, count, size=(resamples, count))
    values = np.array([statistic(indices) for indices in draws])
    point = statistic(np.arange(count))
    if np.all(np.isnan(values)):
        return point, float("nan"), float("nan")
    low, high = np.nanpercentile(values, [2.5, 97.5])
    return point, float(low), float(high)


def paired_difference(first: Sequence[float], second: Sequence[float]) -> tuple[float, float, float]:
    a = np.asarray(first, dtype=np.float64)
    b = np.asarray(second, dtype=np.float64)
    return bootstrap(lambda indices: float(np.mean(a[indices] - b[indices])), len(a))


def paired_ratio(first: Sequence[float], second: Sequence[float]) -> tuple[float, float, float]:
    a = np.asarray(first, dtype=np.float64)
    b = np.asarray(second, dtype=np.float64)
    return bootstrap(lambda indices: float(np.mean(a[indices]) / np.mean(b[indices])), len(a))
