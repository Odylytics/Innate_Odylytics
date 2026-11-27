# E29 — E24 on all 97 people (5-fold cross-validation by person)

Each fold retrains the two learned models only on people outside that fold. 97 people, at most 6 PINs per person, thresholds A=0.25, B=0.55. Cells: **rate [95% CI, bootstrap over people]**. The PIN-knowing impostor uses a DIFFERENT DEVICE (confounded with device noise); bots are the team's generator. The number of sessions per group is in column n.

## Known recipient

| Group | n | hold | step_up | allow |
|---|---|---|---|---|
| owner | 1164 | 1% [1, 2] | 22% [19, 25] | 77% [74, 80] |
| PIN-knowing impostor (other person, other device) | 2328 | 1% [1, 2] | 82% [80, 84] | 17% [15, 19] |
| bot T1 uniform | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| bot T2 timing noise | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| bot T3 replay ±5% | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| bot T4 population sampling | 1164 | 34% [32, 37] | 63% [61, 66] | 2% [2, 3] |
| replay ±10% | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| replay ±15% | 1164 | 32% [29, 35] | 20% [17, 22] | 49% [45, 52] |
| replay ±20% | 1164 | 4% [3, 6] | 39% [37, 42] | 56% [53, 59] |
| replay ±30% | 1164 | 8% [6, 10] | 65% [61, 69] | 27% [24, 31] |
| template-aware bot (scale 1.0) | 1164 | 4% [3, 6] | 19% [16, 22] | 77% [73, 80] |
| template-aware bot (scale 0.5) | 1164 | 5% [4, 7] | 6% [4, 7] | 89% [87, 91] |

## NEW recipient

| Group | n | hold | step_up | allow |
|---|---|---|---|---|
| owner | 1164 | 3% [2, 4] | 82% [79, 84] | 15% [13, 18] |
| PIN-knowing impostor (other person, other device) | 2328 | 28% [25, 30] | 72% [70, 74] | 0% [0, 0] |
| bot T1 uniform | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| bot T2 timing noise | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| bot T3 replay ±5% | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| bot T4 population sampling | 1164 | 73% [70, 76] | 27% [24, 30] | 0% [0, 0] |
| replay ±10% | 1164 | 100% [100, 100] | 0% [0, 0] | 0% [0, 0] |
| replay ±15% | 1164 | 34% [30, 36] | 60% [57, 63] | 7% [5, 8] |
| replay ±20% | 1164 | 9% [7, 11] | 87% [85, 89] | 5% [4, 6] |
| replay ±30% | 1164 | 21% [18, 24] | 79% [76, 81] | 1% [0, 1] |
| template-aware bot (scale 1.0) | 1164 | 6% [4, 7] | 77% [73, 80] | 18% [15, 20] |
| template-aware bot (scale 0.5) | 1164 | 6% [4, 7] | 54% [51, 58] | 40% [36, 44] |

## Sweep of threshold A (B=0.55, known recipient): owner allowed / not allowed for ...

| A | owner allow | PIN-knowing impostor | bot T4 | template-aware 1.0 | replay ±15% |
|---|---|---|---|---|---|
| 0.10 | 15% [13, 18] | 100% [100, 100] | 100% [100, 100] | 82% [80, 85] | 93% [92, 95] |
| 0.15 | 36% [32, 39] | 99% [99, 99] | 100% [100, 100] | 59% [56, 63] | 79% [77, 82] |
| 0.20 | 55% [51, 58] | 96% [95, 97] | 100% [99, 100] | 38% [35, 42] | 67% [64, 70] |
| 0.25 ← | 77% [74, 80] | 83% [81, 85] | 98% [97, 98] | 23% [20, 27] | 51% [48, 55] |
| 0.30 | 89% [87, 91] | 67% [65, 70] | 91% [89, 93] | 14% [12, 16] | 42% [38, 45] |
| 0.35 | 95% [93, 96] | 52% [49, 55] | 84% [82, 87] | 8% [6, 9] | 36% [32, 39] |
| 0.40 | 97% [96, 98] | 28% [25, 30] | 73% [70, 76] | 6% [4, 7] | 34% [30, 36] |

## Per-victim distribution (PIN-knowing impostor, known recipient, A=0.25)

Share of PIN-knowing impostor sessions allowed, computed separately for each victim (97 people): median 17%, 90th percentile 29%, maximum 46%.
Gini coefficient 0.33 (0 = even across victims, 1 = concentrated on a few people). Victims allowed > 50%: 0/97; > 90%: 0/97.
