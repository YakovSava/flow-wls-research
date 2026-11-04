units (prompt, seed): 8

### Kernel / quantization floor (converged own solution against converged truth), relative error

| cell | floor mean | se |
| --- | --- | --- |
| moss-q-c4 | 0.0000 | 0.0000 |

### Total error against converged truth (relative RMS of the final latent), budget 8

| method | moss-q-c4 |
| --- | --- |
| euler | 0.6638 |
| ab2 | 0.6739 |
| ab3 | 0.6661 |
| ab4 | 0.9767 |
| wls5 | 0.7467 |
| wls8 | 0.8609 |
| dynamic | 0.6883 |
| dpmpp2m | 0.6915 |

### Total error against converged truth (relative RMS of the final latent), budget 12

| method | moss-q-c4 |
| --- | --- |
| euler | 0.5693 |
| ab2 | 0.5519 |
| ab3 | 0.5459 |
| ab4 | 0.6219 |
| wls5 | 0.5754 |
| wls8 | 0.6149 |
| dynamic | 0.5502 |
| dpmpp2m | 0.5538 |

### Solver error against the cell's own converged solution, budget 8

| method | moss-q-c4 |
| --- | --- |
| euler | 0.6638 |
| ab2 | 0.6739 |
| ab3 | 0.6661 |
| ab4 | 0.9767 |
| wls5 | 0.7467 |
| wls8 | 0.8609 |
| dynamic | 0.6883 |
| dpmpp2m | 0.6915 |

### Solver error against the cell's own converged solution, budget 12

| method | moss-q-c4 |
| --- | --- |
| euler | 0.5693 |
| ab2 | 0.5519 |
| ab3 | 0.5459 |
| ab4 | 0.6219 |
| wls5 | 0.5754 |
| wls8 | 0.6149 |
| dynamic | 0.5502 |
| dpmpp2m | 0.5538 |

### Geometry (8x8 low-pass) error against converged truth, budget 8

| method | moss-q-c4 |
| --- | --- |
| euler | 0.2422 |
| ab2 | 0.2268 |
| ab3 | 0.2311 |
| ab4 | 0.3559 |
| wls5 | 0.3617 |
| wls8 | 0.5176 |
| dynamic | 0.2677 |
| dpmpp2m | 0.2318 |

### Geometry (8x8 low-pass) error against converged truth, budget 12

| method | moss-q-c4 |
| --- | --- |
| euler | 0.1834 |
| ab2 | 0.1645 |
| ab3 | 0.1561 |
| ab4 | 0.1913 |
| wls5 | 0.2001 |
| wls8 | 0.2600 |
| dynamic | 0.1661 |
| dpmpp2m | 0.1635 |

### Detail (high-pass) error against converged truth, budget 8

| method | moss-q-c4 |
| --- | --- |
| euler | 0.6177 |
| ab2 | 0.6343 |
| ab3 | 0.6241 |
| ab4 | 0.9090 |
| wls5 | 0.6506 |
| wls8 | 0.6819 |
| dynamic | 0.6339 |
| dpmpp2m | 0.6513 |

### Detail (high-pass) error against converged truth, budget 12

| method | moss-q-c4 |
| --- | --- |
| euler | 0.5385 |
| ab2 | 0.5256 |
| ab3 | 0.5221 |
| ab4 | 0.5910 |
| wls5 | 0.5378 |
| wls8 | 0.5545 |
| dynamic | 0.5233 |
| dpmpp2m | 0.5279 |

### Cosine distance of the final latent to converged truth, budget 8

| method | moss-q-c4 |
| --- | --- |
| euler | 0.2477 |
| ab2 | 0.2487 |
| ab3 | 0.2433 |
| ab4 | 0.3883 |
| wls5 | 0.2909 |
| wls8 | 0.3426 |
| dynamic | 0.2575 |
| dpmpp2m | 0.2571 |

