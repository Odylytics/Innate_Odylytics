# E10 — deployable shrinkage toward the population (StrokePIN, real humans)

Enrollment on k=3 sessions; PIN-knowing impostor; scores pooled over all (person, PIN) pairs; 95% CI by bootstrap over people (100 resamples). The dEER and dFAR columns are the **paired difference versus the current backend** (negative = better). Touch size is not used.

## Feature set: timing

| Detector | EER | FAR @ FRR 5% | dEER vs backend | dFAR vs backend |
|---|---|---|---|---|
| backend (sd with floor) | 0.200 | 0.698 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| E2 per PIN, nu=5 (upper bound) | 0.200 | 0.583 | -0.000 [-0.005, +0.005] | -0.115 [-0.138, -0.093] |
| E2 pooled, nu=5 | 0.208 | 0.577 | +0.007 [+0.003, +0.012] | -0.121 [-0.144, -0.095] |
| E2 pooled, nu=10 | 0.213 | 0.585 | +0.012 [+0.008, +0.018] | -0.113 [-0.136, -0.084] |
| E2 pooled + floor, nu=5 | 0.212 | 0.605 | +0.011 [+0.006, +0.016] | -0.093 [-0.120, -0.069] |
| E2 pooled + floor, nu=10 | 0.216 | 0.609 | +0.016 [+0.011, +0.021] | -0.089 [-0.117, -0.062] |
| HYBRID nu=3: E2 pooled for timing + sd with floor for center offset | 0.204 | 0.578 | +0.004 [-0.001, +0.008] | -0.120 [-0.146, -0.098] |
| HYBRID nu=5: E2 pooled for timing + sd with floor for center offset | 0.208 | 0.577 | +0.007 [+0.003, +0.012] | -0.121 [-0.144, -0.095] |
| HYBRID nu=10: E2 pooled for timing + sd with floor for center offset | 0.213 | 0.585 | +0.012 [+0.008, +0.018] | -0.113 [-0.136, -0.084] |

## Feature set: timing + center offset

| Detector | EER | FAR @ FRR 5% | dEER vs backend | dFAR vs backend |
|---|---|---|---|---|
| backend (sd with floor) | 0.166 | 0.715 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| E2 per PIN, nu=5 (upper bound) | 0.198 | 0.677 | +0.032 [+0.026, +0.036] | -0.038 [-0.087, -0.005] |
| E2 pooled, nu=5 | 0.203 | 0.773 | +0.037 [+0.031, +0.043] | +0.058 [+0.004, +0.096] |
| E2 pooled, nu=10 | 0.216 | 0.810 | +0.050 [+0.043, +0.058] | +0.095 [+0.040, +0.139] |
| E2 pooled + floor, nu=5 | 0.207 | 0.795 | +0.041 [+0.034, +0.047] | +0.080 [+0.022, +0.123] |
| E2 pooled + floor, nu=10 | 0.220 | 0.825 | +0.054 [+0.046, +0.061] | +0.110 [+0.051, +0.155] |
| HYBRID nu=3: E2 pooled for timing + sd with floor for center offset | 0.160 | 0.575 | -0.006 [-0.010, -0.004] | -0.140 [-0.186, -0.112] |
| HYBRID nu=5: E2 pooled for timing + sd with floor for center offset | 0.160 | 0.564 | -0.006 [-0.009, -0.003] | -0.151 [-0.196, -0.112] |
| HYBRID nu=10: E2 pooled for timing + sd with floor for center offset | 0.161 | 0.559 | -0.005 [-0.008, -0.002] | -0.156 [-0.202, -0.116] |
