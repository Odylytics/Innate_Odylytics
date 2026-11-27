# E12 — learned owner verification model (StrokePIN, real people)

Split by PERSON (58 training people / 39 test people), 3 splits, averaged. Enrollment k=3 sessions, PIN-knowing impostor. Features = |z| of 24 backend features (touch size REMOVED: device control). The delta columns are relative to the baseline on the same test rows (negative = better); bootstrap CI by person, averaged across splits.

| Model | EER | FAR @ FRR 5% | dEER vs baseline | dFAR vs baseline |
|---|---|---|---|---|
| baseline (mean |z|, backend) | 0.160 | 0.549 | — | — |
| LR with learned weights | 0.188 | 0.546 | +0.028 [+0.018, +0.040] | -0.004 [-0.166, +0.083] |
| learned LightGBM | 0.140 | 0.316 | -0.020 [-0.026, -0.014] | -0.233 [-0.410, -0.134] |

Largest weights learned by LR (first split; positive = a larger |z| raises the likelihood of an impostor; units not normalized across features):

- `pin_hold_3`: +0.497
- `pin_hold_2`: +0.468
- `pin_hold_1`: +0.458
- `pin_hold_5`: +0.456
- `pin_hold_0`: +0.451
- `pin_hold_4`: +0.443
- `pin_flight_2`: +0.398
- `pin_total`: +0.344
