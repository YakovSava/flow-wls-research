import numpy as np
import pytest
import torch

from _bootstrap import module

hf = module("history_filter")
samplers = module("samplers")

SHAPE: tuple[int, ...] = (1, 4, 6, 6)


def schedule(steps: int, shift: float = 3.0) -> torch.Tensor:
    grid = torch.linspace(1.0, 0.0, steps + 1, dtype=torch.float64)
    return shift * grid / (1.0 + (shift - 1.0) * grid)


def polynomial_model(coefficients: list[float]):
    def velocity(sigma: float) -> float:
        return sum(c * sigma**k for k, c in enumerate(coefficients))

    def model(x: torch.Tensor, sigma: torch.Tensor, **_) -> torch.Tensor:
        level = float(sigma.reshape(-1)[0])
        return x - level * velocity(level)

    return model, velocity


def exact_integral(coefficients: list[float], low: float, high: float) -> float:
    return sum(c * (high ** (k + 1) - low ** (k + 1)) / (k + 1) for k, c in enumerate(coefficients))


def run(coefficients: list[float], spec, steps: int = 12, dynamic: bool = False):
    model, _ = polynomial_model(coefficients)
    sigmas = schedule(steps)
    start = torch.zeros(SHAPE, dtype=torch.float64)
    seen: dict[int, torch.Tensor] = {}

    def callback(info) -> None:
        seen[info["i"]] = info["x"].clone()

    samplers.sample_history(model, start, sigmas, callback=callback, spec=spec, dynamic=dynamic, disable=True)
    return seen, sigmas


@pytest.mark.parametrize("degree", [0, 1, 2])
def test_wls_steps_are_exact_for_polynomial_velocity_after_warm_up(degree: int) -> None:
    coefficients = [0.7, -0.4, 0.3][: degree + 1]
    seen, sigmas = run(coefficients, hf.wls_spec(6, gamma=0.9, degree=2))
    last = max(seen)
    for i in range(3, last):
        expected = exact_integral(coefficients, float(sigmas[i]), float(sigmas[i + 1]))
        increment = seen[i + 1] - seen[i]
        assert torch.allclose(increment, torch.full(SHAPE, expected, dtype=torch.float64), atol=1e-10)


def test_euler_matches_manual_recursion() -> None:
    coefficients = [1.0, 0.5]
    seen, sigmas = run(coefficients, hf.euler_spec())
    value = 0.0
    for i in range(len(sigmas) - 2):
        sigma = float(sigmas[i])
        value += (float(sigmas[i + 1]) - sigma) * (coefficients[0] + coefficients[1] * sigma)
    assert torch.allclose(seen[len(sigmas) - 2], torch.full(SHAPE, value, dtype=torch.float64), atol=1e-12)


def test_dynamic_selection_reports_a_spec_every_step_and_stays_exact_on_smooth_fields() -> None:
    coefficients = [0.5, 0.2, -0.1]
    model, _ = polynomial_model(coefficients)
    sigmas = schedule(12)
    chosen: list[tuple[int, object]] = []
    result = samplers.sample_history(
        model,
        torch.zeros(SHAPE, dtype=torch.float64),
        sigmas,
        spec=hf.wls_spec(3),
        dynamic=True,
        observer=lambda index, spec: chosen.append((index, spec)),
        disable=True,
    )
    assert [index for index, _ in chosen] == list(range(len(sigmas) - 2))
    assert torch.isfinite(result).all()
    seen, _ = run(coefficients, hf.wls_spec(3), dynamic=True)
    for i in range(4, max(seen)):
        expected = exact_integral(coefficients, float(sigmas[i]), float(sigmas[i + 1]))
        increment = seen[i + 1] - seen[i]
        assert torch.allclose(increment, torch.full(SHAPE, expected, dtype=torch.float64), atol=1e-6)


def test_final_step_returns_denoised_prediction() -> None:
    coefficients = [0.3]
    model, _ = polynomial_model(coefficients)
    sigmas = schedule(6)
    result = samplers.sample_history(
        model, torch.zeros(SHAPE, dtype=torch.float64), sigmas, spec=hf.euler_spec(), disable=True
    )
    penultimate = float(sigmas[-2])
    seen, _ = run(coefficients, hf.euler_spec(), steps=6)
    expected = seen[len(sigmas) - 2] - penultimate * coefficients[0]
    assert torch.allclose(result, expected, atol=1e-12)


def test_short_sigma_sequence_returns_input() -> None:
    model, _ = polynomial_model([1.0])
    start = torch.ones(SHAPE)
    out = samplers.sample_history(model, start, torch.tensor([1.0]), disable=True)
    assert torch.equal(out, start)


def test_wls_damps_white_noise_in_a_linear_ode_more_than_adams_bashforth() -> None:
    generator = torch.Generator().manual_seed(0)
    sigmas = schedule(16)

    def noisy_model(x: torch.Tensor, sigma: torch.Tensor, **_) -> torch.Tensor:
        level = float(sigma.reshape(-1)[0])
        noise = 0.3 * torch.randn(x.shape, generator=generator, dtype=x.dtype)
        return x - level * (1.0 + noise)

    errors = {}
    for name, spec in (("ab4", hf.adams_bashforth_spec(4)), ("wls8", hf.wls_spec(8))):
        spread = []
        for _ in range(30):
            out = samplers.sample_history(
                noisy_model, torch.zeros((1, 64), dtype=torch.float64), sigmas, spec=spec, disable=True
            )
            spread.append(float(out.std()))
        errors[name] = np.mean(spread)
    assert errors["wls8"] < errors["ab4"]
