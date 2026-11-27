# E10b — the backend's own `owner.py` on StrokePIN (leave-one-person-out prior)

k=3 sitting enrollment sessions, PIN-knowing impostor, all identity features as in the real backend. 95% CI by bootstrap over people (100 resamples). The last row of each table is the paired difference (on minus off; negative = better).

## same posture (sitting)

| Shrinkage | EER | FAR @ FRR 5% |
|---|---|---|
| off (old behavior) | 0.153 | 0.663 |
| on (timing shrinkage) | 0.146 | 0.495 |
| **paired difference** | -0.007 [-0.011, -0.004] | -0.167 [-0.190, -0.114] |

## changed posture (walking)

| Shrinkage | EER | FAR @ FRR 5% |
|---|---|---|
| off (old behavior) | 0.352 | 0.943 |
| on (timing shrinkage) | 0.355 | 0.943 |
| **paired difference** | +0.003 [-0.000, +0.007] | -0.000 [-0.001, +0.001] |
