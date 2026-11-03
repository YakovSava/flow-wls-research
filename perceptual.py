import numpy as np
import torch
import torch.nn.functional as functional

SSIM_WINDOW: int = 11
SSIM_SIGMA: float = 1.5
SSIM_K1: float = 0.01
SSIM_K2: float = 0.03
TILE: int = 32
TILE_OVERLAP: int = 8


def gaussian_window(channels: int, device: torch.device) -> torch.Tensor:
    coordinates = torch.arange(SSIM_WINDOW, dtype=torch.float32) - (SSIM_WINDOW - 1) / 2.0
    kernel = torch.exp(-(coordinates**2) / (2 * SSIM_SIGMA**2))
    kernel = kernel / kernel.sum()
    window = torch.outer(kernel, kernel)
    return window.expand(channels, 1, SSIM_WINDOW, SSIM_WINDOW).to(device)


@torch.no_grad()
def ssim(first: torch.Tensor, second: torch.Tensor) -> float:
    x = first.float().permute(0, 3, 1, 2)
    y = second.float().permute(0, 3, 1, 2)
    channels = x.shape[1]
    window = gaussian_window(channels, x.device)

    def blur(value: torch.Tensor) -> torch.Tensor:
        return functional.conv2d(value, window, padding=SSIM_WINDOW // 2, groups=channels)

    mean_x, mean_y = blur(x), blur(y)
    var_x = blur(x * x) - mean_x**2
    var_y = blur(y * y) - mean_y**2
    covariance = blur(x * y) - mean_x * mean_y
    c1, c2 = SSIM_K1**2, SSIM_K2**2
    score = ((2 * mean_x * mean_y + c1) * (2 * covariance + c2)) / (
        (mean_x**2 + mean_y**2 + c1) * (var_x + var_y + c2)
    )
    return float(score.mean())


def to_lpips_input(images: torch.Tensor) -> torch.Tensor:
    return images.float().permute(0, 3, 1, 2) * 2.0 - 1.0


def decode(vae, latent: np.ndarray, dimensions: int = 3) -> torch.Tensor:
    tensor = torch.from_numpy(latent).float()[None]
    if dimensions == 3:
        tensor = tensor[:, :, None]
    with torch.inference_mode():
        images = vae.decode_tiled(tensor, tile_x=TILE, tile_y=TILE, overlap=TILE_OVERLAP)
    return images.reshape(-1, *images.shape[-3:]).clamp(0.0, 1.0).float().clone()
