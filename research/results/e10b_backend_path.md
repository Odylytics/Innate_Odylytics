# E10b — the backend's own `owner.py` on StrokePIN (leave-one-person-out prior)

k=3 enrollment sessions, PIN-knowing impostor, all identity features as in the real backend. 95% CI by bootstrap over people (100 resamples). The last row of each table is the paired difference (on minus off; negative = better).

| Shrinkage | EER | FAR @ FRR 5% |
|---|---|---|
| off (old behavior) | 0.157 | 0.704 |
| on (timing shrinkage) | 0.148 | 0.541 |
| **paired difference** | -0.008 [-0.011, -0.005] | -0.163 [-0.196, -0.121] |
