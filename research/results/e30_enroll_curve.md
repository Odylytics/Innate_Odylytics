# E30 — number of enrollment sessions and error distribution by victim (StrokePIN, backend distance)

k=1 has no standard deviation; k=5 leaves no test session (at most 5 sessions per person-PIN). 95% CI by bootstrap over people. FAR@FRR5% uses a common threshold; the Gini and 'victims with FAR>90%' columns are per victim (the account owner).

| k | EER | FAR@FRR5% | Gini of FAR by victim | victims with FAR > 90% | median victim FAR |
|---|---|---|---|---|---|
| 2 | 0.167 [0.156, 0.178] | 0.857 [0.661, 0.923] | 0.02 | 7/97 | 0.86 |
| 3 | 0.146 [0.138, 0.155] | 0.503 [0.421, 0.627] | 0.10 | 0/97 | 0.52 |
| 4 | 0.138 [0.128, 0.150] | 0.429 [0.360, 0.534] | 0.13 | 0/97 | 0.44 |
