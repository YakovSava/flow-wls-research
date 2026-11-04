# LinkedIn (English)

Attach: `figures/grid_anima_fur_cfg5.jpg` (or a crop of two rows from it). LinkedIn shows about the first three lines before "see more", so the opening carries the post. Put the links in the first comment if you prefer the post itself without links.

---

We set out to show that a sampler we had proposed would protect INT8 image models from quantization noise. The measurements said otherwise, and that turned out to be the more useful result.

What we found, on four flow-matching models (Anima, Flux3-Klein, Krea 2, Moss-Image), with registered hypotheses and paired confidence intervals:

- The error of real INT8 kernels is white noise, 1.3% to 5.7% of the velocity norm. On the final image it is close to invisible (LPIPS 0.014 to 0.029).
- The choice of sampler changes the result far more than INT8 does (0.05 to 0.8 in latent error, against 0.02 at most). Order-4 methods and our own earlier regularized sampler were never the best choice at 12 steps or fewer.
- A classic 2nd-order Adams-Bashforth beat Euler in all 12 settings we tested on Anima. DPM++ 2M wins from 16 to 24 steps at strong guidance. Distilled models at CFG 1 prefer order 3.
- Why: the network output carries step-to-step jitter of about 1% of its norm at CFG 1 and 6-7% at CFG 5, and high-order rules amplify it.

What we did not show: human preference (LPIPS is distance to a many-step image), more than four prompts and four models, or anything about SDXL-type models. Adams-Bashforth 2 is not new; the contribution is the measurement and a negative result for our own idea.

Preprint: https://doi.org/10.5281/zenodo.23939696
Code: https://github.com/YakovSava/flow-wls-research

#MachineLearning #DiffusionModels #Quantization #OpenSource #ComfyUI #GenerativeAI
