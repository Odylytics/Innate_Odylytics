# E7 — template poisoning attack (synthetic data)

100 (owner, impostor) pairs; the attacker injects sessions right at the update threshold (owner >= 0.8). 'Accepted' = owner >= 0.5. Synthetic personas, this only checks the method.

## Share of the impostor's REAL sessions accepted after n injections (lower is better)

| Defense | n=0 | n=10 | n=25 | n=50 | n=100 | n=200 |
|---|---|---|---|---|---|---|
| none | 0.56 | 0.96 | 1.00 | 1.00 | 1.00 | 1.00 |
| cap1.0sd | 0.56 | 0.85 | 0.85 | 0.85 | 0.85 | 0.85 |
| cap0.5sd | 0.56 | 0.75 | 0.75 | 0.75 | 0.75 | 0.75 |
| cap0.25sd | 0.56 | 0.67 | 0.67 | 0.67 | 0.67 | 0.67 |
| freeze | 0.56 | 0.77 | 0.77 | 0.77 | 0.77 | 0.77 |

## Share of the owner's new sessions accepted after n injections (higher is better)

| Defense | n=0 | n=10 | n=25 | n=50 | n=100 | n=200 |
|---|---|---|---|---|---|---|
| none | 1.00 | 1.00 | 0.68 | 0.59 | 0.58 | 0.58 |
| cap1.0sd | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| cap0.5sd | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| cap0.25sd | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| freeze | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |

## Mean drift of the template (in sd units) after n injections

| Defense | n=0 | n=10 | n=25 | n=50 | n=100 | n=200 |
|---|---|---|---|---|---|---|
| none | 0.00 | 1.05 | 1.66 | 1.82 | 1.83 | 1.83 |
| cap1.0sd | 0.00 | 0.64 | 0.72 | 0.73 | 0.73 | 0.73 |
| cap0.5sd | 0.00 | 0.38 | 0.40 | 0.41 | 0.41 | 0.41 |
| cap0.25sd | 0.00 | 0.21 | 0.21 | 0.22 | 0.22 | 0.22 |
| freeze | 0.00 | 0.42 | 0.42 | 0.42 | 0.42 | 0.42 |

## The cost: a real owner who drifts slowly (hold/flight times grow gradually over 100 sessions) — share of the owner's new sessions accepted

| Defense | +15% | +30% | +50% |
|---|---|---|---|
| none | 1.00 | 1.00 | 1.00 |
| cap1.0sd | 1.00 | 1.00 | 1.00 |
| cap0.5sd | 1.00 | 1.00 | 0.99 |
| cap0.25sd | 1.00 | 1.00 | 0.98 |
| freeze | 1.00 | 1.00 | 1.00 |

Same scenario, but counting acceptance as owner >= 0.8 (the update threshold; more sensitive to the template failing to keep up with the owner):

| Defense | +15% | +30% | +50% |
|---|---|---|---|
| none | 1.00 | 1.00 | 1.00 |
| cap1.0sd | 1.00 | 0.98 | 0.67 |
| cap0.5sd | 1.00 | 0.95 | 0.41 |
| cap0.25sd | 1.00 | 0.90 | 0.28 |
| freeze | 1.00 | 0.99 | 0.68 |
