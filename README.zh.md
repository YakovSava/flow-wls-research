# Flow-WLS 与量化：INT8 和少步数下采样器到底发生了什么

**语言：** [English](README.md) · [Русский](README.ru.md) · **中文** · [Марий](README.mhr.md)

本文是摘要。完整协议（测量前登记的假设、全部表格和置信区间）见英文版 [README.md](README.md)。预印本：[10.5281/zenodo.23939696](https://doi.org/10.5281/zenodo.23939696)。上一项工作：[Flow-WLS，10.5281/zenodo.23337579](https://doi.org/10.5281/zenodo.23337579)。

## 简要结论

我们研究了多步采样器（Adams-Bashforth、我们此前提出的 Flow-WLS、DPM++ 2M）在 8-24 步、模型被量化为 INT8、以及不同 CFG 下的表现。事先的预期是：多步方法对量化噪声特别敏感，而 Flow-WLS 的正则化可以平滑它。测量结果并非如此。

1. **INT8 量化模型不必担心。** ComfyUI 真实的 INT8 内核（Flux3-Klein）产生的是时间上的白噪声：相邻步误差的相关系数为 -0.001。其大小在 CFG 1 时为速度范数的 1.3%，CFG 4 时为 5.7%。对最终潜变量的影响约为 0.02 或更小；INT8 内核与同一权重解压为 bf16 的收敛解之间，LPIPS 距离为 0.014（CFG 1）和 0.029（CFG 4）。
2. **选择采样器的影响大于量化。** 更换采样器会使误差变化 0.05-0.8，而 INT8 至多增加 0.02。
3. **“更高级”不等于“更好”。** 4 阶 Adams-Bashforth 和我们此前的 Flow-WLS-8 在 ≤12 步时，在所有测试模型中都不是最佳选择。AB-4 将白噪声放大近一倍（系数 1.97），AB-3 放大 21%，AB-2 放大 6%。
4. **最佳的简单方法取决于 CFG。** CFG 3 及以上时，AB-2 在 Anima 的全部 12 个测试组合（CFG 1/3/5 × 8/12/16/24 步）中都优于 Euler；DPM++ 2M 从 16-24 步起超过 Euler。对于不使用 CFG 的蒸馏模型（CFG 1 的 Flux3-Klein、Krea 2），AB-3 更好。
5. **原因。** 网络输出在步与步之间存在抖动：CFG 1 约为范数的 1%，CFG 3 约 4%，CFG 5 约 6-7%。CFG 项 `s·(v_c − v_u)` 在每一步都会被重新“抽取”。权重较大的方法会放大这种抖动。
6. **不需要新的 flow_wls 类采样器。** 根据数据拟合的线性历史滤波器，最多只比现有最佳规则好 3.4%。

## 测量内容

- 模型：Anima（bf16，另有 FP8/INT8/INT4/NVFP4 模拟）、Flux3-Klein INT8、Krea 2 INT8（ConvRot）、Moss-Image INT8。
- 4 个提示词，2-3 个种子，8-24 步，CFG 1-5。对 Flux3，将 Q（INT8 内核）与 D（相同权重解压为 bf16）进行比较。
- 指标：潜变量相对误差（总体、几何、细节）、SSIM、LPIPS、观测收敛阶、误差结构（步间相关、频谱）、相对 Euler 的配对置信区间。
- 假设 H1-H15 在相应测量之前写入 README（前 6 个在最初实验之前，后 9 个在后续实验之前）；被否定的假设仍保留在文中。

## 使用方法

1. 将文件夹复制到 `ComfyUI/custom_nodes/`（或 `git clone https://github.com/YakovSava/flow-wls-research`），然后重启 ComfyUI。
2. 在常规的 `sampler_name` 列表（KSampler、KSampler Advanced、KSamplerSelect）中会出现 **`flow_ab2`、`flow_ab3`、`flow_ab4`**。
3. 另有节点 **Flow Easy Sampler (low steps)**，只需二选一：“Model uses CFG 3 or higher”（AB-2）或 “Distilled model, CFG 1”（AB-3）。

如何选择：

| 情形 | 采样器 |
| --- | --- |
| 普通模型，CFG 3 及以上 | `flow_ab2`；16 步以上也可用 `dpmpp_2m` |
| 蒸馏模型，CFG 1 | `flow_ab3`（对 Flux3-Klein，肉眼看与 Euler 没有差别） |
| 任何模型，少于 12 步 | 不要用 `flow_ab4` 或 Flow-WLS 的长窗口 |

`flow_ab4` 仅供实验。这些采样器只适用于 flow 预测的模型（Anima、Flux3、Krea 2、Moss），未在 SDXL 类模型上测试。

## 图片

见 `figures/`：`grid_anima_fur_cfg5.jpg`（最直观）、`grid_krea2_face_cfg1.jpg`、`grid_flux3_face_cfg1.jpg`、`grid_anima_face_cfg5.jpg`。每个图块上标注与参考图的 LPIPS（越小越接近）。

- Anima，纹理类提示词，8 步：Euler 几乎只剩黑色噪声（LPIPS 0.89），DPM++ 2M（0.35）和 AB-2（0.42）能得到完整图像。16 步时 Euler 为 0.34，对比 DPM++ 2M 0.20、AB-3 0.21、AB-2 0.23。
- Krea 2，12 步：Euler 的皮肤像“塑料”（0.34）；AB-2（0.30）、DPM++ 2M（0.27）、AB-3（0.21）恢复了毛孔和雀斑。
- Flux3-Klein，12 步：Euler、DPM++、AB-2、AB-3 在视觉上相同（0.15）。只有 WLS-8 在 8 步时会出问题（0.34）。

## 局限

- LPIPS 衡量的是与多步结果的距离，不是“好不好看”。没有做过人类盲测。
- 只测试了 4 个提示词和 4 个模型；每张图只用一个种子，没有挑选最佳种子。
- Moss-Image 没有“收敛”的参考解（解随步数继续变化），因此只有较大的效应可信。Flux3 在 CFG 4 时参考解的收敛程度为 20-34%。
- Moss 和 Krea 2 只测了 Q 模式：Moss 的 D 模式慢得不实用（约 50 秒/次评估），Krea 2 的 D 模式显存放不下；内核效应只在 Flux3 上测得。
- INT8 权重本身相对未知 bf16 原模型的舍入误差没有测量。
- AB-2 和 DPM++ 2M 是在看到初步结果后加入部分实验的（英文 README 中已标明）。
- 代码和分析由作者与 AI 助手（Claude）共同完成；所有数字均可由仓库复现。

## 复现

需要 ComfyUI 及其 Python 环境。模型路径写在 `harness.py` 的 `MODELS` 中，需按自己的安装位置修改。

```
python run_sweep.py --model anima --modes bf16 --cfgs 1 3 5 --seeds 42 1337 --methods euler ab2 ab3 ab4 wls5 wls8 dynamic dpmpp2m heun --budgets 8 12 16 24 --check-convergence --name e4_anima
python run_sweep_perceptual.py --model anima --modes bf16 --cfgs 1 3 5 --seeds 42 1337 --methods euler ab2 ab3 ab4 wls5 wls8 dynamic dpmpp2m heun --budgets 8 12 16 24 --name e4_anima
python make_image_grids.py
```

测试：`python -m pytest tests`。所有实验的表格在 `results/`。

## 引用与许可

Iakov Savelev（Яков Савельев），2026。Flow-WLS and quantization。Zenodo，[10.5281/zenodo.23939696](https://doi.org/10.5281/zenodo.23939696)。MIT 许可证。
