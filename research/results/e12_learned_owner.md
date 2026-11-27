# E12 — learned owner verification model (StrokePIN, real people)

Split by PERSON (58 training people / 39 test people), 3 splits, averaged. Enrollment k=3 sitting sessions, PIN-knowing impostor. Features = |z| of 31 backend features. The delta columns are relative to the baseline on the same test rows (negative = better); bootstrap CI by person, averaged across splits.

| Test posture | Model | EER | FAR @ FRR 5% | dEER vs baseline | dFAR vs baseline |
|---|---|---|---|---|---|
| same (sitting) | baseline (mean |z|, backend) | 0.149 | 0.558 | — | — |
| same (sitting) | LR with learned weights | 0.135 | 0.296 | -0.014 [-0.027, -0.001] | -0.261 [-0.440, -0.138] |
| same (sitting) | learned LightGBM | 0.108 | 0.200 | -0.041 [-0.055, -0.030] | -0.358 [-0.540, -0.240] |
| changed (walking) | baseline (mean |z|, backend) | 0.354 | 0.943 | — | — |
| changed (walking) | LR with learned weights | 0.273 | 0.738 | -0.081 [-0.108, -0.052] | -0.205 [-0.352, -0.121] |
| changed (walking) | learned LightGBM | 0.264 | 0.675 | -0.090 [-0.120, -0.059] | -0.268 [-0.370, -0.195] |

Largest weights learned by LR (first split; positive = a larger |z| raises the likelihood of an impostor; units not normalized across features):

- `tap_w_mean`: +1.382
- `tap_h_mean`: +1.016
- `pin_hold_0`: +0.288
- `pin_hold_2`: +0.256
- `pin_hold_3`: +0.254
- `pin_flight_2`: +0.250
- `pin_hold_1`: +0.246
- `pin_hold_4`: +0.245
