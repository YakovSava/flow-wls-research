
### SSIM against decoded converged truth (higher is better), budget 8

| method | flux3-q-c1 | flux3-d-c1 |
| --- | --- | --- |
| euler | 0.6664 | 0.6662 |
| ab2 | 0.6712 | 0.6711 |
| ab3 | 0.6840 | 0.6840 |
| ab4 | 0.5984 | 0.6004 |
| wls5 | 0.6425 | 0.6418 |
| wls8 | 0.5967 | 0.5968 |
| dynamic | 0.6752 | 0.6742 |
| dpmpp2m | 0.6669 | 0.6693 |

### SSIM against decoded converged truth (higher is better), budget 12

| method | flux3-q-c1 | flux3-d-c1 |
| --- | --- | --- |
| euler | 0.7436 | 0.7443 |
| ab2 | 0.7788 | 0.7755 |
| ab3 | 0.7877 | 0.7846 |
| ab4 | 0.7480 | 0.7471 |
| wls5 | 0.7751 | 0.7714 |
| wls8 | 0.7377 | 0.7353 |
| dynamic | 0.7783 | 0.7774 |
| dpmpp2m | 0.7765 | 0.7718 |

### LPIPS(alex) against decoded converged truth (lower is better), budget 8

| method | flux3-q-c1 | flux3-d-c1 |
| --- | --- | --- |
| euler | 0.2581 | 0.2589 |
| ab2 | 0.2641 | 0.2646 |
| ab3 | 0.2492 | 0.2487 |
| ab4 | 0.3649 | 0.3635 |
| wls5 | 0.3113 | 0.3119 |
| wls8 | 0.3818 | 0.3808 |
| dynamic | 0.2652 | 0.2648 |
| dpmpp2m | 0.2731 | 0.2706 |

### LPIPS(alex) against decoded converged truth (lower is better), budget 12

| method | flux3-q-c1 | flux3-d-c1 |
| --- | --- | --- |
| euler | 0.1968 | 0.1968 |
| ab2 | 0.1573 | 0.1606 |
| ab3 | 0.1464 | 0.1506 |
| ab4 | 0.1854 | 0.1886 |
| wls5 | 0.1638 | 0.1669 |
| wls8 | 0.2173 | 0.2176 |
| dynamic | 0.1566 | 0.1585 |
| dpmpp2m | 0.1627 | 0.1662 |

### Floor in image space (converged own solution against converged truth)

| cell | SSIM | LPIPS |
| --- | --- | --- |
| flux3-q-c1 | 0.9818 | 0.0140 |
| flux3-d-c1 | 1.0000 | 0.0000 |