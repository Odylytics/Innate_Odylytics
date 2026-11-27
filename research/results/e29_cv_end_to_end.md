# E29 — E24 on all 97 people (5-fold cross-validation by person)

Each fold retrains the two learned models only on people outside that fold. 97 people, at most 6 PINs per person, thresholds A=0.25, B=0.55. Cells: **rate [95% CI, bootstrap over people]**. The PIN-knowing impostor uses a DIFFERENT DEVICE (confounded with device noise); bots are the team's generator. The number of sessions per group is in column n.

## Known recipient

| Group | n | hold | step_up | allow |
|---|---|---|---|---|
| owner, same posture (sitting) | 1164 | 1% [0, 1] | 23% [20, 26] | 76% [73, 79] |
| owner, changed posture (walking) | 2287 | 1% [0, 1] | 50% [46, 54] | 49% [45, 53] |
| PIN-knowing impostor (other person, other device) | 2328 | 1% [1, 2] | 77% [75, 79] | 22% [20, 24] |
| bot T1 uniform | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| bot T2 timing noise | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| bot T3 replay ±5% | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| bot T4 population sampling | 1164 | 32% [28, 35] | 65% [62, 69] | 3% [2, 4] |
| replay ±10% | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| replay ±15% | 1164 | 29% [27, 31] | 20% [18, 23] | 51% [48, 54] |
| replay ±20% | 1164 | 3% [2, 4] | 39% [35, 42] | 58% [55, 62] |
| replay ±30% | 1164 | 6% [4, 7] | 62% [59, 66] | 32% [28, 35] |
| template-aware bot (scale 1.0) | 1164 | 4% [2, 5] | 24% [21, 27] | 72% [69, 76] |
| template-aware bot (scale 0.5) | 1164 | 5% [3, 6] | 9% [7, 10] | 87% [84, 89] |

## NEW recipient

| Group | n | hold | step_up | allow |
|---|---|---|---|---|
| owner, same posture (sitting) | 1164 | 2% [2, 3] | 91% [89, 92] | 7% [5, 8] |
| owner, changed posture (walking) | 2287 | 5% [4, 7] | 94% [93, 95] | 1% [0, 1] |
| PIN-knowing impostor (other person, other device) | 2328 | 18% [16, 20] | 82% [80, 84] | 0% [0, 0] |
| bot T1 uniform | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| bot T2 timing noise | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| bot T3 replay ±5% | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| bot T4 population sampling | 1164 | 68% [65, 71] | 32% [29, 35] | 0% [0, 0] |
| replay ±10% | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| replay ±15% | 1164 | 30% [28, 33] | 67% [65, 70] | 2% [2, 4] |
| replay ±20% | 1164 | 6% [5, 8] | 93% [91, 94] | 1% [1, 2] |
| replay ±30% | 1164 | 14% [12, 17] | 86% [83, 88] | 0% [0, 0] |
| template-aware bot (scale 1.0) | 1164 | 5% [3, 6] | 90% [88, 92] | 6% [4, 7] |
| template-aware bot (scale 0.5) | 1164 | 5% [3, 6] | 74% [70, 77] | 22% [19, 26] |

## Sweep of threshold A (B=0.55, known recipient): sitting owner allowed / not allowed for ...

| A | sitting owner allow | PIN-knowing impostor | bot T4 | template-aware 1.0 | replay ±15% |
|---|---|---|---|---|---|
| 0.10 | 7% [5, 8] | 100% [100, 100] | 100% [100, 100] | 94% [93, 96] | 98% [96, 98] |
| 0.15 | 28% [25, 32] | 99% [99, 100] | 100% [100, 100] | 71% [68, 75] | 86% [83, 88] |
| 0.20 | 53% [49, 57] | 95% [94, 96] | 100% [100, 100] | 47% [43, 51] | 67% [64, 70] |
| 0.25 ← | 76% [73, 79] | 78% [76, 80] | 97% [96, 98] | 28% [24, 31] | 49% [46, 52] |
| 0.30 | 89% [87, 91] | 58% [55, 61] | 91% [90, 93] | 16% [13, 18] | 39% [36, 42] |
| 0.35 | 95% [94, 96] | 39% [36, 41] | 81% [79, 83] | 8% [6, 10] | 33% [31, 35] |
| 0.40 | 98% [97, 98] | 18% [16, 20] | 68% [65, 71] | 5% [3, 6] | 30% [28, 33] |

## Per-victim distribution (PIN-knowing impostor, known recipient, A=0.25)

Share of PIN-knowing impostor sessions allowed, computed separately for each victim (97 people): median 21%, 90th percentile 33%, maximum 58%.
Gini coefficient 0.28 (0 = even across victims, 1 = concentrated on a few people). Victims allowed > 50%: 1/97; > 90%: 0/97.
