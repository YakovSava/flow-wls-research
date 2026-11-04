units (prompt, seed): 8

### Kernel / quantization floor (converged own solution against converged truth), relative error

| cell | floor mean | se |
| --- | --- | --- |
| moss-q-c4 | 0.0000 | 0.0000 |

### Total error against converged truth (relative RMS of the final latent), budget 8

| method | moss-q-c4 |
| --- | --- |
| euler | 0.6648 |
| ab2 | 0.6725 |
| ab3 | 0.6628 |
| ab4 | 0.9706 |
| wls5 | 0.7413 |
| wls8 | 0.8550 |
| dynamic | 0.6853 |
| dpmpp2m | 0.6908 |

### Total error against converged truth (relative RMS of the final latent), budget 12

| method | moss-q-c4 |
| --- | --- |
| euler | 0.5720 |
| ab2 | 0.5518 |
| ab3 | 0.5529 |
| ab4 | 0.6212 |
| wls5 | 0.5817 |
| wls8 | 0.6195 |
| dynamic | 0.5587 |
| dpmpp2m | 0.5516 |

### Solver error against the cell's own converged solution, budget 8

| method | moss-q-c4 |
| --- | --- |
| euler | 0.6648 |
| ab2 | 0.6725 |
| ab3 | 0.6628 |
| ab4 | 0.9706 |
| wls5 | 0.7413 |
| wls8 | 0.8550 |
| dynamic | 0.6853 |
| dpmpp2m | 0.6908 |

### Solver error against the cell's own converged solution, budget 12

| method | moss-q-c4 |
| --- | --- |
| euler | 0.5720 |
| ab2 | 0.5518 |
| ab3 | 0.5529 |
| ab4 | 0.6212 |
| wls5 | 0.5817 |
| wls8 | 0.6195 |
| dynamic | 0.5587 |
| dpmpp2m | 0.5516 |

### Geometry (8x8 low-pass) error against converged truth, budget 8

| method | moss-q-c4 |
| --- | --- |
| euler | 0.2431 |
| ab2 | 0.2293 |
| ab3 | 0.2310 |
| ab4 | 0.3558 |
| wls5 | 0.3602 |
| wls8 | 0.5154 |
| dynamic | 0.2684 |
| dpmpp2m | 0.2348 |

### Geometry (8x8 low-pass) error against converged truth, budget 12

| method | moss-q-c4 |
| --- | --- |
| euler | 0.1855 |
| ab2 | 0.1659 |
| ab3 | 0.1607 |
| ab4 | 0.1932 |
| wls5 | 0.2032 |
| wls8 | 0.2615 |
| dynamic | 0.1717 |
| dpmpp2m | 0.1647 |

### Detail (high-pass) error against converged truth, budget 8

| method | moss-q-c4 |
| --- | --- |
| euler | 0.6185 |
| ab2 | 0.6320 |
| ab3 | 0.6206 |
| ab4 | 0.9025 |
| wls5 | 0.6454 |
| wls8 | 0.6764 |
| dynamic | 0.6304 |
| dpmpp2m | 0.6495 |

### Detail (high-pass) error against converged truth, budget 12

| method | moss-q-c4 |
| --- | --- |
| euler | 0.5407 |
| ab2 | 0.5250 |
| ab3 | 0.5281 |
| ab4 | 0.5897 |
| wls5 | 0.5433 |
| wls8 | 0.5588 |
| dynamic | 0.5305 |
| dpmpp2m | 0.5251 |

### Cosine distance of the final latent to converged truth, budget 8

| method | moss-q-c4 |
| --- | --- |
| euler | 0.2485 |
| ab2 | 0.2474 |
| ab3 | 0.2409 |
| ab4 | 0.3845 |
| wls5 | 0.2874 |
| wls8 | 0.3391 |
| dynamic | 0.2553 |
| dpmpp2m | 0.2563 |

