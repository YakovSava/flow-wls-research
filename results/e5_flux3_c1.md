units (prompt, seed): 8

### Kernel / quantization floor (converged own solution against converged truth), relative error

| cell | floor mean | se |
| --- | --- | --- |
| flux3-q-c1 | 0.0969 | 0.0205 |
| flux3-d-c1 | 0.0000 | 0.0000 |

### Total error against converged truth (relative RMS of the final latent), budget 8

| method | flux3-q-c1 | flux3-d-c1 |
| --- | --- | --- |
| euler | 0.6421 | 0.6443 |
| ab2 | 0.6467 | 0.6466 |
| ab3 | 0.6274 | 0.6283 |
| ab4 | 0.8171 | 0.8184 |
| wls5 | 0.6656 | 0.6674 |
| wls8 | 0.7217 | 0.7223 |
| dynamic | 0.6360 | 0.6373 |
| dpmpp2m | 0.6571 | 0.6543 |

### Total error against converged truth (relative RMS of the final latent), budget 12

| method | flux3-q-c1 | flux3-d-c1 |
| --- | --- | --- |
| euler | 0.5290 | 0.5275 |
| ab2 | 0.4736 | 0.4773 |
| ab3 | 0.4595 | 0.4646 |
| ab4 | 0.5147 | 0.5172 |
| wls5 | 0.4739 | 0.4787 |
| wls8 | 0.5080 | 0.5115 |
| dynamic | 0.4705 | 0.4732 |
| dpmpp2m | 0.4826 | 0.4877 |

### Solver error against the cell's own converged solution, budget 8

| method | flux3-q-c1 | flux3-d-c1 |
| --- | --- | --- |
| euler | 0.6471 | 0.6443 |
| ab2 | 0.6514 | 0.6466 |
| ab3 | 0.6319 | 0.6283 |
| ab4 | 0.8205 | 0.8184 |
| wls5 | 0.6676 | 0.6674 |
| wls8 | 0.7222 | 0.7223 |
| dynamic | 0.6400 | 0.6373 |
| dpmpp2m | 0.6620 | 0.6543 |

### Solver error against the cell's own converged solution, budget 12

| method | flux3-q-c1 | flux3-d-c1 |
| --- | --- | --- |
| euler | 0.5347 | 0.5275 |
| ab2 | 0.4791 | 0.4773 |
| ab3 | 0.4679 | 0.4646 |
| ab4 | 0.5207 | 0.5172 |
| wls5 | 0.4809 | 0.4787 |
| wls8 | 0.5137 | 0.5115 |
| dynamic | 0.4782 | 0.4732 |
| dpmpp2m | 0.4883 | 0.4877 |

### Geometry (8x8 low-pass) error against converged truth, budget 8

| method | flux3-q-c1 | flux3-d-c1 |
| --- | --- | --- |
| euler | 0.1715 | 0.1719 |
| ab2 | 0.1820 | 0.1827 |
| ab3 | 0.1710 | 0.1712 |
| ab4 | 0.2868 | 0.2884 |
| wls5 | 0.2154 | 0.2155 |
| wls8 | 0.2955 | 0.2945 |
| dynamic | 0.1802 | 0.1807 |
| dpmpp2m | 0.1871 | 0.1871 |

### Geometry (8x8 low-pass) error against converged truth, budget 12

| method | flux3-q-c1 | flux3-d-c1 |
| --- | --- | --- |
| euler | 0.1311 | 0.1312 |
| ab2 | 0.1157 | 0.1185 |
| ab3 | 0.1114 | 0.1128 |
| ab4 | 0.1295 | 0.1315 |
| wls5 | 0.1263 | 0.1268 |
| wls8 | 0.1686 | 0.1685 |
| dynamic | 0.1184 | 0.1188 |
| dpmpp2m | 0.1197 | 0.1223 |

### Detail (high-pass) error against converged truth, budget 8

| method | flux3-q-c1 | flux3-d-c1 |
| --- | --- | --- |
| euler | 0.6185 | 0.6205 |
| ab2 | 0.6202 | 0.6199 |
| ab3 | 0.6033 | 0.6043 |
| ab4 | 0.7643 | 0.7652 |
| wls5 | 0.6293 | 0.6311 |
| wls8 | 0.6573 | 0.6583 |
| dynamic | 0.6097 | 0.6108 |
| dpmpp2m | 0.6296 | 0.6266 |

