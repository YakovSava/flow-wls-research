# Flow-WLS under Quantization: Does a Multistep Sampler Survive FP8 / INT4 Velocity Errors?

> **Status: protocol registered, experiments running.** This section was written on 2026-11-03
> *before* any real-model measurement. Results are appended below it as they come in and nothing
> above the line "Results" is edited afterwards except to fix typos.

Follow-up to [Flow-WLS](https://doi.org/10.5281/zenodo.23337579) (regularized multistep integration,
`flow_wls_L`, d = 2, memory decay gamma = 0.85) and to the earlier
[adaptive-step-samplers](https://github.com/YakovSava/adaptive-step-samplers) /
`flow-sde-research` work. Same conventions: no extra network evaluations, paired comparisons with
bootstrap intervals, negative results reported as such.

## Question

Quantizing weights and activations (FP8, INT8, INT4, NVFP4) perturbs the velocity field the sampler
integrates: `v_q(x, t) = v(x, t) + e(x, t)`. Two claims are common:

1. Multistep solvers are *especially* sensitive, because they reuse past (erroneous) evaluations.
2. A regularized multistep method such as Flow-WLS can damp the "high-frequency" quantization noise,
   and a *dynamic* regularization can do it better than a fixed one.

Both statements implicitly assume that `e` behaves like noise that is independent from step to step.
This work first **measures what `e` actually looks like along a sampling trajectory**, and only then
asks which sampler copes best.

## Methods (summary)

* `history_filter.py` - one family of explicit multistep rules, `x_{n+1} = x_n + sum_k w_k v_{n-k}`,
  where the weights come from a weighted least-squares polynomial fit of the velocity history
  (`FilterSpec(length, gamma, degree, ridge)`). Adams-Bashforth of order p is the special case
  `length = p, degree = p - 1, gamma = 1` (interpolation); Flow-WLS is `degree = 2, gamma = 0.85`;
  Euler is `length = 1`. All samplers share one code path (`samplers.sample_history`), so
  differences between them are differences of weights only.
* **Dynamic regularization (new).** At every step the sampler chooses `(length, gamma, degree)` from
  a fixed grid by rolling-origin validation: each candidate predicts the last three velocities from
  the history that precedes them, and the candidate with the smallest squared prediction error wins.
  Because the score is a quadratic form in the history, it needs only the Gram matrix of the last
  11 velocity fields (`HistoryGram`), i.e. a few inner products per step and **zero extra network
  evaluations**.
* `fakequant.py` - simulated quantization of the DiT block linears (`blocks.*`): FP8 E4M3 per tensor,
  INT8 per output channel / per token, INT4 with group 64, NVFP4 (E2M1, block 16, FP8 block scales);
  activations quantized dynamically on the input of every quantized linear. Embedders, the final
  layer, the text path and norms stay in bf16. This is *numerical simulation*, not a hardware kernel.
* Model: Anima (`anima_aestheticV11`, bf16, 576x768, CFG 5, 4 prompt classes x 3 seeds), the only
  checkpoint on this machine that is not already quantized.

## Pre-registered hypotheses

All are about the *relative* final-latent error `||x - x_ref|| / ||x_ref||`, where `x_ref` is the
unquantized model integrated with 40-60 steps; pairs are (prompt, seed).

| # | Hypothesis | Counts as supported if |
| --- | --- | --- |
| H1 | The quantization error `e_n = v_q(x_n) - v(x_n)` is **temporally correlated**, not white | median lag-1 cosine similarity of `e_n` along the trajectory > 0.5 for every format |
| H2 | Because of H1, the realised accumulation of `e` by a multistep rule is **close to the Euler value and far below** the white-noise prediction | realised/predicted ratio of the accumulated error < 0.7 for AB-4 |
| H3 | Aggressive formats (INT4, NVFP4, activation-quantized) hurt Adams-Bashforth-4 more than Euler and WLS-8 at 8-12 steps | extra error of AB-4 from quantization exceeds that of WLS-8, 95% bootstrap interval excludes 0 |
| H4 | WLS-8 has lower total error than AB-4 under every quantization format at 8 and 12 steps | interval of the paired difference excludes 0 in the WLS-8 favour in a majority of cells |
| H5 | The dynamic rule is **no better** than the best fixed WLS setting (expected null), but is never much worse | interval of (dynamic - best static) includes 0 or is positive in most cells; regret <= 10% |
| H6 | For INT4-class formats the quantization floor (error of the *converged* quantized model against the full-precision one) is larger than the discretization error of a 12-step sampler | floor / discretization error > 1 |

Prior expectation, written down before running: H1 and H2 probable, H3 half-true (only for
activation noise), H4 probable, H5 null.

Two controls precede the real-model runs: a synthetic flow with exactly known velocity (below) and
unit tests (`tests/`, 45 tests).

## Synthetic control (2-mode Gaussian mixture, D = 256, shift-3 schedule, 32 trials)

The exact flow-matching velocity of a Gaussian mixture is closed-form, so the integration error can be
separated from everything else. Three velocity-error models of the same relative size `level`:
`white` (fresh i.i.d. noise per evaluation), `smooth` (a fixed random linear map of `v`, a stand-in
for a weight perturbation) and `rounding` (rounding of `v` onto a coarse grid with fixed dithers).

Relative final error, selected cells (`results/synthetic.json` has all of them):

| error model | level | NFE | euler | ab3 | ab4 | wls5 | wls8 | dynamic |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| none | 0 | 12 | 0.208 | 0.118 | **0.113** | 0.124 | 0.132 | 0.120 |
| white | 0.1 | 12 | 0.210 | 0.132 | 0.217 | **0.129** | 0.137 | 0.139 |
| white | 0.2 | 12 | 0.221 | 0.167 | 0.381 | **0.143** | 0.151 | 0.154 |
| white | 0.2 | 20 | 0.143 | 0.071 | 0.104 | 0.071 | **0.067** | **0.067** |
| smooth | 0.2 | 12 | 0.261 | 0.188 | **0.186** | 0.191 | 0.196 | 0.188 |
| rounding | 0.2 | 12 | 0.226 | 0.173 | 0.397 | **0.156** | 0.161 | 0.166 |

What this says (toy problem, not the real model):

* AB-4 is destroyed by white or rounding-like errors (error x3 at level 0.2) - the concern in the
  question is real for that kind of error.
* For the `smooth` (bias-like) error **no sampler helps**: ranking stays what it is without noise,
  AB-4 is even slightly best. A history filter cannot remove an error that is the same at every step.
* The dynamic rule tracks the better of "AB-like" and "WLS-like" but does not beat the best
  fixed choice. Its grid was chosen on this toy only (one of four candidate grids; a degree-1 option
  with ridge, which looked attractive for noise, was *worse* because it biases the integral) and
  frozen before the real-model runs.

So the decisive empirical question is which of the three error types quantization produces. That is
experiment E1.

## Experiments

* **E1 - structure of the quantization error.** Integrate the bf16 model for 20 steps, store `x_n`,
  then re-evaluate the *same* states with each quantized model. `e_n = v_q(x_n) - v(x_n)`. Report
  relative size, lag-1/2 cosine, second-difference ratio (1 for white, ~0 for smooth), spatial
  high-frequency share, and the *accumulated response*: the norm of `sum_j c_j e_j` (c = composite
  quadrature weights of the sampler) relative to Euler, against the white-noise prediction.
* **E2 - end-to-end.** Samplers `euler, ab3, ab4, wls5, wls8, dynamic` x budgets 8 and 12 x
  quantization formats x (prompt, seed) pairs; error against the bf16 reference and against the
  quantized model's own converged solution.

## Results

### E1 - structure of the quantization error (8 units: 4 prompts x 2 seeds, 20 steps)

![error structure](figures/error_structure.png)

Mean over units; "real/white" is the accumulated error of the sampler relative to Euler, measured on the
actual `e_n` (real) and predicted if the same `e_n` were independent between steps (white).
Statistics exclude the final evaluation (sigma ~ 0.01), whose relative error is 40-70% for every format
but which only feeds an Euler jump of size sigma.

| format | rel. size of `e` | lag-1 cos | lag-2 cos | ab4 real/white | wls5 real/white | wls8 real/white |
| --- | --- | --- | --- | --- | --- | --- |
| fp8_w (E4M3 weights) | 0.056 | 0.175 | 0.106 | 1.78 / 2.28 | 1.20 / 1.31 | 1.16 / 1.23 |
| fp8_wa (E4M3 W+A) | 0.100 | 0.132 | 0.083 | 2.12 / 2.39 | 1.30 / 1.38 | 1.20 / 1.27 |
| int8_wa (W per channel, A per token) | 0.082 | 0.076 | 0.040 | 2.34 / 2.42 | 1.37 / 1.39 | 1.25 / 1.27 |
| int4_w (group 64) | 0.156 | 0.579 | 0.426 | 1.15 / 2.23 | 1.07 / 1.30 | 1.07 / 1.24 |
| int4_wa8 | 0.173 | 0.464 | 0.335 | 1.37 / 2.33 | 1.11 / 1.35 | 1.10 / 1.26 |
| nvfp4_w | 0.196 | 0.499 | 0.319 | 1.18 / 2.01 | 1.10 / 1.26 | 1.12 / 1.25 |

Verdicts on the pre-registered hypotheses:

* **H1 (lag-1 cosine > 0.5 for every format): refuted as stated.** It holds only for INT4 weights
  (0.58) and, on the border, NVFP4 (0.50). For FP8 and INT8 the error is nearly uncorrelated between
  consecutive steps (0.08-0.18). The prior expectation was wrong for 8-bit formats.
* **H2 (realised/white < 0.7 for AB-4): split by bit width.** 4-bit weights: 0.52 (INT4), 0.59
  (INT4 + A8), 0.59 (NVFP4) - supported. 8-bit: 0.78 (FP8 weights), 0.89 (FP8 W+A), 0.97 (INT8 W+A) -
  not supported; there the error is white-like and AB-4 amplifies it 1.8-2.3 times relative to Euler.
* The "high-frequency noise" picture holds in *step* space for 8-bit formats only. In *space* the
  error spectrum is close to the spectrum of the velocity itself for 8-bit formats (share of energy
  above half the Nyquist radius 0.43-0.46 versus 0.42 for `v`) and *smoother* than `v` for 4-bit
  formats (0.24-0.28): 4-bit weight rounding produces structured, low-frequency error, not noise.
* Relative size of `e` is large because it includes classifier-free guidance (cfg 5 multiplies the
  difference between conditional and unconditional errors).

Theory for white errors (`results/theory.md`, shift-3 schedule): accumulation gain relative to Euler at
N = 12 / 20 steps is 2.31 / 1.72 for AB-4, 6.0 / 3.5 for AB-5, 19.8 / 9.0 for AB-6 and
**1.19 / 1.12 for WLS-8**. Flow-WLS therefore does not *filter* white errors (the gain is above 1; the
frequency response of WLS-8 has a 1.77x peak at a quarter of the sampling frequency); what it does is
keep the amplification bounded, where interpolating Adams-Bashforth does not. The formulation
"noise suppression by averaging" in the preprint (`sum |w|` 0.066 against 0.54 for AB-6) is a
comparison with AB-6, not with Euler, and should be read in that sense.


### E2 - end-to-end on Anima (12 units: 4 prompts x 3 seeds, 10 and 16 steps)

**Status update (2026-11-03, after E2/E3):** all experiments of the protocol have finished. Full tables:
`results/end_to_end_10_16.md`, `results/perceptual_10_16.md`; raw latents are not versioned (`dumps/`).

![end to end](figures/end_to_end_10_16.png)

Bars: relative RMS error of the final latent against the converged bf16 solution (wls5, 96 steps), mean
over 12 units, whiskers are standard errors. Black ticks: the quantization floor (converged quantized
model against converged bf16). AB-4 at 10 steps is clipped by the axis (true values 1.3-1.9).

Deviation from the registered protocol: the budgets are **10 and 16 steps**, not the 8 and 12 written in
H3/H4. The verdicts below are therefore about 10 and 16 steps. The reference is converged: two
independent 96-step solvers (ab3 and wls5) differ by 1.7% on the one pair where both were run.

Total error, mean of 12 units (selected columns):

| steps | method | bf16 | fp8_w | fp8_wa | int8_wa | int4_w | int4_wa8 | nvfp4_w |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 16 | euler | 0.550 | 0.521 | 0.552 | 0.534 | 0.625 | 0.614 | 0.669 |
| 16 | ab3 | **0.538** | **0.504** | 0.570 | 0.551 | **0.618** | 0.637 | **0.658** |
| 16 | ab4 | 0.667 | 0.637 | 0.895 | 0.842 | 0.773 | 0.966 | 0.784 |
| 16 | wls8 | 0.701 | 0.667 | 0.711 | 0.684 | 0.758 | 0.753 | 0.678 |
| 16 | dynamic | 0.586 | 0.537 | 0.574 | 0.564 | 0.644 | 0.634 | 0.670 |
| 10 | ab4 | 1.571 | 1.386 | 1.939 | 1.778 | 1.605 | 1.956 | 1.335 |
| 10 | wls8 | 0.918 | 0.903 | 0.932 | 0.911 | 0.917 | 0.914 | 0.888 |

Verdicts on the pre-registered hypotheses (paired bootstrap intervals in `results/end_to_end_10_16.md`):

* **H3 (AB-4 suffers more from quantization than WLS-8): supported only for activation quantization.**
  Extra error of AB-4 minus extra error of WLS-8 is positive with an interval excluding 0 for fp8_wa,
  int8_wa (16 steps), int4_wa8 and nvfp4_w (16 steps): +0.22, +0.19, +0.25, +0.14 at 16 steps. For
  weight-only fp8_w and int4_w the interval includes 0 (at 10 steps fp8_w and nvfp4_w even go the other
  way). Overall 6 of 10 (format x budget) cells for the aggressive formats support H3, 1 contradicts it,
  3 are inconclusive. Consistent with E1: activation quantization is re-drawn at every step, so its error
  is the white-like one that AB-4 amplifies.
* **H4 (WLS-8 beats AB-4 under every format): holds in 10 of 12 cells, not in all.** At 10 steps in
  all six formats; at 16 steps in four of six (fp8_w and int4_w inconclusive). But this is a victory over
  an unstable baseline: **in this model AB-4 is worse than plain Euler even without quantization**
  (10 steps: 1.57 against 0.68; relative error above 1 means the result is farther from the reference
  than the noise norm), and **WLS-8 is significantly worse than Euler in 13 of 14 cells** (+0.13 to
  +0.27; only nvfp4_w at 16 steps is inconclusive). Among the fixed multistep rules AB-3 is the best in
  every cell; Euler matches it and is ahead of it for the activation-quantized formats.
* **H5 (dynamic no better than the best fixed rule, regret <= 10%): partly refuted, in the favourable
  direction at 10 steps.** At 10 steps dynamic beats the best static rule (AB-3) in 5 of 7 formats,
  by 0.017-0.067 (intervals exclude 0). At 16 steps it is worse than AB-3 in bf16, fp8_w and int4_w
  (+0.027 to +0.048) and equal elsewhere; regret never exceeds 9%. The best static rule was picked per
  cell after the fact, which favours the static side. What the rule adapts to is weak: with activation
  quantization it picks long windows more often (16 steps, window 8: 26% in bf16, 36% in fp8_wa) and
  gamma = 1 more often (2% against 10%), i.e. it does smooth more where the error is white - but the
  extra quantization error of the dynamic rule is no smaller than that of Euler.
* **H6 (floor larger than discretization error for INT4-class formats): supported, narrowly for INT4.**
  Floor / solver error of the best static rule at 16 steps: int4_w 1.16, int4_wa8 1.09, nvfp4_w 1.66;
  FP8 and INT8 are 0.29-0.49. With a standard error of about 0.05 on the floors the two INT4 ratios are
  not clearly separated from 1; the NVFP4 one is.

Not answered by the data and worth saying: for 4-bit models the solver error against the model's *own*
converged solution is lower than for bf16 (nvfp4_w 0.36 against 0.55 at 16 steps). I do not have an
explanation (a smoother effective field is a guess, not a result).

### E3 - image space (SSIM and LPIPS-alex of the decoded image against the decoded converged bf16)

Latents decoded with the Qwen-Image VAE (tiled, tile 32 latent px, overlap 8, identical for every image).
Rankings agree with the latent metrics: at 16 steps LPIPS is lowest for AB-3 (0.355 in bf16), then
dynamic (0.395), Euler (0.403), WLS-5 (0.413), WLS-8 (0.449) and AB-4 (0.572). Quantization adds to the
LPIPS of AB-4 +0.14 (fp8_wa), +0.11 (int8_wa), +0.19 (int4_wa8) and to that of WLS-8 +0.04, -0.02, +0.17; Euler
changes by at most 0.02 for the 8-bit formats and by +0.15 for int4_wa8. So for the 8-bit formats the
image-space picture repeats the latent one; for INT4 all samplers lose about the same. The image-space floor (LPIPS) is 0.09
(int8_wa), 0.15 (fp8_w), 0.19 (fp8_wa), 0.42 (int4_w), 0.42 (int4_wa8), 0.46 (nvfp4_w), against 0.36-0.40
for the 16-step solver error in bf16: the same picture as H6. No confidence intervals were computed for
the image metrics, only means.

### Conclusions

1. The "multistep methods are especially sensitive to quantization" claim is **true for AB-4 and only for
   activation-quantized formats**, where the error is nearly white in time (lag-1 cosine 0.08-0.13). For
   4-bit weight-only formats the error is temporally correlated and spatially smooth, and the samplers
   are hurt about equally (extra error at 16 steps: Euler +0.075, AB-4 +0.106, WLS-8 +0.057 for int4_w),
   i.e. the loss there is the floor, not an interaction with the multistep history.
2. Flow-WLS (WLS-8) is **robust**: its extra error from any format is within +-0.06 of its bf16 error.
   But it is robust at a price: it is **worse than Euler and AB-3** on this model at 10-16 steps, with or
   without quantization. The robustness is the bounded noise gain, not better accuracy.
3. A dynamic regularization chosen by rolling-origin validation (no extra network calls) is competitive
   with the best fixed rule and better at 10 steps, but does not turn quantization noise into a gain:
   the quantization error that remains is the floor, and for INT4-class formats the floor is as large
   as or larger than the discretization error of a 16-step sampler. Better integrators cannot recover
   that part.

Limits: one model (a single Anima checkpoint), simulated rather than hardware quantization, 12
prompt-seed pairs, step budgets 10 and 16 only, and a metric (distance to a converged trajectory) that
can disagree with human preference. The grid of the dynamic rule was tuned on the synthetic toy only,
not on these 12 units.
