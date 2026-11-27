# E14 — recognizing the owner when typing a new digit string (simulated account numbers; StrokePIN, real people)

Enrollment 3 PINs x 3 sessions. Impostor = another person typing the **same digit string**. 20 content-independent features, **no** touch size. Split by person (58 training / 39 test), 3 splits; 95% bootstrap CI by person, averaged across splits. Lower is better.

| Test | Detector | EER | FAR @ FRR 5% | Owner sessions / impostor / people (last split) |
|---|---|---|---|---|
| same digit string as enrolled | learned LightGBM | 0.245 [0.204, 0.283] | 0.500 [0.392, 0.602] | 225 / 675 / 39 |
| same digit string as enrolled | mean|z| distance | 0.264 [0.231, 0.301] | 0.737 [0.565, 0.909] | 225 / 675 / 39 |
| **new digit string** (6 digits) | learned LightGBM | 0.328 [0.303, 0.357] | 0.697 [0.640, 0.748] | 1170 / 3510 / 39 |
| **new digit string** (6 digits) | mean|z| distance | 0.360 [0.336, 0.385] | 0.917 [0.863, 0.944] | 1170 / 3510 / 39 |
| **new digit string, 12 digits** (2 sessions pooled) | learned LightGBM | 0.284 [0.259, 0.316] | 0.607 [0.531, 0.680] | 1170 / 3510 / 39 |
| **new digit string, 12 digits** (2 sessions pooled) | mean|z| distance | 0.335 [0.302, 0.369] | 0.909 [0.863, 0.942] | 1170 / 3510 / 39 |

Comparison with E12b (same PIN, per-digit-position features, no touch size): distance EER 0.160 / FAR 0.549; LightGBM EER 0.140 / FAR 0.316. Different protocol (E12b enrolls 3 sessions of ONE PIN), so only the direction is comparable, not individual numbers.
