# E11 — human/bot task on a free-text field (real Aalto humans + generated bots)

3 different splits of people. Humans: 33522 real typed sentences from 2260 people, split by person (attacker pool 200 / train 1200 / val 300 / test the rest). FRR 5% threshold on humans in the validation set. Each cell: **share of bots caught** (AUC). Only the `note` field. The bots are still synthetic.

## Training saw all 4 tactics

| Model | Actual FRR | T1 set text directly | T2 even typing | T3 replay | T4 population sampling |
|---|---|---|---|---|---|
| LightGBM, backend (fld_*) | 0.048 | 1.00 (1.00) | 0.99 (1.00) | 0.06 (0.60) | 0.31 (0.85) |
| IsolationForest, backend (fld_*) | 0.064 | 0.00 (0.85) | 0.00 (0.71) | 0.05 (0.49) | 0.01 (0.42) |
| LightGBM, extended | 0.047 | 1.00 (1.00) | 0.99 (1.00) | 0.08 (0.64) | 0.58 (0.93) |
| IsolationForest, extended | 0.061 | 0.67 (0.95) | 0.00 (0.77) | 0.06 (0.48) | 0.01 (0.34) |
| Current backend rules (flag when score < 0.5) | 0.000 | 0.00 | 0.00 | 0.00 | 0.00 |

## Drop exactly one tactic from training (unseen bots)

| Model | Actual FRR | Drop T1 | Drop T2 | Drop T3 | Drop T4 |
|---|---|---|---|---|---|
| LightGBM, backend (fld_*) | 0.049 | 1.00 (0.99) | 0.00 (0.20) | 0.05 (0.52) | 0.04 (0.56) |
| IsolationForest, backend (fld_*) | 0.064 | 0.00 (0.85) | 0.00 (0.71) | 0.05 (0.49) | 0.01 (0.42) |
| LightGBM, extended | 0.047 | 1.00 (0.99) | 0.01 (0.31) | 0.05 (0.52) | 0.05 (0.58) |
| IsolationForest, extended | 0.061 | 0.67 (0.95) | 0.00 (0.77) | 0.06 (0.48) | 0.01 (0.34) |
