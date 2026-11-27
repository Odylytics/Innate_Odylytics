# E23 — PIN + motion. Owner verification on real phone PINs (StrokePIN, 97 people, 6-digit PINs)

Uses the backend's `features.py` + `owner.py`. The impostor **knows the PIN** (another person entering the same PIN). Enrollment k sitting sessions; scores pooled over all (person, PIN) pairs, 95% bootstrap CI by person (100 resamples). Lower is better. Real-person data; each person has one phone, so device differences between people also contribute to the separation.

## k = 3 enrollment sessions, test same posture (sitting)

| Feature set | Detector | EER | FAR @ FRR 5% |
|---|---|---|---|
| PIN (timing + offset) | backend (owner.py: floored sd) | 0.166 [0.156, 0.176] | 0.752 [0.658, 0.846] |
| PIN (timing + offset) | Manhattan scaled | 0.235 [0.224, 0.242] | 0.870 [0.833, 0.894] |
| PIN (timing + offset) | E2 shrinkage toward population (nu=5) | 0.197 [0.185, 0.206] | 0.692 [0.628, 0.755] |
| motion only (IMU) | backend (owner.py: floored sd) | 0.070 [0.064, 0.075] | 0.096 [0.083, 0.110] |
| motion only (IMU) | Manhattan scaled | 0.063 [0.058, 0.070] | 0.080 [0.068, 0.098] |
| motion only (IMU) | E2 shrinkage toward population (nu=5) | 0.038 [0.032, 0.044] | 0.030 [0.022, 0.040] |
| PIN + motion (IMU) | backend (owner.py: floored sd) | 0.081 [0.074, 0.088] | 0.309 [0.201, 0.463] |
| PIN + motion (IMU) | Manhattan scaled | 0.103 [0.095, 0.110] | 0.445 [0.374, 0.535] |
| PIN + motion (IMU) | E2 shrinkage toward population (nu=5) | 0.057 [0.051, 0.061] | 0.075 [0.055, 0.093] |

## k = 3 enrollment sessions, test changed posture (walking)

| Feature set | Detector | EER | FAR @ FRR 5% |
|---|---|---|---|
| PIN (timing + offset) | backend (owner.py: floored sd) | 0.362 [0.337, 0.382] | 0.943 [0.930, 0.952] |
| PIN (timing + offset) | Manhattan scaled | 0.399 [0.386, 0.417] | 0.935 [0.925, 0.944] |
| PIN (timing + offset) | E2 shrinkage toward population (nu=5) | 0.374 [0.355, 0.392] | 0.936 [0.920, 0.949] |
| motion only (IMU) | backend (owner.py: floored sd) | 0.476 [0.460, 0.487] | 0.944 [0.932, 0.951] |
| motion only (IMU) | Manhattan scaled | 0.460 [0.448, 0.478] | 0.947 [0.929, 0.960] |
| motion only (IMU) | E2 shrinkage toward population (nu=5) | 0.441 [0.420, 0.467] | 0.913 [0.865, 0.968] |
| PIN + motion (IMU) | backend (owner.py: floored sd) | 0.459 [0.446, 0.471] | 0.942 [0.928, 0.950] |
| PIN + motion (IMU) | Manhattan scaled | 0.445 [0.431, 0.461] | 0.948 [0.929, 0.964] |
| PIN + motion (IMU) | E2 shrinkage toward population (nu=5) | 0.420 [0.393, 0.439] | 0.910 [0.868, 0.954] |

## k = 5 enrollment sessions, test same posture (sitting)

| Feature set | Detector | EER | FAR @ FRR 5% |
|---|---|---|---|

## k = 5 enrollment sessions, test changed posture (walking)

| Feature set | Detector | EER | FAR @ FRR 5% |
|---|---|---|---|
| PIN (timing + offset) | backend (owner.py: floored sd) | 0.354 [0.338, 0.375] | 0.935 [0.922, 0.949] |
| PIN (timing + offset) | Manhattan scaled | 0.372 [0.356, 0.392] | 0.935 [0.920, 0.947] |
| PIN (timing + offset) | E2 shrinkage toward population (nu=5) | 0.364 [0.345, 0.383] | 0.932 [0.923, 0.946] |
| motion only (IMU) | backend (owner.py: floored sd) | 0.471 [0.456, 0.484] | 0.945 [0.932, 0.955] |
| motion only (IMU) | Manhattan scaled | 0.453 [0.434, 0.470] | 0.943 [0.924, 0.960] |
| motion only (IMU) | E2 shrinkage toward population (nu=5) | 0.440 [0.417, 0.462] | 0.920 [0.885, 0.969] |
| PIN + motion (IMU) | backend (owner.py: floored sd) | 0.451 [0.436, 0.465] | 0.942 [0.923, 0.951] |
| PIN + motion (IMU) | Manhattan scaled | 0.438 [0.422, 0.456] | 0.944 [0.922, 0.962] |
| PIN + motion (IMU) | E2 shrinkage toward population (nu=5) | 0.417 [0.395, 0.442] | 0.915 [0.856, 0.959] |

## Paired comparison: E2 (shrinkage toward the population) minus the current backend, negative = E2 better

| k | Test | Feature set | dEER | dFAR @ FRR 5% |
|---|---|---|---|---|
| 3 | same posture (sitting) | PIN (timing + offset) | +0.031 [+0.025, +0.036] | -0.060 [-0.101, -0.016] |
| 3 | same posture (sitting) | motion only (IMU) | -0.031 [-0.039, -0.025] | -0.066 [-0.086, -0.052] |
| 3 | same posture (sitting) | PIN + motion (IMU) | -0.024 [-0.027, -0.020] | -0.235 [-0.345, -0.144] |
| 3 | changed posture (walking) | PIN (timing + offset) | +0.012 [+0.007, +0.018] | -0.007 [-0.019, +0.006] |
| 3 | changed posture (walking) | motion only (IMU) | -0.035 [-0.047, -0.019] | -0.032 [-0.069, +0.018] |
| 3 | changed posture (walking) | PIN + motion (IMU) | -0.039 [-0.054, -0.024] | -0.032 [-0.064, +0.002] |
| 5 | changed posture (walking) | PIN (timing + offset) | +0.009 [+0.004, +0.014] | -0.003 [-0.015, +0.008] |
| 5 | changed posture (walking) | motion only (IMU) | -0.031 [-0.049, -0.014] | -0.025 [-0.069, +0.016] |
| 5 | changed posture (walking) | PIN + motion (IMU) | -0.034 [-0.045, -0.020] | -0.027 [-0.067, +0.017] |
