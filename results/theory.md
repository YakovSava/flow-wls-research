### White-noise accumulation gain (shift-3 schedule)

Ratio of the standard deviation of the final-state error caused by independent velocity errors of equal size, to the same quantity for Euler. A constant (fully correlated) error always has gain 1.

| method | N=8 | N=10 | N=12 | N=16 | N=20 | N=30 |
| --- | --- | --- | --- | --- | --- | --- |
| euler | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| ab2 | 1.14 | 1.13 | 1.12 | 1.10 | 1.08 | 1.06 |
| ab3 (= wls3) | 1.49 | 1.41 | 1.35 | 1.27 | 1.22 | 1.15 |
| ab4 | 3.10 | 2.62 | 2.31 | 1.94 | 1.72 | 1.45 |
| ab5 | 10.09 | 7.50 | 6.00 | 4.33 | 3.46 | 2.45 |
| ab6 | 38.22 | 27.11 | 19.77 | 12.42 | 8.97 | 5.38 |
| wls4 | 1.34 | 1.28 | 1.24 | 1.18 | 1.15 | 1.10 |
| wls5 | 1.29 | 1.24 | 1.21 | 1.16 | 1.13 | 1.09 |
| wls6 | 1.30 | 1.23 | 1.20 | 1.15 | 1.12 | 1.08 |
| wls8 | 1.39 | 1.25 | 1.19 | 1.15 | 1.12 | 1.08 |
| wls8 g=1.0 | 1.51 | 1.33 | 1.23 | 1.18 | 1.14 | 1.10 |
| wls8 d=1 | 1.18 | 1.15 | 1.12 | 1.09 | 1.08 | 1.06 |

### Frequency response of the one-step increment (uniform grid, N=20, step 16)

Gain on a velocity-error component that alternates with frequency w across steps (w = 0 is a constant bias).

| method | w=0.00 pi | w=0.25 pi | w=0.50 pi | w=0.75 pi | w=1.00 pi |
| --- | --- | --- | --- | --- | --- |
| euler | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| ab2 | 1.00 | 1.20 | 1.58 | 1.89 | 2.00 |
| ab3 (= wls3) | 1.00 | 1.11 | 2.01 | 3.17 | 3.67 |
| ab4 | 1.00 | 0.94 | 2.21 | 5.17 | 6.67 |
| ab5 | 1.00 | 0.89 | 2.18 | 8.49 | 12.24 |
| ab6 | 1.00 | 0.95 | 2.11 | 14.21 | 22.80 |
| wls4 | 1.00 | 1.25 | 2.26 | 2.14 | 1.06 |
| wls5 | 1.00 | 1.43 | 2.07 | 0.95 | 1.46 |
| wls6 | 1.00 | 1.59 | 1.53 | 1.14 | 0.75 |
| wls8 | 1.00 | 1.77 | 0.88 | 0.66 | 0.61 |
| wls8 g=1.0 | 1.00 | 1.91 | 0.65 | 0.43 | 0.38 |
| wls8 d=1 | 1.00 | 1.03 | 0.57 | 0.44 | 0.41 |
