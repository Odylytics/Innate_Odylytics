# E21 — digraph-normalized typing rhythm, recognizing the owner when the test sentence differs from the enrollment sentence (Aalto, real people)

E13 protocol: enroll 3 sentences, test other sentences, impostor = another person's sentence; key-pair prior and variance from a separate group of people. EER and FAR@FRR5%, bootstrap confidence intervals by person.

| Features | n keys | EER | FAR @ FRR 5% |
|---|---|---|---|
| E13 raw (6 log-interval features) | 10 | 0.335 [0.326, 0.341] | 0.737 [0.708, 0.758] |
| E13 raw (6 log-interval features) | 20 | 0.281 [0.273, 0.290] | 0.594 [0.572, 0.616] |
| E13 raw (6 log-interval features) | 30 | 0.249 [0.243, 0.259] | 0.498 [0.473, 0.524] |
| digraph-normalized (6 z features) | 10 | 0.332 [0.325, 0.340] | 0.705 [0.692, 0.726] |
| digraph-normalized (6 z features) | 20 | 0.280 [0.272, 0.288] | 0.601 [0.577, 0.622] |
| digraph-normalized (6 z features) | 30 | 0.245 [0.236, 0.253] | 0.479 [0.456, 0.501] |
| overall speed only (mean z, 1 feature) | 10 | 0.344 [0.337, 0.352] | 0.683 [0.664, 0.704] |
| overall speed only (mean z, 1 feature) | 20 | 0.301 [0.291, 0.310] | 0.574 [0.553, 0.592] |
| overall speed only (mean z, 1 feature) | 30 | 0.266 [0.259, 0.274] | 0.487 [0.472, 0.504] |
| raw + normalized (12 features) | 10 | 0.326 [0.318, 0.332] | 0.730 [0.699, 0.744] |
| raw + normalized (12 features) | 20 | 0.274 [0.266, 0.283] | 0.572 [0.552, 0.596] |
| raw + normalized (12 features) | 30 | 0.238 [0.228, 0.245] | 0.467 [0.446, 0.489] |
