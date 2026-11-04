units (prompt, seed): 4

### Kernel / quantization floor (converged own solution against converged truth), relative error

| cell | floor mean | se |
| --- | --- | --- |
| flux3-q-c4 | 0.1588 | 0.0623 |
| flux3-d-c4 | 0.0000 | 0.0000 |

### Total error against converged truth (relative RMS of the final latent), budget 8

| method | flux3-q-c4 | flux3-d-c4 |
| --- | --- | --- |
| euler | 0.7261 | 0.7211 |
| ab2 | 0.7194 | 0.7160 |
| ab3 | 0.7950 | 0.7942 |
| ab4 | 1.5465 | 1.5296 |
| wls5 | 0.9179 | 0.9144 |
| wls8 | 1.2086 | 1.2022 |
| dynamic | 0.8782 | 0.8770 |
| dpmpp2m | 0.7138 | 0.7164 |

### Total error against converged truth (relative RMS of the final latent), budget 12

| method | flux3-q-c4 | flux3-d-c4 |
| --- | --- | --- |
| euler | 0.6355 | 0.6297 |
| ab2 | 0.6134 | 0.6085 |
| ab3 | 0.6536 | 0.6559 |
| ab4 | 1.1264 | 1.1043 |
| wls5 | 0.7815 | 0.7846 |
| wls8 | 0.8322 | 0.8346 |
| dynamic | 0.7341 | 0.7337 |
| dpmpp2m | 0.6225 | 0.6179 |

### Solver error against the cell's own converged solution, budget 8

| method | flux3-q-c4 | flux3-d-c4 |
| --- | --- | --- |
| euler | 0.7294 | 0.7211 |
| ab2 | 0.7252 | 0.7160 |
| ab3 | 0.7972 | 0.7942 |
| ab4 | 1.5448 | 1.5296 |
| wls5 | 0.9199 | 0.9144 |
| wls8 | 1.2095 | 1.2022 |
| dynamic | 0.8798 | 0.8770 |
| dpmpp2m | 0.7292 | 0.7164 |

### Solver error against the cell's own converged solution, budget 12

| method | flux3-q-c4 | flux3-d-c4 |
| --- | --- | --- |
| euler | 0.6335 | 0.6297 |
| ab2 | 0.6086 | 0.6085 |
| ab3 | 0.6525 | 0.6559 |
| ab4 | 1.1260 | 1.1043 |
| wls5 | 0.7836 | 0.7846 |
| wls8 | 0.8335 | 0.8346 |
| dynamic | 0.7344 | 0.7337 |
| dpmpp2m | 0.6158 | 0.6179 |

### Geometry (8x8 low-pass) error against converged truth, budget 8

| method | flux3-q-c4 | flux3-d-c4 |
| --- | --- | --- |
| euler | 0.2382 | 0.2354 |
| ab2 | 0.2070 | 0.2051 |
| ab3 | 0.2941 | 0.2961 |
| ab4 | 0.6996 | 0.6995 |
| wls5 | 0.5262 | 0.5240 |
| wls8 | 0.9009 | 0.8968 |
| dynamic | 0.4276 | 0.4290 |
| dpmpp2m | 0.2059 | 0.2080 |

### Geometry (8x8 low-pass) error against converged truth, budget 12

| method | flux3-q-c4 | flux3-d-c4 |
| --- | --- | --- |
| euler | 0.1812 | 0.1806 |
| ab2 | 0.1616 | 0.1615 |
| ab3 | 0.2111 | 0.2170 |
| ab4 | 0.4767 | 0.4550 |
| wls5 | 0.3772 | 0.3766 |
| wls8 | 0.4737 | 0.4749 |
| dynamic | 0.3109 | 0.3065 |
| dpmpp2m | 0.1668 | 0.1625 |

### Detail (high-pass) error against converged truth, budget 8

| method | flux3-q-c4 | flux3-d-c4 |
| --- | --- | --- |
| euler | 0.6856 | 0.6813 |
| ab2 | 0.6887 | 0.6857 |
| ab3 | 0.7382 | 0.7366 |
| ab4 | 1.3773 | 1.3588 |
| wls5 | 0.7489 | 0.7461 |
| wls8 | 0.7979 | 0.7926 |
| dynamic | 0.7656 | 0.7635 |
| dpmpp2m | 0.6832 | 0.6852 |

