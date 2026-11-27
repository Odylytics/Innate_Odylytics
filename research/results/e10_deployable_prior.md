# E10 — deployable shrinkage toward the population (StrokePIN, real humans)

Enrollment on k=3 sitting sessions; PIN-knowing impostor; scores pooled over all (person, PIN) pairs; 95% CI by bootstrap over people (100 resamples). The dEER and dFAR columns are the **paired difference versus the current backend** (negative = better). Touch size is not used.

## same posture (sitting), feature set: timing

| Detector | EER | FAR @ FRR 5% | dEER vs backend | dFAR vs backend |
|---|---|---|---|---|
| backend (sd with floor) | 0.199 | 0.674 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| E2 per PIN, nu=5 (upper bound) | 0.199 | 0.561 | -0.000 [-0.006, +0.004] | -0.112 [-0.140, -0.086] |
| E2 pooled, nu=5 | 0.205 | 0.566 | +0.005 [+0.000, +0.010] | -0.108 [-0.137, -0.082] |
| E2 pooled, nu=10 | 0.210 | 0.572 | +0.011 [+0.005, +0.015] | -0.101 [-0.133, -0.072] |
| E2 pooled + floor, nu=5 | 0.209 | 0.589 | +0.009 [+0.005, +0.013] | -0.085 [-0.115, -0.060] |
| E2 pooled + floor, nu=10 | 0.214 | 0.594 | +0.015 [+0.010, +0.019] | -0.080 [-0.112, -0.052] |
| HYBRID nu=3: E2 pooled for timing + sd with floor for center offset | 0.201 | 0.563 | +0.002 [-0.002, +0.006] | -0.111 [-0.140, -0.084] |
| HYBRID nu=5: E2 pooled for timing + sd with floor for center offset | 0.205 | 0.566 | +0.005 [+0.000, +0.010] | -0.108 [-0.137, -0.082] |
| HYBRID nu=10: E2 pooled for timing + sd with floor for center offset | 0.210 | 0.572 | +0.011 [+0.005, +0.015] | -0.101 [-0.133, -0.072] |

## same posture (sitting), feature set: timing + center offset

| Detector | EER | FAR @ FRR 5% | dEER vs backend | dFAR vs backend |
|---|---|---|---|---|
| backend (sd with floor) | 0.164 | 0.678 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| E2 per PIN, nu=5 (upper bound) | 0.195 | 0.651 | +0.032 [+0.027, +0.036] | -0.028 [-0.065, +0.024] |
| E2 pooled, nu=5 | 0.205 | 0.739 | +0.041 [+0.034, +0.047] | +0.061 [+0.021, +0.119] |
| E2 pooled, nu=10 | 0.218 | 0.781 | +0.054 [+0.047, +0.061] | +0.102 [+0.062, +0.166] |
| E2 pooled + floor, nu=5 | 0.209 | 0.770 | +0.045 [+0.038, +0.051] | +0.092 [+0.047, +0.144] |
| E2 pooled + floor, nu=10 | 0.222 | 0.799 | +0.058 [+0.050, +0.066] | +0.121 [+0.078, +0.185] |
| HYBRID nu=3: E2 pooled for timing + sd with floor for center offset | 0.158 | 0.522 | -0.006 [-0.008, -0.003] | -0.156 [-0.177, -0.114] |
| HYBRID nu=5: E2 pooled for timing + sd with floor for center offset | 0.159 | 0.519 | -0.005 [-0.008, -0.002] | -0.159 [-0.181, -0.117] |
| HYBRID nu=10: E2 pooled for timing + sd with floor for center offset | 0.160 | 0.513 | -0.004 [-0.007, +0.000] | -0.165 [-0.185, -0.116] |

## changed posture (walking), feature set: timing

| Detector | EER | FAR @ FRR 5% | dEER vs backend | dFAR vs backend |
|---|---|---|---|---|
| backend (sd with floor) | 0.324 | 0.837 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| E2 per PIN, nu=5 (upper bound) | 0.319 | 0.763 | -0.005 [-0.012, +0.000] | -0.074 [-0.096, -0.056] |
| E2 pooled, nu=5 | 0.324 | 0.775 | +0.000 [-0.008, +0.006] | -0.063 [-0.086, -0.045] |
| E2 pooled, nu=10 | 0.328 | 0.774 | +0.004 [-0.004, +0.011] | -0.063 [-0.084, -0.045] |
| E2 pooled + floor, nu=5 | 0.328 | 0.783 | +0.004 [-0.003, +0.009] | -0.054 [-0.072, -0.039] |
| E2 pooled + floor, nu=10 | 0.332 | 0.783 | +0.008 [-0.000, +0.012] | -0.054 [-0.074, -0.038] |
| HYBRID nu=3: E2 pooled for timing + sd with floor for center offset | 0.320 | 0.773 | -0.004 [-0.010, +0.003] | -0.064 [-0.083, -0.047] |
| HYBRID nu=5: E2 pooled for timing + sd with floor for center offset | 0.324 | 0.775 | +0.000 [-0.008, +0.006] | -0.063 [-0.086, -0.045] |
| HYBRID nu=10: E2 pooled for timing + sd with floor for center offset | 0.328 | 0.774 | +0.004 [-0.004, +0.011] | -0.063 [-0.084, -0.045] |

## changed posture (walking), feature set: timing + center offset

| Detector | EER | FAR @ FRR 5% | dEER vs backend | dFAR vs backend |
|---|---|---|---|---|
| backend (sd with floor) | 0.361 | 0.943 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| E2 per PIN, nu=5 (upper bound) | 0.374 | 0.937 | +0.013 [+0.007, +0.018] | -0.006 [-0.019, +0.007] |
| E2 pooled, nu=5 | 0.350 | 0.935 | -0.011 [-0.018, -0.004] | -0.008 [-0.011, -0.004] |
| E2 pooled, nu=10 | 0.356 | 0.933 | -0.005 [-0.013, +0.003] | -0.011 [-0.014, -0.006] |
| E2 pooled + floor, nu=5 | 0.354 | 0.937 | -0.007 [-0.014, +0.001] | -0.007 [-0.010, -0.003] |
| E2 pooled + floor, nu=10 | 0.360 | 0.935 | -0.000 [-0.009, +0.007] | -0.008 [-0.012, -0.005] |
| HYBRID nu=3: E2 pooled for timing + sd with floor for center offset | 0.364 | 0.943 | +0.003 [-0.001, +0.008] | -0.000 [-0.001, +0.001] |
| HYBRID nu=5: E2 pooled for timing + sd with floor for center offset | 0.365 | 0.943 | +0.005 [+0.000, +0.009] | -0.000 [-0.001, +0.002] |
| HYBRID nu=10: E2 pooled for timing + sd with floor for center offset | 0.367 | 0.943 | +0.006 [+0.001, +0.011] | -0.000 [-0.001, +0.002] |
