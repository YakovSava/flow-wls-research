
### SSIM against decoded converged truth (higher is better), budget 8

| method | flux3-q-c4 | flux3-d-c4 |
| --- | --- | --- |
| euler | 0.6492 | 0.6539 |
| ab2 | 0.6550 | 0.6574 |
| ab3 | 0.6025 | 0.6053 |
| ab4 | 0.3118 | 0.3213 |
| wls5 | 0.5082 | 0.5119 |
| wls8 | 0.4641 | 0.4665 |
| dynamic | 0.5416 | 0.5441 |
| dpmpp2m | 0.6574 | 0.6588 |

### SSIM against decoded converged truth (higher is better), budget 12

| method | flux3-q-c4 | flux3-d-c4 |
| --- | --- | --- |
| euler | 0.7129 | 0.7159 |
| ab2 | 0.7328 | 0.7384 |
| ab3 | 0.7008 | 0.7039 |
| ab4 | 0.4950 | 0.4995 |
| wls5 | 0.5990 | 0.6000 |
| wls8 | 0.5651 | 0.5674 |
| dynamic | 0.6384 | 0.6449 |
| dpmpp2m | 0.7329 | 0.7341 |

### LPIPS(alex) against decoded converged truth (lower is better), budget 8

| method | flux3-q-c4 | flux3-d-c4 |
| --- | --- | --- |
| euler | 0.3031 | 0.3015 |
| ab2 | 0.3008 | 0.3038 |
| ab3 | 0.3649 | 0.3706 |
| ab4 | 0.7582 | 0.7607 |
| wls5 | 0.5128 | 0.5107 |
| wls8 | 0.5965 | 0.5962 |
| dynamic | 0.4532 | 0.4543 |
| dpmpp2m | 0.3037 | 0.3059 |

### LPIPS(alex) against decoded converged truth (lower is better), budget 12

| method | flux3-q-c4 | flux3-d-c4 |
| --- | --- | --- |
| euler | 0.2536 | 0.2492 |
| ab2 | 0.2317 | 0.2316 |
| ab3 | 0.2720 | 0.2741 |
| ab4 | 0.5551 | 0.5455 |
| wls5 | 0.4155 | 0.4099 |
| wls8 | 0.4619 | 0.4592 |
| dynamic | 0.3454 | 0.3417 |
| dpmpp2m | 0.2415 | 0.2349 |

### Floor in image space (converged own solution against converged truth)

| cell | SSIM | LPIPS |
| --- | --- | --- |
| flux3-q-c4 | 0.9692 | 0.0286 |
| flux3-d-c4 | 1.0000 | 0.0000 |