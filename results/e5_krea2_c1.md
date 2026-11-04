units (prompt, seed): 8

### Kernel / quantization floor (converged own solution against converged truth), relative error

| cell | floor mean | se |
| --- | --- | --- |
| krea2-q-c1 | 0.0000 | 0.0000 |

### Total error against converged truth (relative RMS of the final latent), budget 8

| method | krea2-q-c1 |
| --- | --- |
| euler | 0.5250 |
| ab2 | 0.5382 |
| ab3 | 0.5028 |
| ab4 | 0.6214 |
| wls5 | 0.5550 |
| wls8 | 0.6366 |
| dynamic | 0.4980 |
| dpmpp2m | 0.5441 |

### Total error against converged truth (relative RMS of the final latent), budget 12

| method | krea2-q-c1 |
| --- | --- |
| euler | 0.4307 |
| ab2 | 0.4527 |
| ab3 | 0.4207 |
| ab4 | 0.4832 |
| wls5 | 0.4398 |
| wls8 | 0.4692 |
| dynamic | 0.4163 |
| dpmpp2m | 0.4474 |

### Solver error against the cell's own converged solution, budget 8

| method | krea2-q-c1 |
| --- | --- |
| euler | 0.5250 |
| ab2 | 0.5382 |
| ab3 | 0.5028 |
| ab4 | 0.6214 |
| wls5 | 0.5550 |
| wls8 | 0.6366 |
| dynamic | 0.4980 |
| dpmpp2m | 0.5441 |

### Solver error against the cell's own converged solution, budget 12

| method | krea2-q-c1 |
| --- | --- |
| euler | 0.4307 |
| ab2 | 0.4527 |
| ab3 | 0.4207 |
| ab4 | 0.4832 |
| wls5 | 0.4398 |
| wls8 | 0.4692 |
| dynamic | 0.4163 |
| dpmpp2m | 0.4474 |

### Geometry (8x8 low-pass) error against converged truth, budget 8

| method | krea2-q-c1 |
| --- | --- |
| euler | 0.2227 |
| ab2 | 0.2222 |
| ab3 | 0.2056 |
| ab4 | 0.2709 |
| wls5 | 0.2813 |
| wls8 | 0.3626 |
| dynamic | 0.2267 |
| dpmpp2m | 0.2226 |

### Geometry (8x8 low-pass) error against converged truth, budget 12

| method | krea2-q-c1 |
| --- | --- |
| euler | 0.1579 |
| ab2 | 0.1629 |
| ab3 | 0.1500 |
| ab4 | 0.1753 |
| wls5 | 0.1672 |
| wls8 | 0.2040 |
| dynamic | 0.1567 |
| dpmpp2m | 0.1628 |

### Detail (high-pass) error against converged truth, budget 8

| method | krea2-q-c1 |
| --- | --- |
| euler | 0.4696 |
| ab2 | 0.4828 |
| ab3 | 0.4524 |
| ab4 | 0.5521 |
| wls5 | 0.4619 |
| wls8 | 0.4997 |
| dynamic | 0.4337 |
| dpmpp2m | 0.4893 |

### Detail (high-pass) error against converged truth, budget 12

| method | krea2-q-c1 |
| --- | --- |
| euler | 0.3946 |
| ab2 | 0.4173 |
| ab3 | 0.3880 |
| ab4 | 0.4448 |
| wls5 | 0.3974 |
| wls8 | 0.4069 |
| dynamic | 0.3781 |
| dpmpp2m | 0.4123 |

### Cosine distance of the final latent to converged truth, budget 8

| method | krea2-q-c1 |
| --- | --- |
| euler | 0.1552 |
| ab2 | 0.1569 |
| ab3 | 0.1476 |
| ab4 | 0.1894 |
| wls5 | 0.1838 |
| wls8 | 0.2530 |
| dynamic | 0.1466 |
| dpmpp2m | 0.1582 |

