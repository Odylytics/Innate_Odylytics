# E5 — replay detection (synthetic data)

300 synthetic accounts, 10 old sessions per account. The threshold is chosen so that **only ~1% of new real-human sessions are treated as replays**; the table reports the catch rate of replayed sessions by the attacker's noise level (time ±n, coordinates ±max(2, 40n) px). Synthetic personas, this only checks the method.

## 4-digit PIN

| Distance | Threshold | FPR | Median distance of real humans | noise ±2.5% | noise ±5.0% | noise ±10.0% | noise ±15.0% | noise ±20.0% | noise ±30.0% |
|---|---|---|---|---|---|---|---|---|---|
| rel (current) | 0.065 | 0.010 | 0.141 | 1.00 | 1.00 | 0.93 | 0.28 | 0.05 | 0.00 |
| rel+ (adds center offset) | 0.088 | 0.010 | 0.143 | 1.00 | 1.00 | 1.00 | 0.59 | 0.07 | 0.00 |
| z (by owner sd) | 0.388 | 0.010 | 0.625 | 1.00 | 1.00 | 1.00 | 0.66 | 0.14 | 0.00 |

## 6-digit PIN

| Distance | Threshold | FPR | Median distance of real humans | noise ±2.5% | noise ±5.0% | noise ±10.0% | noise ±15.0% | noise ±20.0% | noise ±30.0% |
|---|---|---|---|---|---|---|---|---|---|
| rel (current) | 0.078 | 0.010 | 0.153 | 1.00 | 1.00 | 1.00 | 0.56 | 0.12 | 0.01 |
| rel+ (adds center offset) | 0.106 | 0.010 | 0.152 | 1.00 | 1.00 | 1.00 | 0.99 | 0.36 | 0.00 |
| z (by owner sd) | 0.499 | 0.010 | 0.720 | 1.00 | 1.00 | 1.00 | 0.97 | 0.35 | 0.00 |

## FPR of the version used in the backend (rel+, threshold 0.085) by number of old sessions compared

| PIN | 10 old sessions | 50 old sessions | 200 old sessions |
|---|---|---|---|
| 4 digits | 0.000 | 0.033 | 0.075 |
| 6 digits | 0.000 | 0.000 | 0.000 |