### Detail (high-pass) error against converged truth, budget 12

| method | flux3-q-c4 | flux3-d-c4 |
| --- | --- | --- |
| euler | 0.6087 | 0.6028 |
| ab2 | 0.5915 | 0.5865 |
| ab3 | 0.6180 | 0.6185 |
| ab4 | 1.0194 | 1.0048 |
| wls5 | 0.6827 | 0.6866 |
| wls8 | 0.6799 | 0.6824 |
| dynamic | 0.6644 | 0.6661 |
| dpmpp2m | 0.5995 | 0.5959 |

### Cosine distance of the final latent to converged truth, budget 8

| method | flux3-q-c4 | flux3-d-c4 |
| --- | --- | --- |
| euler | 0.2799 | 0.2776 |
| ab2 | 0.2760 | 0.2737 |
| ab3 | 0.3160 | 0.3170 |
| ab4 | 0.6818 | 0.6788 |
| wls5 | 0.3750 | 0.3735 |
| wls8 | 0.4505 | 0.4477 |
| dynamic | 0.3645 | 0.3639 |
| dpmpp2m | 0.2714 | 0.2727 |

### Cosine distance of the final latent to converged truth, budget 12

| method | flux3-q-c4 | flux3-d-c4 |
| --- | --- | --- |
| euler | 0.2136 | 0.2100 |
| ab2 | 0.1969 | 0.1947 |
| ab3 | 0.2180 | 0.2190 |
| ab4 | 0.4962 | 0.4830 |
| wls5 | 0.2969 | 0.3000 |
| wls8 | 0.3103 | 0.3127 |
| dynamic | 0.2669 | 0.2678 |
| dpmpp2m | 0.2008 | 0.1990 |

### Norm ratio of the final latent to converged truth (1 = same energy), budget 8

| method | flux3-q-c4 | flux3-d-c4 |
| --- | --- | --- |
| euler | 0.9502 | 0.9471 |
| ab2 | 0.9675 | 0.9687 |
| ab3 | 1.0038 | 0.9987 |
| ab4 | 1.5382 | 1.5207 |
| wls5 | 1.1090 | 1.1053 |
| wls8 | 1.4219 | 1.4172 |
| dynamic | 1.0619 | 1.0594 |
| dpmpp2m | 0.9754 | 0.9763 |

### Norm ratio of the final latent to converged truth (1 = same energy), budget 12

| method | flux3-q-c4 | flux3-d-c4 |
| --- | --- | --- |
| euler | 0.9653 | 0.9642 |
| ab2 | 0.9823 | 0.9798 |
| ab3 | 0.9929 | 0.9920 |
| ab4 | 1.2256 | 1.2142 |
| wls5 | 1.0341 | 1.0332 |
| wls8 | 1.1012 | 1.1010 |
| dynamic | 1.0172 | 1.0140 |
| dpmpp2m | 0.9902 | 0.9897 |

### Observed convergence order (slope of log solver error against log budget)

| method | flux3-q-c4 | flux3-d-c4 |
| --- | --- | --- |
| euler | +0.36 +- 0.14 | +0.34 +- 0.15 |
| ab2 | +0.43 +- 0.18 | +0.39 +- 0.19 |
| ab3 | +0.51 +- 0.18 | +0.48 +- 0.13 |
| ab4 | +0.81 +- 0.28 | +0.84 +- 0.30 |
| wls5 | +0.40 +- 0.08 | +0.39 +- 0.09 |
| wls8 | +0.92 +- 0.06 | +0.90 +- 0.07 |
| dynamic | +0.45 +- 0.09 | +0.45 +- 0.07 |
| dpmpp2m | +0.41 +- 0.18 | +0.36 +- 0.21 |

### Paired contrasts against euler


**flux3-q-c4**: method - euler, total error (negative = better than euler; * = 95% interval excludes 0)

| method | 8 steps | 12 steps |
| --- | --- | --- |
| ab2 | -0.0067 [-0.0413, +0.0279]  | -0.0221 [-0.0355, -0.0040]* |
| ab3 | +0.0689 [-0.0092, +0.1520]  | +0.0181 [-0.0123, +0.0485]  |
| ab4 | +0.8204 [+0.6716, +1.0240]* | +0.4909 [+0.3948, +0.6504]* |
| wls5 | +0.1919 [+0.0939, +0.2898]* | +0.1460 [+0.0632, +0.2289]* |
| wls8 | +0.4825 [+0.4083, +0.5567]* | +0.1967 [+0.1202, +0.2642]* |
| dynamic | +0.1521 [+0.0286, +0.2756]* | +0.0986 [+0.0196, +0.1776]* |
| dpmpp2m | -0.0123 [-0.0587, +0.0341]  | -0.0130 [-0.0284, +0.0130]  |

