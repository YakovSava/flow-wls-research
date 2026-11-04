# Reddit

Правила перед публикацией: прочитайте правила каждого сабреддита (самореклама, обязательные теги, дни для проектов). Картинки прикладывайте файлами из `figures/` (для r/comfyui и r/StableDiffusion главные: `grid_anima_fur_cfg5.jpg` и `grid_krea2_face_cfg1.jpg`). Ссылку на препринт и репозиторий лучше дать в тексте и продублировать в первом комментарии, если сабреддит режет посты со ссылками. Перед публикацией сделайте `git push`.

---

## 1. r/comfyui

**Title:** INT8 isn't the problem, the sampler is: I measured samplers on INT8 flow models at 8-16 steps and added flow_ab2 / flow_ab3 to the sampler list

**Body:**

I wanted to know whether multistep samplers get hurt by INT8 models, because the common advice says they do. I measured it on real INT8 checkpoints (Flux3-Klein, Krea 2, Moss-Image) and on Anima, at 8-24 steps and different CFG. Short version:

- **INT8 itself is nearly harmless.** The error of ComfyUI's INT8 kernels is white noise (no correlation between steps), 1.3% of the velocity at CFG 1 and 5.7% at CFG 4. On the final image it comes to about LPIPS 0.014-0.029 against the same weights in bf16 (converged solutions).
- **The sampler matters much more than INT8.** Order-3 Adams-Bashforth and my own earlier Flow-WLS-8 idea broke the image at 8 steps on Anima, and WLS-8 did on Flux3-Klein (grids attached); by the error metrics order 4 and WLS-8 were never the best at 12 steps or fewer in any of the four models. I wrote that earlier idea myself and it lost, so I am saying so.
- **What worked:** with CFG 3+ a 2nd-order Adams-Bashforth (`flow_ab2`) beat Euler in all 12 settings I tested on Anima, and `dpmpp_2m` is better than Euler from about 16 steps. For distilled models at CFG 1 (Flux3-Klein, Krea 2) a 3rd-order one (`flow_ab3`) gave the lowest error among the options in the dropdown. For Flux3-Klein at 12 steps all of Euler / DPM++ 2M / AB-2 / AB-3 look the same to my eye, so there is no reason to switch there.
- **Where you can see it:** on a texture-heavy prompt (Anima, 8 steps) Euler left almost black noise (LPIPS 0.89 to the many-step image), DPM++ 2M (0.35) and AB-2 (0.42) gave a finished picture. On Krea 2 at 12 steps Euler gave airbrushed skin, AB-2 / DPM++ 2M / AB-3 brought pores and freckles back.

The custom node adds `flow_ab2`, `flow_ab3`, `flow_ab4` to the normal `sampler_name` dropdown (KSampler, KSamplerSelect...), plus a "Flow Easy Sampler" node with two choices. Install: put the folder in `custom_nodes` and restart. Works only with flow-matching models (Anima, Flux3, Krea 2, Moss); I did not test SDXL-type models.

What this is not: LPIPS is a distance to a many-step image, not a beauty score, and I did not run a human preference test. It is 4 prompts and 4 models, one seed per picture, no seed picking. Moss-Image has no converged reference, so only large effects are trustworthy there.

Repo with all tables and the image grids: https://github.com/YakovSava/flow-wls-research
Write-up: https://doi.org/10.5281/zenodo.23939696

---

## 2. r/MachineLearning

**Title:** [R] Real INT8 kernels add white noise to flow-matching samplers; low-order Adams-Bashforth vs Euler/DPM++ under CFG, and a negative result for our own regularized multistep sampler

**Body:**

**Question.** Multistep ODE samplers are said to be especially sensitive to quantization noise because they reuse past (noisy) velocity evaluations, and a regularized multistep rule (our earlier Flow-WLS) was expected to damp it. We tested both claims.

**Setup.** Flow-matching image models: Anima (bf16, plus simulated FP8/INT8/INT4/NVFP4), and real INT8 checkpoints run by ComfyUI's INT8 kernels (Flux3-Klein, Krea 2 with ConvRot, Moss-Image). 4 prompts, 2-3 seeds, 8-24 steps, CFG 1-5, reference = many-step solution of the same model. Hypotheses H1-H15 were written down before the corresponding runs (six before the first experiments, nine before the follow-up); paired bootstrap intervals against Euler. For Flux3 we compared the real INT8 path with the same weights dequantized to bf16 (isolates kernel/activation error from weight rounding).

**Results.**
1. Real INT8 error is white in time (lag-1 correlation -0.001; realised accumulation equals the white-noise prediction), 1.3% of the velocity norm at CFG 1, 5.7% at CFG 4. Effect on the final latent <= ~0.02 (LPIPS 0.014-0.029 between converged INT8 and bf16-dequantized images). Simulated 8-bit formats were already nearly white; 4-bit weight formats are correlated and smooth.
2. White-noise gain relative to Euler: AB-2 1.06, AB-3 1.21, AB-4 1.97. AB-4 and long-window Flow-WLS were never the best choice at <= 12 steps.
3. The best simple rule depends on guidance: AB-2 beat Euler in 12/12 (CFG, steps) cells on Anima; DPM++ 2M from 16-24 steps; AB-3 for distilled models at CFG 1. The pattern reproduced on a second architecture.
4. Mechanism, measured: the guided velocity is trend plus a step-to-step uncorrelated jitter of ~1% (CFG 1), ~4% (CFG 3), 6-7% (CFG 5) of the norm; the guidance term s(v_c - v_u) is redrawn at every step.
5. A constant-weight linear history filter fitted to the data (leave-one-unit-out) improves on the best existing rule by at most 3.4%, so we do not claim a new sampler.
6. Registered hypotheses that failed: H1 (error correlated for every format), H14 (AB-4 hurt by INT8 more than WLS-8 in real kernels), part of H8, H10 (narrowly).