### Cosine distance of the final latent to converged truth, budget 12

| method | krea2-q-c1 |
| --- | --- |
| euler | 0.1179 |
| ab2 | 0.1325 |
| ab3 | 0.1248 |
| ab4 | 0.1383 |
| wls5 | 0.1344 |
| wls8 | 0.1461 |
| dynamic | 0.1240 |
| dpmpp2m | 0.1310 |

### Norm ratio of the final latent to converged truth (1 = same energy), budget 8

| method | krea2-q-c1 |
| --- | --- |
| euler | 0.9656 |
| ab2 | 1.0110 |
| ab3 | 0.9654 |
| ab4 | 1.0607 |
| wls5 | 0.8940 |
| wls8 | 0.8983 |
| dynamic | 0.9251 |
| dpmpp2m | 1.0194 |

### Norm ratio of the final latent to converged truth (1 = same energy), budget 12

| method | krea2-q-c1 |
| --- | --- |
| euler | 0.9608 |
| ab2 | 1.0142 |
| ab3 | 0.9904 |
| ab4 | 1.0364 |
| wls5 | 0.9579 |
| wls8 | 0.9263 |
| dynamic | 0.9685 |
| dpmpp2m | 1.0214 |

### Observed convergence order (slope of log solver error against log budget)

| method | krea2-q-c1 |
| --- | --- |
| euler | +0.61 +- 0.27 |
| ab2 | +0.70 +- 0.32 |
| ab3 | +0.76 +- 0.33 |
| ab4 | +0.89 +- 0.31 |
| wls5 | +0.87 +- 0.37 |
| wls8 | +0.90 +- 0.32 |
| dynamic | +0.76 +- 0.36 |
| dpmpp2m | +0.79 +- 0.31 |

### Paired contrasts against euler


**krea2-q-c1**: method - euler, total error (negative = better than euler; * = 95% interval excludes 0)

| method | 8 steps | 12 steps |
| --- | --- | --- |
| ab2 | +0.0132 [-0.0283, +0.0610]  | +0.0220 [-0.0592, +0.1351]  |
| ab3 | -0.0222 [-0.0435, -0.0018]* | -0.0100 [-0.0874, +0.0923]  |
| ab4 | +0.0964 [+0.0556, +0.1373]* | +0.0525 [-0.0177, +0.1553]  |
| wls5 | +0.0301 [-0.0124, +0.0663]  | +0.0090 [-0.0527, +0.0870]  |
| wls8 | +0.1117 [+0.0298, +0.2038]* | +0.0385 [-0.0144, +0.1007]  |
| dynamic | -0.0269 [-0.0505, -0.0023]* | -0.0144 [-0.0782, +0.0705]  |
| dpmpp2m | +0.0191 [-0.0198, +0.0653]  | +0.0166 [-0.0757, +0.1359]  |

H15 count: euler is not worse than wls8 in 2 of 2 (cell, budget) pairs.

H7 table: best of ab3/dynamic (by mean) against euler; -1 = significantly better than euler, 0 = inconclusive, +1 = significantly worse

| cell | budget | best | verdict |
| --- | --- | --- | --- |
| krea2-q-c1 | 8 | dynamic | -1 |
| krea2-q-c1 | 12 | dynamic | +0 |

### Reference convergence (ab3 and wls5 at the reference step count, relative difference)

| cell | unit | difference |
| --- | --- | --- |
| krea2-q-c1 | flat s42 | 0.0518 |

### What the dynamic rule chose (share of steps)

| cell | steps | length | degree | gamma |
| --- | --- | --- | --- | --- |
| krea2-q-c1 | 8 | 3:39%, 4:45%, 5:7%, 6:9% | 2:100% | 0.7:57%, 0.85:39%, 1.0:4% |
| krea2-q-c1 | 12 | 3:38%, 4:28%, 5:23%, 6:5%, 8:7% | 2:100% | 0.7:51%, 0.85:39%, 1.0:10% |