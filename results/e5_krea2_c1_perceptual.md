
### SSIM against decoded converged truth (higher is better), budget 8

| method | krea2-q-c1 |
| --- | --- |
| euler | 0.6207 |
| ab2 | 0.6289 |
| ab3 | 0.6265 |
| ab4 | 0.5661 |
| wls5 | 0.5714 |
| wls8 | 0.5362 |
| dynamic | 0.6174 |
| dpmpp2m | 0.6234 |

### SSIM against decoded converged truth (higher is better), budget 12

| method | krea2-q-c1 |
| --- | --- |
| euler | 0.6611 |
| ab2 | 0.6730 |
| ab3 | 0.6953 |
| ab4 | 0.6485 |
| wls5 | 0.6515 |
| wls8 | 0.6187 |
| dynamic | 0.6796 |
| dpmpp2m | 0.6849 |

### LPIPS(alex) against decoded converged truth (lower is better), budget 8

| method | krea2-q-c1 |
| --- | --- |
| euler | 0.3422 |
| ab2 | 0.3123 |
| ab3 | 0.3040 |
| ab4 | 0.3658 |
| wls5 | 0.3492 |
| wls8 | 0.3911 |
| dynamic | 0.3065 |
| dpmpp2m | 0.3130 |

### LPIPS(alex) against decoded converged truth (lower is better), budget 12

| method | krea2-q-c1 |
| --- | --- |
| euler | 0.2453 |
| ab2 | 0.2248 |
| ab3 | 0.2037 |
| ab4 | 0.2359 |
| wls5 | 0.2166 |
| wls8 | 0.2489 |
| dynamic | 0.2040 |
| dpmpp2m | 0.2187 |

### Floor in image space (converged own solution against converged truth)

| cell | SSIM | LPIPS |
| --- | --- | --- |
| krea2-q-c1 | 1.0000 | 0.0000 |