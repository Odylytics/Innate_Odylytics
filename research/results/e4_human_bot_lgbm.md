# E4 — LightGBM for the human/bot task (synthetic data)

3 independent data generations, averaged. The threshold is chosen on humans in the validation set so that FRR = 5%. Each cell is the **share of bots caught** (AUC in parentheses). Synthetic data: this only checks the pipeline.

## Training saw all 4 tactics (optimistic)

| Model | Actual FRR | Tactic 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| LightGBM | 0.047 | 1.00 (1.00) | 1.00 (1.00) | 0.85 (0.97) | 0.97 (0.99) |
| IsolationForest (humans only) | 0.051 | 1.00 (1.00) | 1.00 (1.00) | 0.12 (0.65) | 0.47 (0.87) |
| Combined (LightGBM or IsolationForest) | 0.049 | 1.00 (nan) | 1.00 (nan) | 0.80 (nan) | 0.97 (nan) |
| LightGBM (no touch size) | 0.052 | 1.00 (1.00) | 1.00 (1.00) | 0.85 (0.96) | 0.98 (1.00) |
| IsolationForest (humans only) (no touch size) | 0.050 | 1.00 (1.00) | 1.00 (1.00) | 0.13 (0.67) | 0.38 (0.85) |
| Combined (LightGBM or IsolationForest) (no touch size) | 0.047 | 1.00 (nan) | 1.00 (nan) | 0.82 (nan) | 0.97 (nan) |
| Baseline rules (human.py) | 0.049 | 1.00 (1.00) | 1.00 (1.00) | 0.04 (0.49) | 0.01 (0.41) |

## Drop one tactic from training, test on exactly that tactic (more realistic for unseen bots)

| Model | Actual FRR | Drop tactic 1 | Drop 2 | Drop 3 | Drop 4 |
|---|---|---|---|---|---|
| LightGBM | 0.047 | 0.00 (0.50) | 1.00 (1.00) | 0.07 (0.56) | 0.23 (0.68) |
| IsolationForest (humans only) | 0.051 | 1.00 (1.00) | 1.00 (1.00) | 0.12 (0.65) | 0.47 (0.87) |
| Combined (LightGBM or IsolationForest) | 0.049 | 1.00 (nan) | 1.00 (nan) | 0.11 (nan) | 0.41 (nan) |
| LightGBM (no touch size) | 0.050 | 0.00 (0.41) | 1.00 (1.00) | 0.08 (0.57) | 0.24 (0.69) |
| IsolationForest (humans only) (no touch size) | 0.050 | 1.00 (1.00) | 1.00 (1.00) | 0.13 (0.67) | 0.38 (0.85) |
| Combined (LightGBM or IsolationForest) (no touch size) | 0.049 | 1.00 (nan) | 1.00 (nan) | 0.13 (nan) | 0.37 (nan) |

## Which features the model relies on (gain, full model)

| Feature | Gain share |
|---|---|
| swipe_v_peak_ratio | 0.18 |
| swipe_lateral_dev | 0.16 |
| dy_std | 0.14 |
| tap_w_std | 0.13 |
| dx_std | 0.10 |
| off_mean | 0.09 |
| swipe_straight | 0.03 |
| tap_h_std | 0.03 |

The full model is saved at `research/models/human_lgbm_synthetic.txt` (trained on SYNTHETIC data, **not used for the submission**).
