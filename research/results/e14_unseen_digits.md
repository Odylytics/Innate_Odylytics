# E14 — recognizing the owner when typing a new digit string (simulated account numbers; StrokePIN, real people)

Enrollment 3 PINs x 3 sessions while sitting. Impostor = another person typing the **same digit string**, same posture. 20 content-independent features, **no** touch size. Split by person (58 training / 39 test), 3 splits; 95% bootstrap CI by person, averaged across splits. Lower is better.

| Test | Detector | EER | FAR @ FRR 5% | Owner sessions / impostor / people (last split) |
|---|---|---|---|---|
| same digit string as enrolled | learned LightGBM | 0.250 [0.218, 0.288] | 0.537 [0.442, 0.619] | 227 / 681 / 39 |
| same digit string as enrolled | mean|z| distance | 0.261 [0.225, 0.296] | 0.784 [0.597, 0.933] | 227 / 681 / 39 |
| **new digit string** (6 digits) | learned LightGBM | 0.325 [0.302, 0.345] | 0.697 [0.645, 0.746] | 1170 / 3510 / 39 |
| **new digit string** (6 digits) | mean|z| distance | 0.356 [0.331, 0.381] | 0.918 [0.871, 0.943] | 1170 / 3510 / 39 |
| **new digit string, 12 digits** (2 sessions pooled) | learned LightGBM | 0.268 [0.243, 0.296] | 0.588 [0.507, 0.661] | 1170 / 3510 / 39 |
| **new digit string, 12 digits** (2 sessions pooled) | mean|z| distance | 0.332 [0.301, 0.361] | 0.918 [0.850, 0.938] | 1170 / 3510 / 39 |
| new digit string, while **walking** | learned LightGBM | 0.367 [0.337, 0.399] | 0.822 [0.751, 0.879] | 1140 / 3420 / 38 |
| new digit string, while **walking** | mean|z| distance | 0.414 [0.382, 0.447] | 0.933 [0.910, 0.950] | 1140 / 3420 / 38 |

Comparison with E12b (same PIN, per-digit-position features, no touch size): distance EER 0.161 / FAR 0.573; LightGBM EER 0.158 / FAR 0.375. Different protocol (E12b enrolls 3 sessions of ONE PIN), so only the direction is comparable, not individual numbers.