### Detail (high-pass) error against converged truth, budget 12

| method | flux3-q-c1 | flux3-d-c1 |
| --- | --- | --- |
| euler | 0.5122 | 0.5107 |
| ab2 | 0.4591 | 0.4622 |
| ab3 | 0.4456 | 0.4505 |
| ab4 | 0.4980 | 0.5000 |
| wls5 | 0.4566 | 0.4614 |
| wls8 | 0.4784 | 0.4822 |
| dynamic | 0.4551 | 0.4578 |
| dpmpp2m | 0.4673 | 0.4719 |

### Cosine distance of the final latent to converged truth, budget 8

| method | flux3-q-c1 | flux3-d-c1 |
| --- | --- | --- |
| euler | 0.2260 | 0.2279 |
| ab2 | 0.2221 | 0.2225 |
| ab3 | 0.2100 | 0.2108 |
| ab4 | 0.3138 | 0.3142 |
| wls5 | 0.2335 | 0.2345 |
| wls8 | 0.2656 | 0.2658 |
| dynamic | 0.2153 | 0.2162 |
| dpmpp2m | 0.2271 | 0.2253 |

### Cosine distance of the final latent to converged truth, budget 12

| method | flux3-q-c1 | flux3-d-c1 |
| --- | --- | --- |
| euler | 0.1551 | 0.1546 |
| ab2 | 0.1177 | 0.1199 |
| ab3 | 0.1110 | 0.1136 |
| ab4 | 0.1378 | 0.1393 |
| wls5 | 0.1180 | 0.1200 |
| wls8 | 0.1333 | 0.1348 |
| dynamic | 0.1169 | 0.1178 |
| dpmpp2m | 0.1209 | 0.1237 |

### Norm ratio of the final latent to converged truth (1 = same energy), budget 8

| method | flux3-q-c1 | flux3-d-c1 |
| --- | --- | --- |
| euler | 0.9132 | 0.9138 |
| ab2 | 0.9591 | 0.9597 |
| ab3 | 0.9522 | 0.9528 |
| ab4 | 1.0640 | 1.0656 |
| wls5 | 0.9571 | 0.9579 |
| wls8 | 0.9887 | 0.9893 |
| dynamic | 0.9530 | 0.9529 |
| dpmpp2m | 0.9722 | 0.9724 |

### Norm ratio of the final latent to converged truth (1 = same energy), budget 12

| method | flux3-q-c1 | flux3-d-c1 |
| --- | --- | --- |
| euler | 0.9518 | 0.9520 |
| ab2 | 0.9830 | 0.9836 |
| ab3 | 0.9776 | 0.9777 |
| ab4 | 0.9889 | 0.9892 |
| wls5 | 0.9749 | 0.9758 |
| wls8 | 0.9811 | 0.9821 |
| dynamic | 0.9759 | 0.9760 |
| dpmpp2m | 0.9931 | 0.9936 |

### Observed convergence order (slope of log solver error against log budget)

| method | flux3-q-c1 | flux3-d-c1 |
| --- | --- | --- |
| euler | +0.53 +- 0.17 | +0.55 +- 0.17 |
| ab2 | +0.78 +- 0.15 | +0.77 +- 0.15 |
| ab3 | +0.76 +- 0.14 | +0.76 +- 0.14 |
| ab4 | +1.15 +- 0.16 | +1.16 +- 0.16 |
| wls5 | +0.83 +- 0.12 | +0.84 +- 0.11 |
| wls8 | +0.85 +- 0.08 | +0.86 +- 0.07 |
| dynamic | +0.74 +- 0.15 | +0.75 +- 0.14 |
| dpmpp2m | +0.77 +- 0.15 | +0.74 +- 0.16 |

### Paired contrasts against euler


**flux3-q-c1**: method - euler, total error (negative = better than euler; * = 95% interval excludes 0)

| method | 8 steps | 12 steps |
| --- | --- | --- |
| ab2 | +0.0046 [-0.0156, +0.0216]  | -0.0554 [-0.1203, +0.0002]  |
| ab3 | -0.0148 [-0.0388, +0.0066]  | -0.0695 [-0.1360, -0.0103]* |
| ab4 | +0.1750 [+0.1459, +0.2053]* | -0.0143 [-0.0780, +0.0410]  |
| wls5 | +0.0234 [-0.0142, +0.0579]  | -0.0550 [-0.1290, +0.0120]  |
| wls8 | +0.0795 [+0.0327, +0.1232]* | -0.0210 [-0.1036, +0.0552]  |
| dynamic | -0.0061 [-0.0370, +0.0211]  | -0.0585 [-0.1291, +0.0031]  |
| dpmpp2m | +0.0150 [-0.0062, +0.0362]  | -0.0464 [-0.1151, +0.0115]  |

