import numpy as np
import pytest
import torch

from _bootstrap import module

hf = module("history_filter")


def shifted_schedule(steps: int, shift: float = 3.0) -> list[float]:
    grid = np.linspace(1.0, 0.0, steps + 1)
    return list(shift * grid / (1.0 + (shift - 1.0) * grid))


def legacy_weights(dt: float, past_dts: list[float], deg: int, gamma: float) -> np.ndarray:
    length = 1 + len(past_dts)
    d = length - 1 if length <= deg + 1 else deg
    nodes = [0.0]
    acc = 0.0
    for h in past_dts:
        acc -= h
        nodes.append(acc)
    nodes_arr = np.array(nodes)
    w_diag = np.diag(np.array([gamma**k for k in range(length)]))
    design = np.column_stack([nodes_arr**m for m in range(d + 1)])
    inverse = np.linalg.pinv(design.T @ w_diag @ design)
    projection = inverse @ design.T @ w_diag
    integral = np.array([(dt ** (m + 1)) / (m + 1) for m in range(d + 1)])
    return integral @ projection


@pytest.mark.parametrize("length", [3, 5, 8])
def test_matches_legacy_implementation(length: int) -> None:
    sigmas = shifted_schedule(14)
    index = 9
    spec = hf.wls_spec(length)
    new = hf.step_weights(sigmas, index, spec)
    dts = [sigmas[k + 1] - sigmas[k] for k in range(index)]
    legacy = legacy_weights(sigmas[index + 1] - sigmas[index], dts[::-1][: length - 1], 2, 0.85)
    assert np.allclose(new, legacy, atol=1e-9)


@pytest.mark.parametrize("order", [1, 2, 3, 4, 5])
def test_adams_bashforth_is_exact_on_polynomials(order: int) -> None:
    sigmas = shifted_schedule(16)
    index = 10
    spec = hf.adams_bashforth_spec(order)
    weights = hf.step_weights(sigmas, index, spec)
    for power in range(order):
        samples = np.array([sigmas[index - k] ** power for k in range(len(weights))])
        exact = (sigmas[index + 1] ** (power + 1) - sigmas[index] ** (power + 1)) / (power + 1)
        assert np.isclose(weights @ samples, exact, atol=1e-10)


def test_adams_bashforth_two_uniform_step_coefficients() -> None:
    sigmas = [4.0, 3.0, 2.0, 1.0, 0.0]
    weights = hf.step_weights(sigmas, 2, hf.adams_bashforth_spec(2))
    assert np.allclose(weights, [-1.5, 0.5])


def test_wls_reproduces_quadratics() -> None:
    sigmas = shifted_schedule(16)
    index = 11
    spec = hf.wls_spec(7, gamma=0.8)
    weights = hf.step_weights(sigmas, index, spec)
    for power in range(3):
        samples = np.array([sigmas[index - k] ** power for k in range(len(weights))])
        exact = (sigmas[index + 1] ** (power + 1) - sigmas[index] ** (power + 1)) / (power + 1)
        assert np.isclose(weights @ samples, exact, atol=1e-10)


def test_euler_weight_is_step() -> None:
    sigmas = shifted_schedule(8)
    weights = hf.step_weights(sigmas, 3, hf.euler_spec())
    assert np.allclose(weights, [sigmas[4] - sigmas[3]])


def test_composite_weights_sum_to_total_interval() -> None:
    sigmas = shifted_schedule(12)
    for spec in (hf.euler_spec(), hf.adams_bashforth_spec(4), hf.wls_spec(6)):
        composite = hf.composite_weights(sigmas, spec)
        assert np.isclose(composite.sum(), sigmas[-1] - sigmas[0], atol=1e-9)


