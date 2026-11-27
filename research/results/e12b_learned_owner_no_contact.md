# E12 — learned owner verification model (StrokePIN, real people)

Split by PERSON (58 training people / 39 test people), 3 splits, averaged. Enrollment k=3 sitting sessions, PIN-knowing impostor. Features = |z| of 24 backend features (touch size REMOVED: device control). The delta columns are relative to the baseline on the same test rows (negative = better); bootstrap CI by person, averaged across splits.

| Test posture | Model | EER | FAR @ FRR 5% | dEER vs baseline | dFAR vs baseline |
|---|---|---|---|---|---|
| same (sitting) | baseline (mean |z|, backend) | 0.161 | 0.573 | — | — |
| same (sitting) | LR with learned weights | 0.206 | 0.510 | +0.045 [+0.030, +0.058] | -0.063 [-0.229, +0.057] |
| same (sitting) | learned LightGBM | 0.158 | 0.375 | -0.003 [-0.013, +0.007] | -0.198 [-0.363, -0.085] |
| changed (walking) | baseline (mean |z|, backend) | 0.363 | 0.944 | — | — |
| changed (walking) | LR with learned weights | 0.319 | 0.737 | -0.043 [-0.070, -0.022] | -0.206 [-0.254, -0.149] |
| changed (walking) | learned LightGBM | 0.309 | 0.708 | -0.053 [-0.078, -0.033] | -0.236 [-0.294, -0.184] |

Largest weights learned by LR (first split; positive = a larger |z| raises the likelihood of an impostor; units not normalized across features):

- `pin_hold_0`: +0.288
- `pin_flight_2`: +0.281
- `pin_hold_3`: +0.276
- `pin_hold_5`: +0.273
- `pin_hold_1`: +0.269
- `pin_hold_2`: +0.268
- `pin_hold_4`: +0.259
- `pin_flight_3`: +0.184