**flux3-d-c1**: method - euler, total error (negative = better than euler; * = 95% interval excludes 0)

| method | 8 steps | 12 steps |
| --- | --- | --- |
| ab2 | +0.0023 [-0.0188, +0.0195]  | -0.0502 [-0.1151, +0.0079]  |
| ab3 | -0.0159 [-0.0406, +0.0056]  | -0.0629 [-0.1299, -0.0049]* |
| ab4 | +0.1741 [+0.1421, +0.2084]* | -0.0104 [-0.0749, +0.0467]  |
| wls5 | +0.0231 [-0.0183, +0.0589]  | -0.0488 [-0.1211, +0.0183]  |
| wls8 | +0.0780 [+0.0274, +0.1257]* | -0.0160 [-0.0970, +0.0600]  |
| dynamic | -0.0070 [-0.0379, +0.0189]  | -0.0543 [-0.1223, +0.0069]  |
| dpmpp2m | +0.0100 [-0.0098, +0.0267]  | -0.0398 [-0.1106, +0.0227]  |

### Effect of the real INT8 kernels (Q - D)


**flux3-q-c1 against flux3-d-c1**: extra total error of the real INT8 path, same method

| method | 8 steps | 12 steps |
| --- | --- | --- |
| euler | -0.0021 [-0.0115, +0.0047]  | +0.0014 [-0.0016, +0.0050]  |
| ab2 | +0.0001 [-0.0081, +0.0077]  | -0.0037 [-0.0173, +0.0107]  |
| ab3 | -0.0010 [-0.0076, +0.0034]  | -0.0051 [-0.0108, +0.0003]  |
| ab4 | -0.0013 [-0.0048, +0.0024]  | -0.0025 [-0.0087, +0.0033]  |
| wls5 | -0.0018 [-0.0072, +0.0027]  | -0.0048 [-0.0115, +0.0010]  |
| wls8 | -0.0006 [-0.0045, +0.0031]  | -0.0035 [-0.0089, +0.0008]  |
| dynamic | -0.0013 [-0.0076, +0.0035]  | -0.0027 [-0.0113, +0.0050]  |
| dpmpp2m | +0.0028 [-0.0005, +0.0070]  | -0.0051 [-0.0145, +0.0028]  |

ab4 extra - wls8 extra (H14):

* 8 steps: -0.0007 [-0.0067, +0.0066] 
* 12 steps: +0.0010 [-0.0059, +0.0080] 

H15 count: euler is not worse than wls8 in 2 of 4 (cell, budget) pairs.

H7 table: best of ab3/dynamic (by mean) against euler; -1 = significantly better than euler, 0 = inconclusive, +1 = significantly worse

| cell | budget | best | verdict |
| --- | --- | --- | --- |
| flux3-q-c1 | 8 | ab3 | +0 |
| flux3-q-c1 | 12 | ab3 | -1 |
| flux3-d-c1 | 8 | ab3 | +0 |
| flux3-d-c1 | 12 | ab3 | -1 |

### Reference convergence (ab3 and wls5 at the reference step count, relative difference)

| cell | unit | difference |
| --- | --- | --- |
| flux3-q-c1 | flat s42 | 0.0283 |
| flux3-d-c1 | flat s42 | 0.0205 |

### What the dynamic rule chose (share of steps)

| cell | steps | length | degree | gamma |
| --- | --- | --- | --- | --- |
| flux3-q-c1 | 8 | 3:55%, 4:45% | 2:100% | 0.7:29%, 0.85:55%, 1.0:16% |
| flux3-q-c1 | 12 | 3:41%, 4:52%, 5:5%, 6:2% | 2:100% | 0.7:59%, 0.85:41% |
| flux3-d-c1 | 8 | 3:61%, 4:39% | 2:100% | 0.7:23%, 0.85:61%, 1.0:16% |
| flux3-d-c1 | 12 | 3:41%, 4:52%, 5:6%, 6:1% | 2:100% | 0.7:58%, 0.85:41%, 1.0:1% |