### Cosine distance of the final latent to converged truth, budget 12

| method | moss-q-c4 |
| --- | --- |
| euler | 0.1861 |
| ab2 | 0.1702 |
| ab3 | 0.1661 |
| ab4 | 0.2032 |
| wls5 | 0.1788 |
| wls8 | 0.1994 |
| dynamic | 0.1685 |
| dpmpp2m | 0.1703 |

### Norm ratio of the final latent to converged truth (1 = same energy), budget 8

| method | moss-q-c4 |
| --- | --- |
| euler | 0.8753 |
| ab2 | 0.9409 |
| ab3 | 0.9311 |
| ab4 | 1.1898 |
| wls5 | 0.9656 |
| wls8 | 1.0685 |
| dynamic | 0.9403 |
| dpmpp2m | 0.9612 |

### Norm ratio of the final latent to converged truth (1 = same energy), budget 12

| method | moss-q-c4 |
| --- | --- |
| euler | 0.9146 |
| ab2 | 0.9644 |
| ab3 | 0.9621 |
| ab4 | 1.0114 |
| wls5 | 0.9595 |
| wls8 | 0.9695 |
| dynamic | 0.9538 |
| dpmpp2m | 0.9804 |

### Observed convergence order (slope of log solver error against log budget)

| method | moss-q-c4 |
| --- | --- |
| euler | +0.43 +- 0.13 |
| ab2 | +0.56 +- 0.20 |
| ab3 | +0.54 +- 0.13 |
| ab4 | +1.18 +- 0.17 |
| wls5 | +0.67 +- 0.09 |
| wls8 | +0.84 +- 0.07 |
| dynamic | +0.58 +- 0.15 |
| dpmpp2m | +0.63 +- 0.21 |

### Paired contrasts against euler


**moss-q-c4**: method - euler, total error (negative = better than euler; * = 95% interval excludes 0)

| method | 8 steps | 12 steps |
| --- | --- | --- |
| ab2 | +0.0100 [-0.0082, +0.0252]  | -0.0173 [-0.0565, +0.0182]  |
| ab3 | +0.0023 [-0.0170, +0.0203]  | -0.0233 [-0.0518, +0.0035]  |
| ab4 | +0.3129 [+0.2732, +0.3554]* | +0.0527 [+0.0114, +0.0992]* |
| wls5 | +0.0828 [+0.0545, +0.1111]* | +0.0061 [-0.0347, +0.0405]  |
| wls8 | +0.1970 [+0.1524, +0.2377]* | +0.0456 [-0.0018, +0.0866]  |
| dynamic | +0.0245 [+0.0017, +0.0487]* | -0.0190 [-0.0633, +0.0196]  |
| dpmpp2m | +0.0277 [+0.0118, +0.0400]* | -0.0155 [-0.0574, +0.0216]  |

H15 count: euler is not worse than wls8 in 2 of 2 (cell, budget) pairs.

H7 table: best of ab3/dynamic (by mean) against euler; -1 = significantly better than euler, 0 = inconclusive, +1 = significantly worse

| cell | budget | best | verdict |
| --- | --- | --- | --- |
| moss-q-c4 | 8 | ab3 | +0 |
| moss-q-c4 | 12 | ab3 | +0 |

### Reference convergence (ab3 and wls5 at the reference step count, relative difference)

| cell | unit | difference |
| --- | --- | --- |
| moss-q-c4 | flat s42 | 0.2190 |

### What the dynamic rule chose (share of steps)

| cell | steps | length | degree | gamma |
| --- | --- | --- | --- | --- |
| moss-q-c4 | 8 | 3:66%, 4:20%, 5:7%, 6:7% | 2:100% | 0.7:34%, 0.85:66% |
| moss-q-c4 | 12 | 3:32%, 4:24%, 5:16%, 6:20%, 8:8% | 2:100% | 0.7:58%, 0.85:36%, 1.0:6% |