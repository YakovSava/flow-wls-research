# INT8 Isn't the Problem: Measuring Samplers on Quantized Flow-Matching Models (and Disproving Our Own Idea)

*Subtitle: Real INT8 kernels add white noise that barely shows. What actually matters is the sampler and the guidance scale, and the regularized sampler we proposed lost to a 2nd-order classic.*

**Tags (Medium allows five):** Machine Learning, Stable Diffusion, Generative AI, Open Source, Quantization

*Images to upload from the repository's `figures/` folder: `grid_anima_fur_cfg5.jpg` (hero), `grid_krea2_face_cfg1.jpg`, `grid_flux3_face_cfg1.jpg`. Run `git push` before publishing so the links work.*

---

If you run image models on a home GPU you are probably running quantized weights, and you have probably read the advice that goes with them: don't use fancy samplers on quantized models, they accumulate the error. We wanted to check that. The result was inconvenient for us, so this is partly a story about being wrong.

## The idea we started with

In an earlier preprint we proposed Flow-WLS, a multistep sampler that fits a low-degree polynomial to the recent velocity history by weighted least squares and integrates it. The argument was that this kind of smoothing would damp the high-frequency noise that quantization adds. It sounded reasonable, and we expected it to hold.

Before each round of measurements we wrote down the hypotheses and the conditions under which each would count as supported: six at first, nine more before the follow-up. That habit matters: it makes it hard to bend the conclusion afterwards. Several hypotheses failed, and they stay in the write-up.

## What we measured

Four flow-matching models: Anima (bf16, plus simulated FP8, INT8, INT4 and NVFP4), and three real INT8 checkpoints run by ComfyUI's own kernels: Flux3-Klein, Krea 2 (with ConvRot) and Moss-Image. Four prompts, two or three seeds, 8 to 24 steps, guidance scale (CFG) from 1 to 5. The reference for every error is a many-step solution of the same model.

For Flux3 we compared two modes of the very same checkpoint: the real INT8 path (quantized weights and dynamically quantized activations) and the same weights dequantized to bf16. The difference between the two isolates the error of the kernels.

## Finding 1: the kernel noise is white, and small

The error of the real INT8 kernels is uncorrelated between consecutive steps (correlation −0.001). It is 1.3% of the velocity norm at CFG 1 and 5.7% at CFG 4. The final latent moves by about 0.02 or less, and the perceptual distance (LPIPS) between the converged INT8 and bf16-dequantized images is 0.014 at CFG 1 and 0.029 at CFG 4. You cannot see it.

One caveat we cannot remove: we compared the INT8 kernels with the same weights in bf16. The rounding error of the INT8 weights against an unknown bf16 original was not measured.

## Finding 2: higher-order samplers amplify white noise

If the error is white, you can compute how much a multistep rule amplifies it. Relative to Euler: 1.06 for Adams-Bashforth of order 2, 1.21 for order 3, 1.97 for order 4. That matched what we saw, since order 4 was the most sensitive to INT8. But its own excess error, 0.5 to 0.8, is tens of times larger than anything quantization added.

## Finding 3: the right sampler depends on guidance

On Anima we ran nine samplers at CFG 1, 3 and 5 and at 8, 12, 16 and 24 steps.

- A 2nd-order Adams-Bashforth beat Euler in all 12 settings, by 0.03 to 0.12 in latent error.
- DPM++ 2M overtook Euler at strong guidance from about 16 to 24 steps.
- At CFG 1, which is how distilled models such as Flux3-Klein and Krea 2 run, the 3rd-order rule gave the lowest error among the simple rules.
- Order 4 and the long-window Flow-WLS were never the best choice at 12 steps or fewer, in any model.

Our first experiment had concluded that Euler was the best. It was, among the six methods in that set, none of which was Adams-Bashforth 2. When we added it, the conclusion changed, and we corrected the write-up.

## Why

The velocity the network outputs is not a smooth function of the step. It is a smooth trend plus a jitter that is uncorrelated from one step to the next. We measured its relative size: about 1% of the norm at CFG 1, 4% at CFG 3 and 6 to 7% at CFG 5. The guidance term (the difference between the conditional and unconditional predictions, scaled by CFG) is redrawn at every step. A rule with large weights amplifies that jitter, and it only helps when the jitter is small. That fits all of the above.

We then asked whether a better history filter could be fitted directly from data. A constant-weight linear filter, cross-validated by leaving one unit out, improved on the best existing rule by at most 3.4%. So there is no room for a new sampler of this family, and we are not claiming one.

## What you can see

![Anima, texture-heavy prompt, 8/12/16 steps](grid_anima_fur_cfg5.jpg)

Rows: Euler, DPM++ 2M, AB-2, AB-3, WLS-8. The number on each tile is LPIPS to the reference.

On a texture-heavy prompt at 8 steps Euler leaves almost black noise (LPIPS 0.89), while DPM++ 2M (0.35) and AB-2 (0.42) give a complete picture. At 16 steps Euler is at 0.34, against 0.20 for DPM++ 2M, 0.21 for AB-3 and 0.23 for AB-2. On Krea 2 at 12 steps Euler gives airbrushed skin, and AB-2, DPM++ 2M and AB-3 bring the pores and freckles back. On Flux3-Klein at 12 steps Euler, DPM++ 2M, AB-2 and AB-3 are visually the same picture, so there is no reason to switch there.

## Using it

The repository is a ComfyUI custom node. It adds `flow_ab2`, `flow_ab3` and `flow_ab4` to the normal sampler list, plus a one-choice node, "Flow Easy Sampler". Use `flow_ab2` for CFG 3 and above and `flow_ab3` for distilled models at CFG 1. It works with flow-matching models (Anima, Flux3, Krea 2, Moss); we did not test SDXL-type models.

## What we did not show

- LPIPS measures distance to a many-step image, not preference. We did not run a human preference test.
- Four prompts, four models, one seed per displayed picture and no seed picking.
- The reference does not converge for Moss-Image, so only large effects are meaningful there. For Flux3 at CFG 4 it converges to 20-34%.
- Moss-Image and Krea 2 were measured in the quantized mode only.
- Adams-Bashforth 2 and DPM++ 2M were added to part of the experiments after the first results. The write-up marks which.
- Adams-Bashforth 2 is not new. The contribution is the measurement, and a negative result for our own idea.

Code, tables and figures: https://github.com/YakovSava/flow-wls-research
Preprint: https://doi.org/10.5281/zenodo.23939696
