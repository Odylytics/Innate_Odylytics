# E29 — E24 on all 97 people (5-fold cross-validation by person) — RULES ONLY, learned models off (fallback mode)

Each fold retrains the two learned models only on people outside that fold. 97 people, at most 6 PINs per person, thresholds A=0.25, B=0.55. Cells: **rate [95% CI, bootstrap over people]**. The PIN-knowing impostor uses a DIFFERENT DEVICE (confounded with device noise); bots are the team's generator. The number of sessions per group is in column n.

## Known recipient

| Group | n | hold | step_up | allow |
|---|---|---|---|---|
| owner, same posture (sitting) | 1164 | 1% [0, 1] | 4% [3, 6] | 95% [94, 96] |
| owner, changed posture (walking) | 2287 | 0% [0, 0] | 13% [11, 16] | 87% [84, 89] |
| PIN-knowing impostor (other person, other device) | 2328 | 0% [0, 0] | 10% [9, 12] | 89% [88, 91] |
| bot T1 uniform | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| bot T2 timing noise | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| bot T3 replay ±5% | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| bot T4 population sampling | 1164 | 0% [0, 0] | 22% [19, 25] | 78% [75, 81] |
| replay ±10% | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| replay ±15% | 1164 | 27% [25, 30] | 1% [0, 1] | 72% [70, 74] |
| replay ±20% | 1164 | 1% [0, 1] | 1% [0, 1] | 98% [98, 99] |
| replay ±30% | 1164 | 0% [0, 0] | 1% [0, 2] | 99% [98, 100] |
| template-aware bot (scale 1.0) | 1164 | 1% [0, 1] | 5% [3, 6] | 95% [93, 96] |
| template-aware bot (scale 0.5) | 1164 | 2% [1, 4] | 2% [2, 4] | 95% [94, 96] |

## NEW recipient

| Group | n | hold | step_up | allow |
|---|---|---|---|---|
| owner, same posture (sitting) | 1164 | 1% [0, 1] | 9% [7, 10] | 91% [89, 93] |
| owner, changed posture (walking) | 2287 | 1% [0, 1] | 29% [25, 34] | 70% [66, 75] |
| PIN-knowing impostor (other person, other device) | 2328 | 1% [0, 1] | 39% [36, 41] | 61% [59, 64] |
| bot T1 uniform | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| bot T2 timing noise | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| bot T3 replay ±5% | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| bot T4 population sampling | 1164 | 0% [0, 0] | 58% [55, 62] | 41% [38, 45] |
| replay ±10% | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| replay ±15% | 1164 | 27% [25, 30] | 2% [1, 3] | 71% [68, 73] |
| replay ±20% | 1164 | 1% [0, 1] | 2% [2, 3] | 97% [96, 98] |
| replay ±30% | 1164 | 0% [0, 0] | 3% [2, 4] | 97% [96, 98] |
| template-aware bot (scale 1.0) | 1164 | 1% [0, 1] | 9% [7, 11] | 90% [88, 92] |
| template-aware bot (scale 0.5) | 1164 | 2% [1, 4] | 13% [11, 16] | 84% [81, 87] |

## Sweep of threshold A (B=0.55, known recipient): sitting owner allowed / not allowed for ...

| A | sitting owner allow | PIN-knowing impostor | bot T4 | template-aware 1.0 | replay ±15% |
|---|---|---|---|---|---|
| 0.10 | 91% [89, 93] | 39% [36, 41] | 59% [55, 62] | 10% [8, 12] | 29% [27, 32] |
| 0.15 | 93% [92, 95] | 22% [20, 25] | 39% [36, 42] | 8% [6, 9] | 28% [26, 31] |
| 0.20 | 94% [93, 96] | 15% [13, 16] | 30% [27, 33] | 7% [5, 8] | 28% [26, 31] |
| 0.25 ← | 95% [94, 96] | 11% [9, 12] | 22% [19, 25] | 5% [4, 7] | 28% [26, 30] |
| 0.30 | 96% [95, 97] | 8% [7, 9] | 16% [14, 19] | 4% [3, 5] | 28% [26, 30] |
| 0.35 | 99% [99, 100] | 1% [1, 2] | 0% [0, 0] | 1% [0, 1] | 27% [25, 30] |
| 0.40 | 99% [99, 100] | 1% [0, 1] | 0% [0, 0] | 1% [0, 1] | 27% [25, 30] |

## Per-victim distribution (PIN-knowing impostor, known recipient, A=0.25)

Share of PIN-knowing impostor sessions allowed, computed separately for each victim (97 people): median 92%, 90th percentile 100%, maximum 100%.
Gini coefficient 0.05 (0 = even across victims, 1 = concentrated on a few people). Victims allowed > 50%: 97/97; > 90%: 54/97.
