# E1/E2 (proxy) — few-shot owner verification on DSL-StrongPassword

51 subjects, 31 timing features, enroll = k random reps of session 1, test = sessions 5-8, 10 enrollment draws per subject, 95% CI by bootstrap over subjects. Lower is better.

## k = 3 enrollment samples

| Detector | EER | FAR @ FRR=5% |
|---|---|---|
| Manhattan scaled (baseline) | 0.211 [0.179, 0.244] | 0.492 [0.421, 0.559] |
| Manhattan + sd floor (current owner.py) | 0.208 [0.174, 0.242] | 0.506 [0.437, 0.578] |
| E2 variance prior nu=2 | 0.199 [0.164, 0.234] | 0.382 [0.310, 0.453] |
| E2 variance prior nu=5 | 0.200 [0.165, 0.237] | 0.381 [0.308, 0.452] |
| E2 variance prior nu=10 | 0.200 [0.164, 0.236] | 0.380 [0.312, 0.448] |
| E1 Mahalanobis shrink lam=0.5 | 0.247 [0.216, 0.279] | 0.618 [0.557, 0.678] |
| E1 Mahalanobis shrink lam=0.9 | 0.246 [0.214, 0.278] | 0.618 [0.556, 0.676] |

## k = 5 enrollment samples

| Detector | EER | FAR @ FRR=5% |
|---|---|---|
| Manhattan scaled (baseline) | 0.198 [0.165, 0.229] | 0.465 [0.392, 0.538] |
| Manhattan + sd floor (current owner.py) | 0.199 [0.168, 0.235] | 0.472 [0.394, 0.548] |
| E2 variance prior nu=2 | 0.197 [0.162, 0.232] | 0.382 [0.306, 0.452] |
| E2 variance prior nu=5 | 0.198 [0.163, 0.236] | 0.378 [0.304, 0.452] |
| E2 variance prior nu=10 | 0.198 [0.161, 0.238] | 0.377 [0.301, 0.454] |
| E1 Mahalanobis shrink lam=0.5 | 0.221 [0.192, 0.251] | 0.604 [0.535, 0.671] |
| E1 Mahalanobis shrink lam=0.9 | 0.218 [0.190, 0.249] | 0.600 [0.531, 0.667] |

## k = 10 enrollment samples

| Detector | EER | FAR @ FRR=5% |
|---|---|---|
| Manhattan scaled (baseline) | 0.194 [0.160, 0.228] | 0.435 [0.364, 0.510] |
| Manhattan + sd floor (current owner.py) | 0.194 [0.158, 0.231] | 0.441 [0.366, 0.514] |
| E2 variance prior nu=2 | 0.193 [0.155, 0.231] | 0.375 [0.300, 0.451] |
| E2 variance prior nu=5 | 0.195 [0.159, 0.232] | 0.369 [0.296, 0.444] |
| E2 variance prior nu=10 | 0.195 [0.160, 0.235] | 0.367 [0.297, 0.445] |
| E1 Mahalanobis shrink lam=0.5 | 0.211 [0.181, 0.243] | 0.570 [0.501, 0.639] |
| E1 Mahalanobis shrink lam=0.9 | 0.208 [0.176, 0.241] | 0.560 [0.490, 0.632] |

## Paired difference (same subjects): E2 nu=5 minus baseline, negative = E2 better

| k | dEER | dFAR @ FRR=5% |
|---|---|---|
| 3 | -0.011 [-0.022, +0.001] | -0.112 [-0.153, -0.071] |
| 5 | +0.000 [-0.010, +0.011] | -0.087 [-0.122, -0.051] |
| 10 | +0.001 [-0.006, +0.010] | -0.066 [-0.097, -0.036] |
