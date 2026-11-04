
### SSIM against decoded converged truth (higher is better), budget 8

| method | moss-q-c4 |
| --- | --- |
| euler | 0.5790 |
| ab2 | 0.6196 |
| ab3 | 0.5944 |
| ab4 | 0.4924 |
| wls5 | 0.5098 |
| wls8 | 0.4431 |
| dynamic | 0.5948 |
| dpmpp2m | 0.6064 |

### SSIM against decoded converged truth (higher is better), budget 12

| method | moss-q-c4 |
| --- | --- |
| euler | 0.6547 |
| ab2 | 0.7068 |
| ab3 | 0.6852 |
| ab4 | 0.6592 |
| wls5 | 0.6426 |
| wls8 | 0.5871 |
| dynamic | 0.6608 |
| dpmpp2m | 0.7108 |

### LPIPS(alex) against decoded converged truth (lower is better), budget 8

| method | moss-q-c4 |
| --- | --- |
| euler | 0.3420 |
| ab2 | 0.2983 |
| ab3 | 0.3117 |
| ab4 | 0.4290 |
| wls5 | 0.4491 |
| wls8 | 0.5553 |
| dynamic | 0.3366 |
| dpmpp2m | 0.3090 |

### LPIPS(alex) against decoded converged truth (lower is better), budget 12

| method | moss-q-c4 |
| --- | --- |
| euler | 0.2427 |
| ab2 | 0.2001 |
| ab3 | 0.2023 |
| ab4 | 0.2421 |
| wls5 | 0.2369 |
| wls8 | 0.2984 |
| dynamic | 0.2162 |
| dpmpp2m | 0.1953 |

### Floor in image space (converged own solution against converged truth)

| cell | SSIM | LPIPS |
| --- | --- | --- |
| moss-q-c4 | 1.0000 | 0.0000 |