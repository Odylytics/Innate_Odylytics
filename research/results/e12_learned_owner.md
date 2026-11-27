# E12 — learned owner verification model (StrokePIN, real people)

Split by PERSON (58 training people / 39 test people), 3 splits, averaged. Enrollment k=3 sessions, PIN-knowing impostor. Features = |z| of 26 backend features. The delta columns are relative to the baseline on the same test rows (negative = better); bootstrap CI by person, averaged across splits.

| Model | EER | FAR @ FRR 5% | dEER vs baseline | dFAR vs baseline |
|---|---|---|---|---|
| baseline (mean |z|, backend) | 0.149 | 0.528 | — | — |
| LR with learned weights | 0.129 | 0.300 | -0.020 [-0.031, -0.006] | -0.228 [-0.409, -0.121] |
| learned LightGBM | 0.097 | 0.171 | -0.052 [-0.061, -0.043] | -0.357 [-0.540, -0.245] |

Largest weights learned by LR (first split; positive = a larger |z| raises the likelihood of an impostor; units not normalized across features):

- `tap_w_mean`: +2.753
- `tap_h_mean`: +2.649
- `pin_hold_3`: +0.497
- `pin_hold_2`: +0.471
- `pin_hold_0`: +0.456
- `pin_hold_4`: +0.437
- `pin_hold_1`: +0.436
- `pin_hold_5`: +0.419
