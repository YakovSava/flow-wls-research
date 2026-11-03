
### SSIM against decoded converged truth (higher is better), budget 8

| method | anima-bf16-c1 | anima-bf16-c3 | bf16 |
| --- | --- | --- | --- |
| euler | 0.5373 | 0.4566 | 0.4150 |
| ab2 | 0.6413 | 0.4973 | 0.4584 |
| ab3 | 0.6516 | 0.4446 | 0.3861 |
| ab4 | 0.4706 | 0.2268 | 0.1765 |
| wls5 | 0.6321 | 0.3943 | 0.3760 |
| wls8 | 0.6085 | 0.3678 | 0.3693 |
| dynamic | 0.6513 | 0.4208 | 0.3861 |
| dpmpp2m | 0.6044 | 0.4729 | 0.4130 |
| heun | 0.5502 | 0.4036 | 0.3657 |

### SSIM against decoded converged truth (higher is better), budget 12

| method | anima-bf16-c1 | anima-bf16-c3 | bf16 |
| --- | --- | --- | --- |
| euler | 0.6124 | 0.5184 | 0.4707 |
| ab2 | 0.7218 | 0.5999 | 0.5021 |
| ab3 | 0.7338 | 0.5238 | 0.4547 |
| ab4 | 0.6388 | 0.4057 | 0.3064 |
| wls5 | 0.7215 | 0.4632 | 0.3982 |
| wls8 | 0.6991 | 0.4269 | 0.3828 |
| dynamic | 0.7273 | 0.4966 | 0.4156 |
| dpmpp2m | 0.7007 | 0.5871 | 0.4871 |
| heun | 0.6384 | 0.4626 | 0.4014 |

### SSIM against decoded converged truth (higher is better), budget 16

| method | anima-bf16-c1 | anima-bf16-c3 | bf16 |
| --- | --- | --- | --- |
| euler | 0.6759 | 0.5920 | 0.5079 |
| ab2 | 0.7854 | 0.6883 | 0.5682 |
| ab3 | 0.7964 | 0.6263 | 0.5089 |
| ab4 | 0.7594 | 0.5363 | 0.4146 |
| wls5 | 0.7783 | 0.5303 | 0.4489 |
| wls8 | 0.7541 | 0.4811 | 0.4198 |
| dynamic | 0.7869 | 0.5731 | 0.4772 |
| dpmpp2m | 0.7776 | 0.6687 | 0.5519 |
| heun | 0.7159 | 0.5217 | 0.4609 |

### SSIM against decoded converged truth (higher is better), budget 24

| method | anima-bf16-c1 | anima-bf16-c3 | bf16 |
| --- | --- | --- | --- |
| euler | 0.7469 | 0.6753 | 0.6388 |
| ab2 | 0.8509 | 0.7667 | 0.6907 |
| ab3 | 0.8758 | 0.7658 | 0.6360 |
| ab4 | 0.8653 | 0.6720 | 0.5354 |
| wls5 | 0.8479 | 0.6596 | 0.5088 |
| wls8 | 0.8124 | 0.5897 | 0.4629 |
| dynamic | 0.8539 | 0.7472 | 0.6282 |
| dpmpp2m | 0.8538 | 0.7578 | 0.6758 |
| heun | 0.7816 | 0.6381 | 0.5189 |

### LPIPS(alex) against decoded converged truth (lower is better), budget 8

| method | anima-bf16-c1 | anima-bf16-c3 | bf16 |
| --- | --- | --- | --- |
| euler | 0.6255 | 0.5666 | 0.6447 |
| ab2 | 0.3558 | 0.4121 | 0.4955 |
| ab3 | 0.2866 | 0.4375 | 0.6299 |
| ab4 | 0.4180 | 0.6973 | 0.7695 |
| wls5 | 0.3321 | 0.5632 | 0.7186 |
| wls8 | 0.3646 | 0.6478 | 0.7728 |
| dynamic | 0.2884 | 0.4874 | 0.6552 |
| dpmpp2m | 0.3273 | 0.3869 | 0.4864 |
| heun | 0.5265 | 0.6480 | 0.7655 |

### LPIPS(alex) against decoded converged truth (lower is better), budget 12

| method | anima-bf16-c1 | anima-bf16-c3 | bf16 |
| --- | --- | --- | --- |
| euler | 0.4585 | 0.4544 | 0.4856 |
| ab2 | 0.2343 | 0.3154 | 0.4229 |
| ab3 | 0.2104 | 0.3290 | 0.4600 |
| ab4 | 0.2424 | 0.5327 | 0.7068 |
| wls5 | 0.2320 | 0.4021 | 0.5824 |
| wls8 | 0.2555 | 0.4549 | 0.6459 |
| dynamic | 0.2253 | 0.3742 | 0.5526 |
| dpmpp2m | 0.2548 | 0.3049 | 0.4174 |
| heun | 0.3979 | 0.4990 | 0.6400 |

### LPIPS(alex) against decoded converged truth (lower is better), budget 16

| method | anima-bf16-c1 | anima-bf16-c3 | bf16 |
| --- | --- | --- | --- |
| euler | 0.3370 | 0.3539 | 0.4416 |
| ab2 | 0.1605 | 0.2404 | 0.3688 |
| ab3 | 0.1561 | 0.2597 | 0.3864 |
| ab4 | 0.1519 | 0.3740 | 0.5796 |
| wls5 | 0.1747 | 0.3246 | 0.4468 |
| wls8 | 0.1959 | 0.3815 | 0.4848 |
| dynamic | 0.1679 | 0.3019 | 0.4276 |
| dpmpp2m | 0.1793 | 0.2427 | 0.3739 |
| heun | 0.2772 | 0.4112 | 0.5072 |

### LPIPS(alex) against decoded converged truth (lower is better), budget 24

| method | anima-bf16-c1 | anima-bf16-c3 | bf16 |
| --- | --- | --- | --- |
| euler | 0.2275 | 0.2732 | 0.2524 |
| ab2 | 0.1003 | 0.1763 | 0.1967 |
| ab3 | 0.0801 | 0.1486 | 0.2405 |
| ab4 | 0.0708 | 0.2179 | 0.3565 |
| wls5 | 0.1076 | 0.1937 | 0.3705 |
| wls8 | 0.1463 | 0.2444 | 0.4337 |
| dynamic | 0.1007 | 0.1694 | 0.2591 |
| dpmpp2m | 0.1118 | 0.1758 | 0.2009 |
| heun | 0.1858 | 0.2857 | 0.4100 |

### Floor in image space (converged own solution against converged truth)

| cell | SSIM | LPIPS |
| --- | --- | --- |
| anima-bf16-c1 | 1.0000 | 0.0000 |
| anima-bf16-c3 | 1.0000 | 0.0000 |
| bf16 | 1.0000 | 0.0000 |