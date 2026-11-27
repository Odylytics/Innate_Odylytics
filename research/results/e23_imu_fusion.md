# E23 — PIN + motion. Owner verification on real phone PINs (StrokePIN, 97 people, 6-digit PINs)

Uses the backend's `features.py` + `owner.py`. The impostor **knows the PIN** (another person entering the same PIN). Enrollment k sessions; scores pooled over all (person, PIN) pairs, 95% bootstrap CI by person (100 resamples). Lower is better. Real-person data; each person has one phone, so device differences between people also contribute to the separation.

## k = 3 enrollment sessions

| Feature set | Detector | EER | FAR @ FRR 5% |
|---|---|---|---|
| PIN (timing + offset) | backend (owner.py: floored sd) | 0.166 [0.156, 0.174] | 0.671 [0.587, 0.749] |
| PIN (timing + offset) | Manhattan scaled | 0.236 [0.227, 0.246] | 0.847 [0.790, 0.873] |
| PIN (timing + offset) | E2 shrinkage toward population (nu=5) | 0.196 [0.189, 0.204] | 0.658 [0.612, 0.703] |
| motion only (IMU) | backend (owner.py: floored sd) | 0.068 [0.063, 0.074] | 0.091 [0.080, 0.109] |
| motion only (IMU) | Manhattan scaled | 0.063 [0.058, 0.070] | 0.083 [0.068, 0.100] |
| motion only (IMU) | E2 shrinkage toward population (nu=5) | 0.038 [0.034, 0.045] | 0.029 [0.024, 0.039] |
| PIN + motion (IMU) | backend (owner.py: floored sd) | 0.077 [0.067, 0.083] | 0.230 [0.151, 0.343] |
| PIN + motion (IMU) | Manhattan scaled | 0.099 [0.093, 0.107] | 0.396 [0.329, 0.464] |
| PIN + motion (IMU) | E2 shrinkage toward population (nu=5) | 0.054 [0.049, 0.059] | 0.061 [0.046, 0.089] |

## k = 5 enrollment sessions

| Feature set | Detector | EER | FAR @ FRR 5% |
|---|---|---|---|

## Paired comparison: E2 (shrinkage toward the population) minus the current backend, negative = E2 better

| k | Feature set | dEER | dFAR @ FRR 5% |
|---|---|---|---|
| 3 | PIN (timing + offset) | +0.031 [+0.025, +0.036] | -0.013 [-0.065, +0.032] |
| 3 | motion only (IMU) | -0.030 [-0.038, -0.024] | -0.062 [-0.085, -0.050] |
| 3 | PIN + motion (IMU) | -0.022 [-0.028, -0.017] | -0.170 [-0.271, -0.105] |