**flux3-d-c4**: method - euler, total error (negative = better than euler; * = 95% interval excludes 0)

| method | 8 steps | 12 steps |
| --- | --- | --- |
| ab2 | -0.0051 [-0.0371, +0.0269]  | -0.0212 [-0.0337, -0.0094]* |
| ab3 | +0.0731 [-0.0049, +0.1534]  | +0.0262 [-0.0125, +0.0649]  |
| ab4 | +0.8085 [+0.6821, +1.0268]* | +0.4746 [+0.3818, +0.6332]* |
| wls5 | +0.1933 [+0.0928, +0.2938]* | +0.1549 [+0.0702, +0.2423]* |
| wls8 | +0.4811 [+0.4041, +0.5581]* | +0.2049 [+0.1259, +0.2821]* |
| dynamic | +0.1559 [+0.0342, +0.2777]* | +0.1040 [+0.0253, +0.1927]* |
| dpmpp2m | -0.0048 [-0.0376, +0.0281]  | -0.0118 [-0.0276, +0.0040]  |

### Effect of the real INT8 kernels (Q - D)


**flux3-q-c4 against flux3-d-c4**: extra total error of the real INT8 path, same method

| method | 8 steps | 12 steps |
| --- | --- | --- |
| euler | +0.0050 [-0.0077, +0.0142]  | +0.0058 [+0.0036, +0.0076]* |
| ab2 | +0.0034 [-0.0041, +0.0079]  | +0.0049 [-0.0031, +0.0130]  |
| ab3 | +0.0008 [-0.0068, +0.0073]  | -0.0023 [-0.0218, +0.0136]  |
| ab4 | +0.0169 [-0.0131, +0.0488]  | +0.0221 [+0.0018, +0.0359]* |
| wls5 | +0.0035 [-0.0025, +0.0075]  | -0.0031 [-0.0140, +0.0044]  |
| wls8 | +0.0063 [+0.0027, +0.0100]* | -0.0025 [-0.0117, +0.0038]  |
| dynamic | +0.0011 [-0.0071, +0.0093]  | +0.0004 [-0.0112, +0.0115]  |
| dpmpp2m | -0.0026 [-0.0381, +0.0259]  | +0.0046 [-0.0073, +0.0168]  |

ab4 extra - wls8 extra (H14):

* 8 steps: +0.0106 [-0.0215, +0.0442] 
* 12 steps: +0.0245 [-0.0016, +0.0401] 

H15 count: euler is not worse than wls8 in 4 of 4 (cell, budget) pairs.

H7 table: best of ab3/dynamic (by mean) against euler; -1 = significantly better than euler, 0 = inconclusive, +1 = significantly worse

| cell | budget | best | verdict |
| --- | --- | --- | --- |
| flux3-q-c4 | 8 | ab3 | +0 |
| flux3-q-c4 | 12 | ab3 | +0 |
| flux3-d-c4 | 8 | ab3 | +0 |
| flux3-d-c4 | 12 | ab3 | +0 |

### Reference convergence (ab3 and wls5 at the reference step count, relative difference)

| cell | unit | difference |
| --- | --- | --- |
| flux3-q-c4 | flat s42 | 0.3421 |
| flux3-d-c4 | flat s42 | 0.2002 |

### What the dynamic rule chose (share of steps)

| cell | steps | length | degree | gamma |
| --- | --- | --- | --- | --- |
| flux3-q-c4 | 8 | 3:71%, 4:29% | 2:100% | 0.7:14%, 0.85:71%, 1.0:14% |
| flux3-q-c4 | 12 | 3:32%, 4:52%, 5:11%, 6:5% | 2:100% | 0.7:68%, 0.85:32% |
| flux3-d-c4 | 8 | 3:75%, 4:25% | 2:100% | 0.7:11%, 0.85:75%, 1.0:14% |
| flux3-d-c4 | 12 | 3:34%, 4:50%, 5:11%, 6:5% | 2:100% | 0.7:66%, 0.85:34% |