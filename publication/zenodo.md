# Zenodo: метаданные и описание

DOI: 10.5281/zenodo.23939696

## Поля формы

| Поле | Значение |
| --- | --- |
| Resource type | Publication / Preprint |
| Title | Flow-WLS under quantization: low-order multistep samplers for guided and INT8 flow-matching models |
| Publication date | 2026-11-04 |
| Version | 1.0 |
| Language | English |
| Authors | Savelev, Iakov (GitHub: YakovSava). Второго автора добавьте сами: Yuzvynsky, Yehor, если он указывается как соавтор |
| License | Creative Commons Attribution 4.0 (текст); код в репозитории под MIT |
| Keywords | flow matching; ODE sampler; Adams-Bashforth; DPM++ 2M; classifier-free guidance; quantization; INT8; ComfyUI; diffusion models; negative result |
| Related identifiers | "Continues": 10.5281/zenodo.23337579 (DOI). "Is supplemented by": https://github.com/YakovSava/flow-wls-research (URL). "Is supplemented by": https://github.com/YakovSava/adaptive-step-samplers (URL, по желанию) |
| Software | Если подключена интеграция GitHub-Zenodo, выпуск (release) репозитория создаст архив кода автоматически |

Перед публикацией выполните `git push` в репозиторий: сейчас коммиты только локальные, и ссылки на GitHub в текстах заработают после этого.

## Description (HTML для вставки в режиме Source)

```html
<p><b>Summary.</b> We measured how multistep ODE samplers behave on flow-matching image models at 8-24 steps, when the model is quantized to INT8 and when classifier-free guidance (CFG) is used. Our earlier preprint (<a href="https://doi.org/10.5281/zenodo.23337579">10.5281/zenodo.23337579</a>) proposed Flow-WLS, a regularized multistep sampler, and the working expectation was that it would damp quantization noise. The measurements do not support that expectation, and this record reports the results as they are, including the refuted hypotheses.</p>

<p><b>Main results.</b></p>
<ul>
<li>The error of real INT8 kernels (ComfyUI, Flux3-Klein) is white in time: lag-1 correlation of the velocity error -0.001. Its size is 1.3% of the velocity norm at CFG 1 and 5.7% at CFG 4 (a factor of 4.36). The effect on the final latent is about 0.02 or less, and the LPIPS distance between the converged images of the INT8 kernels and of the same weights dequantized to bf16 is 0.014 (CFG 1) and 0.029 (CFG 4).</li>
<li>The choice of sampler changes the final error by 0.05-0.8, quantization by 0.02 at most.</li>
<li>Adams-Bashforth of order 4 and the long-window Flow-WLS-8 were not the best choice at 12 steps or fewer in any tested model. White-noise gain relative to Euler: 1.06 (AB-2), 1.21 (AB-3), 1.97 (AB-4).</li>
<li>The best simple rule depends on guidance. At CFG 3 and above AB-2 beats Euler in 12 of 12 (CFG, budget) cells on Anima, and DPM++ 2M overtakes Euler from 16-24 steps; for distilled models without guidance (Flux3-Klein, Krea 2 at CFG 1) AB-3 (together with the dynamic rule) gave the lowest error.</li>
<li>Measured mechanism: the guided velocity is a smooth trend plus a jitter that is uncorrelated from step to step, about 1% of the norm at CFG 1, 4% at CFG 3 and 6-7% at CFG 5. The guidance term is redrawn at every step.</li>
<li>A constant-weight linear history filter fitted to the data improves on the best existing rule by at most 3.4% (leave-one-unit-out), so no new sampler of the Flow-WLS class is justified.</li>
</ul>

<p><b>Setup.</b> Anima (bf16 with simulated FP8/INT8/INT4/NVFP4), Flux3-Klein INT8, Krea 2 INT8 (ConvRot), Moss-Image INT8; 4 prompts, 2-3 seeds, 8-24 steps, CFG 1-5. Hypotheses H1-H15 were registered in the README before the corresponding measurements (six before the first experiments, nine before the follow-up); paired bootstrap intervals are reported against Euler. For Flux3 the real INT8 path (Q) is compared with the same weights dequantized to bf16 (D).</p>

<p><b>Software.</b> The code adds <code>flow_ab2</code>, <code>flow_ab3</code> and <code>flow_ab4</code> to the standard ComfyUI sampler list and a one-choice node "Flow Easy Sampler". Experiments, tables (<code>results/</code>) and image grids (<code>figures/</code>) are in the repository: <a href="https://github.com/YakovSava/flow-wls-research">github.com/YakovSava/flow-wls-research</a>.</p>

<p><b>Limitations.</b> LPIPS measures distance to a many-step image, not preference; no human preference test was done. Four prompts and four models; one seed per displayed image, no seed selection. The "converged" reference does not converge for Moss-Image and only roughly (20-34%) for Flux3 at CFG 4, so only large effects are interpreted there. Moss-Image and Krea 2 were measured in Q mode only. The rounding error of the INT8 weights against an unknown bf16 original was not measured. AB-2 and DPM++ 2M were added to part of the experiments after the first results (marked in the README). Models with epsilon prediction (SDXL-like) were not tested.</p>
```
