# E13 — the "Innate Challenge" hypothesis: do more characters give better owner recognition and bot detection?

Real people typing sentences on a phone (Aalto), timing only. Each sentence is cut at the first n keys (n = 6 is equivalent to the length of a 6-digit PIN). Every n uses the same sentences. **Absolute numbers cannot be compared with StrokePIN** (different data, different measurements: here there is no key hold time and no coordinates).

## (1) Owner verification by number of keys

| Number of keys n | EER | FAR @ FRR 5% |
|---|---|---|
| 6 | 0.364 [0.355, 0.371] | 0.807 [0.787, 0.822] |
| 10 | 0.337 [0.330, 0.345] | 0.733 [0.714, 0.761] |
| 20 | 0.279 [0.272, 0.289] | 0.591 [0.566, 0.616] |
| 30 | 0.245 [0.238, 0.254] | 0.489 [0.472, 0.511] |

## (2) Bot detection on typed sentences by number of keys (AUC; LightGBM has seen the bot type, split by person)

| Number of keys n | T2 uniform typing | T4 population sampling |
|---|---|---|
| 6 | 0.915 | 0.719 |
| 10 | 0.969 | 0.764 |
| 20 | 0.996 | 0.848 |
| 30 | 0.995 | 0.891 |
