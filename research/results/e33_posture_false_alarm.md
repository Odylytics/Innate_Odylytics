# E33 — false alarms by posture (sitting/walking) and mixed-posture enrollment (StrokePIN)

False alarm = the real owner is NOT `allow`ed (gets `step_up` or `hold`). Leak = the PIN-knowing impostor is `allow`ed. Fixed test set for every enrollment scheme (owner: 2 sitting + 2 walking; PIN-knowing impostor: 3 sitting + 3 walking, other device). Thresholds A=0.25, B=0.55. 95% CI by bootstrap over people.

## full: all learned models, people never seen (10 people)

### Known recipient

| Enrollment | Sitting owner: false alarm | Sitting owner: held | Walking owner: false alarm | Walking owner: held | of which held as 'bot-like' (walking) | Sitting PIN-knowing impostor: leak | Walking PIN-knowing impostor: leak |
|---|---|---|---|---|---|---|---|
| sitting 3 (current ~ app) | 17% [11, 23] | 0% [0, 1] | 41% [31, 50] | 1% [0, 1] | 1% [0, 1] | 24% [21, 27] | 31% [27, 35] |
| walking 3 | 36% [28, 44] | 0% [0, 1] | 16% [11, 21] | 1% [0, 1] | 1% [0, 1] | 30% [28, 32] | 37% [31, 42] |
| sitting 2 + walking 1 (k=3) | 19% [13, 25] | 0% [0, 1] | 23% [15, 31] | 1% [0, 1] | 1% [0, 1] | 32% [28, 37] | 38% [34, 43] |
| sitting 2 + walking 2 (k=4) | 20% [13, 27] | 0% [0, 1] | 18% [12, 24] | 1% [0, 1] | 1% [0, 1] | 34% [30, 38] | 39% [35, 43] |
| sitting 3 + walking 1 (k=4) | 17% [11, 23] | 0% [0, 1] | 28% [20, 37] | 1% [0, 1] | 1% [0, 1] | 29% [26, 34] | 35% [31, 39] |
| sitting 3 + walking 3 (k=6) | 18% [12, 25] | 0% [0, 1] | 19% [12, 25] | 1% [0, 1] | 1% [0, 1] | 33% [29, 38] | 40% [35, 43] |

### NEW recipient

| Enrollment | Sitting owner: false alarm | Walking owner: false alarm | PIN-knowing impostor (sitting+walking): leak |
|---|---|---|---|
| sitting 3 (current ~ app) | 84% [78, 89] | 98% [98, 99] | 0% [0, 0] |
| walking 3 | 98% [95, 99] | 85% [78, 91] | 0% [0, 1] |
| sitting 2 + walking 1 (k=3) | 88% [83, 92] | 95% [92, 97] | 0% [0, 1] |
| sitting 2 + walking 2 (k=4) | 90% [86, 95] | 93% [88, 97] | 1% [0, 1] |
| sitting 3 + walking 1 (k=4) | 84% [78, 88] | 97% [94, 99] | 0% [0, 0] |
| sitting 3 + walking 3 (k=6) | 89% [85, 93] | 93% [90, 96] | 0% [0, 1] |

## rules: learned models off, everyone (96 people)

### Known recipient

| Enrollment | Sitting owner: false alarm | Sitting owner: held | Walking owner: false alarm | Walking owner: held | of which held as 'bot-like' (walking) | Sitting PIN-knowing impostor: leak | Walking PIN-knowing impostor: leak |
|---|---|---|---|---|---|---|---|
| sitting 3 (current ~ app) | 4% [3, 5] | 0% [0, 0] | 11% [9, 12] | 0% [0, 0] | 0% [0, 0] | 90% [89, 91] | 85% [84, 86] |
| walking 3 | 7% [6, 9] | 0% [0, 0] | 5% [4, 6] | 0% [0, 0] | 0% [0, 0] | 89% [88, 90] | 86% [85, 87] |
| sitting 2 + walking 1 (k=3) | 4% [3, 4] | 0% [0, 0] | 7% [6, 8] | 0% [0, 0] | 0% [0, 0] | 92% [91, 93] | 88% [87, 89] |
| sitting 2 + walking 2 (k=4) | 3% [2, 4] | 0% [0, 0] | 5% [4, 6] | 0% [0, 0] | 0% [0, 0] | 93% [92, 94] | 89% [88, 91] |
| sitting 3 + walking 1 (k=4) | 3% [2, 4] | 0% [0, 0] | 6% [5, 7] | 0% [0, 0] | 0% [0, 0] | 93% [92, 94] | 89% [87, 90] |
| sitting 3 + walking 3 (k=6) | 2% [2, 3] | 0% [0, 0] | 4% [3, 4] | 0% [0, 0] | 0% [0, 0] | 94% [93, 95] | 91% [89, 92] |

### NEW recipient

| Enrollment | Sitting owner: false alarm | Walking owner: false alarm | PIN-knowing impostor (sitting+walking): leak |
|---|---|---|---|
| sitting 3 (current ~ app) | 9% [8, 10] | 25% [21, 29] | 57% [55, 59] |
| walking 3 | 22% [19, 26] | 9% [7, 10] | 61% [59, 64] |
| sitting 2 + walking 1 (k=3) | 9% [7, 10] | 11% [10, 13] | 70% [68, 72] |
| sitting 2 + walking 2 (k=4) | 8% [7, 9] | 8% [7, 9] | 74% [72, 75] |
| sitting 3 + walking 1 (k=4) | 8% [7, 9] | 10% [9, 12] | 71% [69, 72] |
| sitting 3 + walking 3 (k=6) | 7% [6, 8] | 7% [6, 8] | 76% [74, 77] |

