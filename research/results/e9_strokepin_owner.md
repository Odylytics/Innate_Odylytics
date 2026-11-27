# E9 — owner verification on real phone PINs (StrokePIN, 97 people, 6-digit PIN)

Uses the backend's `features.py` + `owner.py`. The impostor **knows the PIN** (another person enters the same PIN). Enrollment on k sessions; scores pooled over all (person, PIN) pairs, 95% CI by bootstrap over people (100 resamples). Lower is better. Real-human data; each person has one phone, so device differences between people also contribute to the separation.

## k = 3 enrollment sessions

| Feature set | Detector | EER | FAR @ FRR 5% |
|---|---|---|---|
| timing | backend (owner.py: sd with floor) | 0.201 [0.193, 0.209] | 0.686 [0.647, 0.719] |
| timing | Manhattan scaled | 0.265 [0.256, 0.272] | 0.784 [0.760, 0.803] |
| timing | E2 shrinkage toward population (nu=5) | 0.199 [0.190, 0.207] | 0.565 [0.531, 0.588] |
| timing + center offset | backend (owner.py: sd with floor) | 0.166 [0.157, 0.174] | 0.671 [0.601, 0.757] |
| timing + center offset | Manhattan scaled | 0.236 [0.225, 0.246] | 0.847 [0.798, 0.879] |
| timing + center offset | E2 shrinkage toward population (nu=5) | 0.196 [0.185, 0.206] | 0.658 [0.607, 0.705] |
| timing + center offset + touch size | backend (owner.py: sd with floor) | 0.155 [0.145, 0.164] | 0.656 [0.575, 0.747] |
| timing + center offset + touch size | Manhattan scaled | 0.230 [0.221, 0.239] | 0.914 [0.896, 0.926] |
| timing + center offset + touch size | E2 shrinkage toward population (nu=5) | 0.159 [0.150, 0.169] | 0.538 [0.484, 0.610] |

## k = 5 enrollment sessions

| Feature set | Detector | EER | FAR @ FRR 5% |
|---|---|---|---|

## Paired comparison: E2 (shrinkage toward population) minus current backend, negative = E2 is better

| k | Feature set | dEER | dFAR @ FRR 5% |
|---|---|---|---|
| 3 | timing | -0.002 [-0.007, +0.003] | -0.121 [-0.145, -0.095] |
| 3 | timing + center offset | +0.031 [+0.025, +0.036] | -0.013 [-0.058, +0.031] |
| 3 | timing + center offset + touch size | +0.003 [-0.001, +0.008] | -0.118 [-0.160, -0.072] |