**Limitations.** LPIPS/latent distance to a reference is not preference; no human study. Four prompts, four models. The reference does not converge for Moss-Image (wls5 at 64 vs 160 steps differ by 32%) and only roughly for Flux3 at CFG 4 (20-34%). Moss and Krea 2 only in the quantized mode. Weight rounding of the INT8 checkpoints relative to an unknown bf16 original was not measured. AB-2 / DPM++ 2M were added to part of the runs post hoc (marked). No epsilon-prediction models. AB-2 is of course not new; the contribution is the measurement and the negative result.

Code, tables, figures: https://github.com/YakovSava/flow-wls-research
Preprint: https://doi.org/10.5281/zenodo.23939696

---

## 3. r/StableDiffusion

**Title:** Euler vs DPM++ 2M vs AB-2 vs AB-3 at 8 / 12 / 16 steps on flow models (Anima, Krea 2, Flux3-Klein INT8): where the sampler visibly matters

**Body:**

Grids attached (rows: Euler, DPM++ 2M, AB-2, AB-3, WLS-8; columns: 8 / 12 / 16 steps and a many-step reference; the number on a tile is LPIPS to the reference, lower is closer; one prompt and one seed per picture, no seed picking).

What I see:
- Anima, texture-heavy prompt, 8 steps: Euler leaves almost black noise, DPM++ 2M and AB-2 give a complete picture. At 16 steps Euler is still darker and less detailed than DPM++ 2M / AB-3 / AB-2.
- Krea 2 INT8 at 12 steps: Euler = smooth airbrushed skin, AB-2 / DPM++ 2M / AB-3 bring pores and freckles back.
- Flux3-Klein INT8 at 12 steps: Euler, DPM++ 2M, AB-2 and AB-3 are the same picture to my eye. Only WLS-8 (my own earlier idea) breaks the face at 8 steps.
- INT8 itself added almost nothing in these tests; the sampler choice changed the result far more.

Honest limits: no preference test, four prompts, four models, flow-matching models only (not SDXL-type). Tables, code and the ComfyUI node (`flow_ab2`, `flow_ab3` in the normal sampler list): https://github.com/YakovSava/flow-wls-research , write-up: https://doi.org/10.5281/zenodo.23939696. Code and analysis were prepared with an AI assistant.

---

## Заготовленные ответы на вероятные возражения

Отвечать спокойно и по существу, соглашаться там, где критик прав. Все пункты ниже подтверждаются файлами репозитория.

1. **"LPIPS это не качество."** Согласны. Это расстояние до картинки, полученной за много шагов; так и написано. Слепого теста на людях нет, поэтому мы не утверждаем, что картинки "красивее", только что на малом числе шагов они ближе к пределу и что некоторые сэмплеры видимо ломают изображение.
2. **"AB-2 не новый, это классика."** Да. Вклад в измерении: как ведут себя эти методы на guided и INT8 flow-моделях, какой шум у реальных INT8-ядер, и в отрицательном результате для нашего собственного Flow-WLS. Мы не заявляем нового метода.
3. **"4 промпта это ничто."** Согласны, это указано в ограничениях. Поэтому просим промпты и модели, где результат ломается; код и таблицы открыты, чтобы можно было перепроверить.
4. **"Почему не UniPC / DPM++ 3M / SDE-варианты?"** Не тестировали. Проверены Euler, AB-2/3/4, WLS-5/8, динамический выбор, DPM++ 2M, Heun.
5. **"Это написал ИИ."** Код и анализ делались вместе с ИИ-ассистентом, это указано. Числа берутся из файлов в `results/` и воспроизводятся скриптами; ошибки, которые мы нашли у себя по ходу (например, что AB-2 вначале не входил в сравнение и из-за этого "Euler лучший" был неверным), записаны в README.
6. **"Работает ли на SDXL?"** Нет данных. Проверялись только flow-matching модели (Anima, Flux3, Krea 2, Moss).
7. **"Ваш прежний препринт утверждал обратное."** Да. Новые измерения не подтвердили его как рекомендацию для малого числа шагов; это явно написано, и README содержит исправленные выводы.
8. **"Вы не измерили ошибку самих INT8-весов."** Верно, это в ограничениях. Измерена ошибка INT8-ядер и активаций относительно тех же весов в bf16, а не относительно неизвестного bf16-оригинала.
9. **"Подбирали seed?"** Нет. Использовались заранее фиксированные seed 42 и 1337 (и 7 в одном эксперименте), картинки показаны для seed 42.
10. **"А скорость?"** Все методы AB-k используют ту же одну оценку сети на шаг, что и Euler (без дополнительных вызовов модели); накладные расходы на историю пренебрежимо малы. Heun при равном числе вызовов сети проигрывал.
11. **"Другие шедулеры, ancestral, hires fix?"** Не охвачено; расписание сигм одно на модель ("normal" для Anima, "simple" для остальных).
