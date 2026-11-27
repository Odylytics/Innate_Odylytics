# E9 — owner verification on real phone PINs (StrokePIN, 97 people, 6-digit PIN)

Uses the backend's `features.py` + `owner.py`. The impostor **knows the PIN** (another person enters the same PIN). Enrollment on k sitting sessions; scores pooled over all (person, PIN) pairs, 95% CI by bootstrap over people (100 resamples). Lower is better. Real-human data; each person has one phone, so device differences between people also contribute to the separation.

## k = 3 enrollment sessions, tested on same posture (sitting)

| Feature set | Detector | EER | FAR @ FRR 5% |
|---|---|---|---|
| timing | backend (owner.py: sd with floor) | 0.201 [0.192, 0.211] | 0.710 [0.669, 0.746] |
| timing | Manhattan scaled | 0.264 [0.257, 0.273] | 0.799 [0.778, 0.816] |
| timing | E2 shrinkage toward population (nu=5) | 0.200 [0.190, 0.209] | 0.570 [0.535, 0.606] |
| timing + center offset | backend (owner.py: sd with floor) | 0.166 [0.156, 0.175] | 0.752 [0.661, 0.832] |
| timing + center offset | Manhattan scaled | 0.235 [0.228, 0.244] | 0.870 [0.841, 0.894] |
| timing + center offset | E2 shrinkage toward population (nu=5) | 0.197 [0.186, 0.209] | 0.692 [0.634, 0.750] |
| timing + center offset + touch size | backend (owner.py: sd with floor) | 0.157 [0.148, 0.167] | 0.740 [0.645, 0.837] |
| timing + center offset + touch size | Manhattan scaled | 0.229 [0.220, 0.238] | 0.915 [0.903, 0.925] |
| timing + center offset + touch size | E2 shrinkage toward population (nu=5) | 0.161 [0.150, 0.170] | 0.581 [0.512, 0.650] |

## k = 3 enrollment sessions, tested on changed posture (walking)

| Feature set | Detector | EER | FAR @ FRR 5% |
|---|---|---|---|
| timing | backend (owner.py: sd with floor) | 0.323 [0.309, 0.336] | 0.839 [0.817, 0.861] |
| timing | Manhattan scaled | 0.365 [0.355, 0.377] | 0.890 [0.879, 0.902] |
| timing | E2 shrinkage toward population (nu=5) | 0.318 [0.305, 0.333] | 0.763 [0.731, 0.790] |
| timing + center offset | backend (owner.py: sd with floor) | 0.362 [0.344, 0.381] | 0.943 [0.931, 0.952] |
| timing + center offset | Manhattan scaled | 0.399 [0.384, 0.413] | 0.935 [0.926, 0.944] |
| timing + center offset | E2 shrinkage toward population (nu=5) | 0.374 [0.351, 0.389] | 0.936 [0.921, 0.951] |
| timing + center offset + touch size | backend (owner.py: sd with floor) | 0.353 [0.335, 0.378] | 0.942 [0.930, 0.953] |
| timing + center offset + touch size | Manhattan scaled | 0.390 [0.375, 0.408] | 0.944 [0.939, 0.947] |
| timing + center offset + touch size | E2 shrinkage toward population (nu=5) | 0.342 [0.319, 0.363] | 0.925 [0.905, 0.944] |

## k = 5 enrollment sessions, tested on same posture (sitting)

| Feature set | Detector | EER | FAR @ FRR 5% |
|---|---|---|---|

## k = 5 enrollment sessions, tested on changed posture (walking)

| Feature set | Detector | EER | FAR @ FRR 5% |
|---|---|---|---|
| timing | backend (owner.py: sd with floor) | 0.315 [0.299, 0.332] | 0.826 [0.795, 0.856] |
| timing | Manhattan scaled | 0.328 [0.314, 0.346] | 0.846 [0.811, 0.873] |
| timing | E2 shrinkage toward population (nu=5) | 0.309 [0.293, 0.327] | 0.752 [0.706, 0.786] |
| timing + center offset | backend (owner.py: sd with floor) | 0.354 [0.338, 0.374] | 0.935 [0.918, 0.950] |
| timing + center offset | Manhattan scaled | 0.372 [0.354, 0.386] | 0.935 [0.920, 0.949] |
| timing + center offset | E2 shrinkage toward population (nu=5) | 0.364 [0.347, 0.382] | 0.932 [0.921, 0.943] |
| timing + center offset + touch size | backend (owner.py: sd with floor) | 0.344 [0.321, 0.365] | 0.935 [0.920, 0.948] |
| timing + center offset + touch size | Manhattan scaled | 0.353 [0.334, 0.370] | 0.937 [0.921, 0.946] |
| timing + center offset + touch size | E2 shrinkage toward population (nu=5) | 0.332 [0.313, 0.354] | 0.922 [0.909, 0.940] |

## Paired comparison: E2 (shrinkage toward population) minus current backend, negative = E2 is better

| k | Test | Feature set | dEER | dFAR @ FRR 5% |
|---|---|---|---|---|
| 3 | same posture (sitting) | timing | -0.001 [-0.005, +0.004] | -0.140 [-0.161, -0.107] |
| 3 | same posture (sitting) | timing + center offset | +0.031 [+0.026, +0.037] | -0.060 [-0.095, -0.017] |
| 3 | same posture (sitting) | timing + center offset + touch size | +0.005 [+0.000, +0.009] | -0.159 [-0.198, -0.117] |
| 3 | changed posture (walking) | timing | -0.004 [-0.010, +0.001] | -0.076 [-0.097, -0.055] |
| 3 | changed posture (walking) | timing + center offset | +0.012 [+0.007, +0.018] | -0.007 [-0.015, +0.007] |
| 3 | changed posture (walking) | timing + center offset + touch size | -0.011 [-0.020, -0.003] | -0.018 [-0.031, -0.004] |
| 5 | changed posture (walking) | timing | -0.006 [-0.014, +0.002] | -0.074 [-0.100, -0.051] |
| 5 | changed posture (walking) | timing + center offset | +0.009 [+0.003, +0.016] | -0.003 [-0.015, +0.009] |
| 5 | changed posture (walking) | timing + center offset + touch size | -0.012 [-0.024, -0.002] | -0.012 [-0.027, -0.000] |