### Cosine distance of the final latent to converged truth, budget 12

| method | moss-q-c4 |
| --- | --- |
| euler | 0.1881 |
| ab2 | 0.1709 |
| ab3 | 0.1700 |
| ab4 | 0.2027 |
| wls5 | 0.1825 |
| wls8 | 0.2025 |
| dynamic | 0.1728 |
| dpmpp2m | 0.1694 |

### Norm ratio of the final latent to converged truth (1 = same energy), budget 8

| method | moss-q-c4 |
| --- | --- |
| euler | 0.8729 |
| ab2 | 0.9383 |
| ab3 | 0.9286 |
| ab4 | 1.1864 |
| wls5 | 0.9630 |
| wls8 | 1.0655 |
| dynamic | 0.9378 |
| dpmpp2m | 0.9587 |

### Norm ratio of the final latent to converged truth (1 = same energy), budget 12

| method | moss-q-c4 |
| --- | --- |
| euler | 0.9121 |
| ab2 | 0.9618 |
| ab3 | 0.9595 |
| ab4 | 1.0087 |
| wls5 | 0.9569 |
| wls8 | 0.9668 |
| dynamic | 0.9513 |
| dpmpp2m | 0.9778 |

### Observed convergence order (slope of log solver error against log budget)

| method | moss-q-c4 |
| --- | --- |
| euler | +0.42 +- 0.13 |
| ab2 | +0.56 +- 0.19 |
| ab3 | +0.50 +- 0.14 |
| ab4 | +1.16 +- 0.17 |
| wls5 | +0.62 +- 0.09 |
| wls8 | +0.80 +- 0.08 |
| dynamic | +0.52 +- 0.14 |
| dpmpp2m | +0.65 +- 0.20 |

### Paired contrasts against euler


**moss-q-c4**: method - euler, total error (negative = better than euler; * = 95% interval excludes 0)

| method | 8 steps | 12 steps |
| --- | --- | --- |
| ab2 | +0.0077 [-0.0080, +0.0230]  | -0.0202 [-0.0558, +0.0116]  |
| ab3 | -0.0020 [-0.0225, +0.0196]  | -0.0191 [-0.0477, +0.0079]  |
| ab4 | +0.3058 [+0.2668, +0.3480]* | +0.0492 [+0.0171, +0.0894]* |
| wls5 | +0.0765 [+0.0425, +0.1091]* | +0.0097 [-0.0304, +0.0448]  |
| wls8 | +0.1902 [+0.1380, +0.2361]* | +0.0475 [+0.0000, +0.0893]* |
| dynamic | +0.0205 [-0.0031, +0.0477]  | -0.0133 [-0.0512, +0.0231]  |
| dpmpp2m | +0.0260 [+0.0102, +0.0402]* | -0.0204 [-0.0564, +0.0107]  |

H15 count: euler is not worse than wls8 in 2 of 2 (cell, budget) pairs.

H7 table: best of ab3/dynamic (by mean) against euler; -1 = significantly better than euler, 0 = inconclusive, +1 = significantly worse

| cell | budget | best | verdict |
| --- | --- | --- | --- |
| moss-q-c4 | 8 | ab3 | +0 |
| moss-q-c4 | 12 | ab3 | +0 |

### Reference convergence (ab3 and wls5 at the reference step count, relative difference)

| cell | unit | difference |
| --- | --- | --- |
| moss-q-c4 | flat s42 | 0.3503 |

### What the dynamic rule chose (share of steps)

| cell | steps | length | degree | gamma |
| --- | --- | --- | --- | --- |
| moss-q-c4 | 8 | 3:66%, 4:20%, 5:7%, 6:7% | 2:100% | 0.7:34%, 0.85:66% |
| moss-q-c4 | 12 | 3:32%, 4:24%, 5:16%, 6:20%, 8:8% | 2:100% | 0.7:58%, 0.85:36%, 1.0:6% |