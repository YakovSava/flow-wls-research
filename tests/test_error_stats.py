import numpy as np

from _bootstrap import module

stats = module("error_stats")
hf = module("history_filter")


def schedule(steps: int, shift: float = 3.0) -> list[float]:
    grid = np.linspace(1.0, 0.0, steps + 1)
    return list(shift * grid / (1.0 + (shift - 1.0) * grid))


def test_lagged_cosine_is_one_for_constant_and_near_zero_for_white() -> None:
    constant = np.tile(np.arange(1.0, 9.0), (12, 1))
    assert np.allclose(stats.lagged_cosine(constant, 1), 1.0)
    white = np.random.default_rng(0).normal(size=(400, 512))
    assert abs(stats.lagged_cosine(white, 1).mean()) < 0.02


def test_second_difference_ratio_distinguishes_white_from_smooth() -> None:
    generator = np.random.default_rng(1)
    white = generator.normal(size=(60, 256))
    smooth = np.cumsum(generator.normal(size=(60, 256)), axis=0) * 0.01 + 1.0
    assert 0.9 < stats.second_difference_ratio(white) < 1.1
    assert stats.second_difference_ratio(smooth) < 0.01


def test_spatial_high_fraction_orders_smooth_and_checkerboard() -> None:
    height, width = 32, 32
    y, x = np.mgrid[0:height, 0:width]
    smooth = np.sin(2 * np.pi * x / width)[None]
    checker = ((-1.0) ** (x + y))[None]
    assert stats.spatial_high_fraction(smooth) < 0.01
    assert stats.spatial_high_fraction(checker) > 0.9


def test_euler_response_is_one_and_constant_errors_pass_through_every_method() -> None:
    sigmas = schedule(14)
    errors = np.tile(np.random.default_rng(2).normal(size=(1, 64)), (14, 1))
    for spec in (hf.euler_spec(), hf.adams_bashforth_spec(4), hf.wls_spec(8)):
        response = stats.accumulated_response(errors, sigmas, spec)
        assert np.isclose(response.realised, 1.0, atol=1e-9)


def test_white_errors_are_amplified_by_adams_bashforth_as_predicted() -> None:
    sigmas = schedule(14)
    generator = np.random.default_rng(3)
    ratios = []
    for _ in range(40):
        errors = generator.normal(size=(14, 2048))
        ratios.append(stats.accumulated_response(errors, sigmas, hf.adams_bashforth_spec(4)))
    realised = np.mean([r.realised for r in ratios])
    predicted = np.mean([r.white for r in ratios])
    assert predicted > 1.5
    assert abs(realised - predicted) / predicted < 0.1


def test_mean_and_error_handles_single_and_empty_samples() -> None:
    assert stats.mean_and_error([2.0]) == (2.0, 0.0)
    mean, error = stats.mean_and_error([1.0, 3.0])
    assert mean == 2.0 and np.isclose(error, 1.0)
    assert np.isnan(stats.mean_and_error([])[0])
