# E4b — human/bot with REAL HUMANS (StrokePIN) and generator-made bots

3 different splits of people (train 40 / val 12 / test 30 / attacker pool 15 people, no person in two sets). The threshold is chosen so that FRR = 5% on humans in the validation set. Each cell: **share of bots caught** (AUC). Only the PIN part is compared. The bots are still synthetic.

## Training saw all 4 tactics

| Model | Actual FRR (test humans) | T1 | T2 | T3 | T4 |
|---|---|---|---|---|---|
| LightGBM | 0.059 | 1.00 (1.00) | 1.00 (1.00) | 0.26 (0.74) | 0.73 (0.93) |
| IsolationForest (humans only) | 0.046 | 1.00 (0.97) | 0.86 (0.97) | 0.07 (0.54) | 0.03 (0.59) |
| Combined | 0.053 | 1.00 (0.97) | 1.00 (0.97) | 0.20 (0.57) | 0.62 (0.78) |
| LightGBM (no touch size) | 0.059 | 1.00 (1.00) | 1.00 (1.00) | 0.23 (0.72) | 0.69 (0.91) |
| IsolationForest (humans only) (no touch size) | 0.056 | 0.33 (0.94) | 0.31 (0.93) | 0.07 (0.52) | 0.03 (0.59) |
| Combined (no touch size) | 0.061 | 1.00 (0.97) | 1.00 (0.97) | 0.18 (0.56) | 0.61 (0.77) |
| Baseline rules (human.py) | 0.058 | 1.00 (1.00) | 1.00 (1.00) | 0.05 (0.49) | 0.01 (0.46) |

## Drop exactly one tactic from training, test on that tactic (unseen bots)

| Model | Actual FRR | Drop T1 | Drop T2 | Drop T3 | Drop T4 |
|---|---|---|---|---|---|
| LightGBM | 0.059 | 1.00 (1.00) | 0.56 (0.86) | 0.09 (0.57) | 0.20 (0.66) |
| IsolationForest (humans only) | 0.046 | 1.00 (0.97) | 0.86 (0.97) | 0.07 (0.54) | 0.03 (0.59) |
| Combined | 0.057 | 1.00 (0.97) | 0.76 (0.85) | 0.09 (0.52) | 0.15 (0.54) |
| LightGBM (no touch size) | 0.058 | 1.00 (1.00) | 0.47 (0.80) | 0.08 (0.57) | 0.20 (0.70) |
| IsolationForest (humans only) (no touch size) | 0.056 | 0.33 (0.94) | 0.31 (0.93) | 0.07 (0.52) | 0.03 (0.59) |
| Combined (no touch size) | 0.064 | 1.00 (0.97) | 0.39 (0.66) | 0.09 (0.52) | 0.16 (0.54) |