def test_wls_amplifies_white_noise_far_less_than_adams_bashforth() -> None:
    sigmas = shifted_schedule(20)
    ab = hf.white_noise_gain(sigmas, hf.adams_bashforth_spec(4))
    wls = hf.white_noise_gain(sigmas, hf.wls_spec(8))
    euler = hf.white_noise_gain(sigmas, hf.euler_spec())
    assert np.isclose(euler, 1.0)
    assert 1.0 < wls < ab


def test_frequency_response_is_one_at_zero_frequency_and_smaller_for_wls_at_nyquist() -> None:
    sigmas = list(np.linspace(1.0, 0.0, 13))
    frequencies = np.array([0.0, np.pi])
    responses = {}
    for name, spec in (("ab", hf.adams_bashforth_spec(4)), ("wls", hf.wls_spec(8))):
        weights = hf.step_weights(sigmas, 9, spec)
        responses[name] = hf.frequency_response(weights, sigmas[10] - sigmas[9], frequencies)
        assert np.isclose(responses[name][0], 1.0)
    assert responses["wls"][1] < responses["ab"][1]


def test_ridge_shrinks_towards_constant() -> None:
    nodes = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    plain = hf.integral_weights(nodes, -1.0, hf.wls_spec(5, gamma=1.0, ridge=0.0))
    shrunk = hf.integral_weights(nodes, -1.0, hf.wls_spec(5, gamma=1.0, ridge=1e6))
    assert np.sum(shrunk**2) < np.sum(plain**2)


def test_gram_matches_direct_inner_products() -> None:
    generator = torch.Generator().manual_seed(0)
    history = hf.HistoryGram(capacity=4)
    vectors = [torch.randn(3, 5, 5, generator=generator) for _ in range(7)]
    for vector in vectors:
        history.push(vector)
    kept = vectors[-4:][::-1]
    direct = np.array([[float((a * b).sum()) for b in kept] for a in kept])
    assert np.allclose(history.newest_first_gram(), direct, rtol=1e-4, atol=1e-4)


def test_validation_score_matches_direct_residual() -> None:
    generator = torch.Generator().manual_seed(1)
    sigmas = shifted_schedule(12)
    vectors = [torch.randn(2, 4, 4, generator=generator) for _ in range(8)]
    history = hf.HistoryGram(capacity=12)
    for vector in vectors:
        history.push(vector)
    index = 7
    spec = hf.wls_spec(4)
    score = hf.validation_score(history.newest_first_gram(), sigmas, index, spec, origins=2)
    total = 0.0
    for back in range(2):
        target = index - back
        end = target - 1
        nodes = hf.nodes_from_sigmas(sigmas, end, spec.length)
        weights = hf.point_weights(nodes, sigmas[target] - sigmas[end], spec)
        prediction = sum(float(w) * vectors[end - k] for k, w in enumerate(weights))
        total += float(((vectors[target] - prediction) ** 2).sum())
    assert np.isclose(score, total / 2, rtol=1e-5)


def test_selection_prefers_heavy_smoothing_on_noise_and_light_on_smooth_signal() -> None:
    generator = torch.Generator().manual_seed(2)
    sigmas = shifted_schedule(24)
    base = hf.wls_spec(3, gamma=1.0, degree=2)
    smooth_history = hf.HistoryGram(capacity=12)
    noisy_history = hf.HistoryGram(capacity=12)
    for k in range(16):
        s = sigmas[k]
        signal = torch.full((64,), 1.0 + 0.5 * s + 0.2 * s * s)
        smooth_history.push(signal)
        noisy_history.push(signal + 0.5 * torch.randn(64, generator=generator))
    grid = [hf.wls_spec(3, 1.0, 2), hf.wls_spec(8, 1.0, 1), hf.wls_spec(8, 0.85, 1)]
    noisy_choice = hf.select_spec(noisy_history, sigmas, 15, grid, 3, base)
    smooth_choice = hf.select_spec(smooth_history, sigmas, 15, grid, 3, base)
    assert noisy_choice.length == 8
    assert smooth_choice.length in (3, 8)
