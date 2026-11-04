
### SSIM against decoded converged truth (higher is better), budget 8

| method | moss-q-c4 |
| --- | --- |
| euler | 0.5800 |
| ab2 | 0.6177 |
| ab3 | 0.5955 |
| ab4 | 0.4909 |
| wls5 | 0.5098 |
| wls8 | 0.4428 |
| dynamic | 0.5961 |
| dpmpp2m | 0.6059 |

### SSIM against decoded converged truth (higher is better), budget 12

| method | moss-q-c4 |
| --- | --- |
| euler | 0.6561 |
| ab2 | 0.7038 |
| ab3 | 0.6879 |
| ab4 | 0.6557 |
| wls5 | 0.6443 |
| wls8 | 0.5885 |
| dynamic | 0.6642 |
| dpmpp2m | 0.7079 |

### LPIPS(alex) against decoded converged truth (lower is better), budget 8

| method | moss-q-c4 |
| --- | --- |
| euler | 0.3381 |
| ab2 | 0.2975 |
| ab3 | 0.3131 |
| ab4 | 0.4299 |
| wls5 | 0.4525 |
| wls8 | 0.5590 |
| dynamic | 0.3355 |
| dpmpp2m | 0.3076 |

### LPIPS(alex) against decoded converged truth (lower is better), budget 12

| method | moss-q-c4 |
| --- | --- |
| euler | 0.2402 |
| ab2 | 0.1966 |
| ab3 | 0.1978 |
| ab4 | 0.2400 |
| wls5 | 0.2331 |
| wls8 | 0.2975 |
| dynamic | 0.2101 |
| dpmpp2m | 0.1938 |

### Floor in image space (converged own solution against converged truth)

| cell | SSIM | LPIPS |
| --- | --- | --- |
| moss-q-c4 | 1.0000 | 0.0000 |