# E29 — E24 on all 97 people (5-fold cross-validation by person) — RULES ONLY, learned models off (fallback mode)

Each fold retrains the two learned models only on people outside that fold. 97 people, at most 6 PINs per person, thresholds A=0.25, B=0.55. Cells: **rate [95% CI, bootstrap over people]**. The PIN-knowing impostor uses a DIFFERENT DEVICE (confounded with device noise); bots are the team's generator. The number of sessions per group is in column n.

## Known recipient

| Group | n | hold | step_up | allow |
|---|---|---|---|---|
| owner | 1164 | 0% [0, 1] | 3% [2, 4] | 96% [95, 98] |
| PIN-knowing impostor (other person, other device) | 2328 | 0% [0, 0] | 11% [9, 12] | 89% [88, 91] |
| bot T1 uniform | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| bot T2 timing noise | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| bot T3 replay ±5% | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| bot T4 population sampling | 1164 | 0% [0, 0] | 18% [16, 20] | 82% [80, 84] |
| replay ±10% | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| replay ±15% | 1164 | 30% [27, 33] | 1% [0, 1] | 69% [66, 72] |
| replay ±20% | 1164 | 1% [0, 1] | 1% [1, 2] | 98% [97, 99] |
| replay ±30% | 1164 | 0% [0, 0] | 1% [1, 2] | 99% [98, 99] |
| template-aware bot (scale 1.0) | 1164 | 0% [0, 1] | 3% [2, 4] | 96% [95, 97] |
| template-aware bot (scale 0.5) | 1164 | 4% [2, 5] | 1% [0, 1] | 96% [94, 97] |

## NEW recipient

| Group | n | hold | step_up | allow |
|---|---|---|---|---|
| owner | 1164 | 1% [0, 1] | 8% [7, 10] | 91% [89, 93] |
| PIN-knowing impostor (other person, other device) | 2328 | 0% [0, 1] | 42% [39, 44] | 58% [55, 60] |
| bot T1 uniform | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| bot T2 timing noise | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| bot T3 replay ±5% | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| bot T4 population sampling | 1164 | 0% [0, 0] | 52% [49, 55] | 48% [45, 51] |
| replay ±10% | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| replay ±15% | 1164 | 30% [27, 33] | 3% [2, 4] | 67% [64, 70] |
| replay ±20% | 1164 | 1% [0, 1] | 4% [3, 5] | 95% [94, 97] |
| replay ±30% | 1164 | 0% [0, 0] | 4% [2, 5] | 96% [95, 98] |
| template-aware bot (scale 1.0) | 1164 | 0% [0, 1] | 7% [5, 9] | 92% [91, 94] |
| template-aware bot (scale 0.5) | 1164 | 4% [2, 5] | 10% [8, 11] | 87% [85, 89] |

## Sweep of threshold A (B=0.55, known recipient): owner allowed / not allowed for ...

| A | owner allow | PIN-knowing impostor | bot T4 | template-aware 1.0 | replay ±15% |
|---|---|---|---|---|---|
| 0.10 | 91% [89, 93] | 42% [40, 45] | 52% [49, 55] | 8% [6, 9] | 33% [30, 36] |
| 0.15 | 94% [92, 95] | 23% [21, 25] | 34% [31, 37] | 6% [5, 8] | 32% [29, 35] |
| 0.20 | 95% [94, 97] | 15% [14, 17] | 25% [22, 27] | 5% [4, 6] | 31% [28, 34] |
| 0.25 ← | 96% [95, 98] | 11% [9, 12] | 18% [16, 20] | 4% [3, 5] | 31% [28, 34] |
| 0.30 | 97% [96, 98] | 8% [7, 10] | 14% [12, 16] | 2% [2, 3] | 31% [28, 34] |
| 0.35 | 99% [99, 100] | 1% [0, 1] | 0% [0, 1] | 0% [0, 1] | 30% [27, 33] |
| 0.40 | 99% [99, 100] | 0% [0, 1] | 0% [0, 0] | 0% [0, 1] | 30% [27, 33] |

## Per-victim distribution (PIN-knowing impostor, known recipient, A=0.25)

Share of PIN-knowing impostor sessions allowed, computed separately for each victim (97 people): median 92%, 90th percentile 96%, maximum 100%.
Gini coefficient 0.04 (0 = even across victims, 1 = concentrated on a few people). Victims allowed > 50%: 97/97; > 90%: 49/97.
