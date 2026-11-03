import pytest
import torch

from _bootstrap import module

fq = module("fakequant")


@pytest.fixture
def weights() -> torch.Tensor:
    generator = torch.Generator().manual_seed(0)
    return torch.randn(64, 128, generator=generator).to(torch.bfloat16)


@pytest.mark.parametrize("fmt", ["e4m3", "e5m2"])
def test_fp8_is_idempotent_and_lossy(weights: torch.Tensor, fmt: str) -> None:
    once = fq.fake_fp8(weights, fmt)
    assert once.dtype == weights.dtype
    assert not torch.equal(once, weights)
    assert torch.equal(fq.fake_fp8(once, fmt), once)


def test_fp8_e4m3_is_finer_than_e5m2(weights: torch.Tensor) -> None:
    fine = (fq.fake_fp8(weights, "e4m3").float() - weights.float()).pow(2).mean()
    coarse = (fq.fake_fp8(weights, "e5m2").float() - weights.float()).pow(2).mean()
    assert fine < coarse


@pytest.mark.parametrize("bits,group", [(8, None), (4, 64), (4, 32)])
def test_int_uses_at_most_2_pow_bits_levels_per_group(weights: torch.Tensor, bits: int, group: int | None) -> None:
    result = fq.fake_int(weights, bits, group).float()
    size = weights.shape[-1] if group is None else group
    grouped = result.reshape(-1, size)
    for row in grouped:
        assert len(torch.unique(row)) <= 2**bits - 1


def test_int_error_decreases_with_bits(weights: torch.Tensor) -> None:
    errors = [
        (fq.fake_int(weights, bits, 64).float() - weights.float()).pow(2).mean().item()
        for bits in (3, 4, 6, 8)
    ]
    assert errors == sorted(errors, reverse=True)


def test_smaller_groups_lower_int4_error(weights: torch.Tensor) -> None:
    coarse = (fq.fake_int(weights, 4, 128).float() - weights.float()).pow(2).mean()
    fine = (fq.fake_int(weights, 4, 16).float() - weights.float()).pow(2).mean()
    assert fine < coarse


def test_nvfp4_values_lie_on_scaled_grid(weights: torch.Tensor) -> None:
    result = fq.fake_nvfp4(weights).float()
    blocks = result.reshape(64, 8, 16)
    for block in blocks.reshape(-1, 16)[:20]:
        magnitudes = block.abs()
        top = magnitudes.max()
        if top > 0:
            ratios = (magnitudes / top * 6.0).tolist()
            grid = fq.FP4_GRID
            assert all(min(abs(r - g) for g in grid) < 0.35 for r in ratios)


def test_nvfp4_is_coarser_than_int8_and_fp8(weights: torch.Tensor) -> None:
    def error(tensor: torch.Tensor) -> float:
        return (tensor.float() - weights.float()).pow(2).mean().item()

    assert error(fq.fake_nvfp4(weights)) > error(fq.fake_fp8(weights, "e4m3")) > 0
    assert error(fq.fake_nvfp4(weights)) > error(fq.fake_int(weights, 8, None))


def test_specs_registry_has_reference_and_quantized_variants() -> None:
    assert fq.SPECS["bf16"].weight is None and fq.SPECS["bf16"].activation is None
    assert fq.SPECS["fp8_wa"].activation is not None
    assert fq.SPECS["int4_w"].activation is None


class Tiny(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.blocks = torch.nn.ModuleList([torch.nn.Linear(32, 32), torch.nn.Linear(32, 32)])
        self.head = torch.nn.Linear(32, 4)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        for block in self.blocks:
            x = block(x)
        return self.head(x)


def test_quantized_weights_apply_and_restore() -> None:
    torch.manual_seed(0)
    model = Tiny()
    sample = torch.randn(5, 32)
    reference = model(sample).detach().clone()
    store = fq.QuantizedWeights(model, prefix="blocks.")
    assert set(store.layers) == {"blocks.0", "blocks.1"}
    store.apply(fq.SPECS["int4_wa8"])
    perturbed = model(sample).detach()
    assert not torch.allclose(perturbed, reference)
    assert len(store.handles) == 2
    store.release()
    assert torch.equal(model(sample).detach(), reference)
    assert store.handles == []


def test_head_is_never_quantized() -> None:
    model = Tiny()
    head_before = model.head.weight.detach().clone()
    store = fq.QuantizedWeights(model, prefix="blocks.")
    store.apply(fq.SPECS["int4_w"])
    assert torch.equal(model.head.weight, head_before)
