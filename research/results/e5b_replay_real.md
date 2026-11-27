# E5b — calibrating the replay check on real humans (StrokePIN)

1842 (person, PIN) pairs, each with 4–10 entries of the same PIN (both sitting and walking). Current threshold in the backend: **0.085** (chosen on synthetic data in E5). Distance = the backend's `replay.distance`.

## Are new real humans mistaken for replays? (nearest distance to their own history)

| Old sessions compared | Trials | Median distance | FPR at current threshold | FPR at 0.5x threshold |
|---|---|---|---|---|
| 3 | 17892 | 0.206 | 0.0028 | 0.0001 |
| 5 | 17777 | 0.189 | 0.0040 | 0.0001 |
| 8 | 17071 | 0.176 | 0.0064 | 0.0001 |

Real-human distance percentiles: 0.1% = 0.071; 0.5% = 0.087; 1% = 0.094; 5% = 0.117. Median distance of replayed sessions by noise: ±2.5% -> 0.019, ±5.0% -> 0.025, ±10.0% -> 0.050, ±15.0% -> 0.075, ±20.0% -> 0.101, ±30.0% -> 0.150.

**Linear extrapolation** of FPR by number of old sessions (data only goes up to 8): ~0.073 percentage points per additional old session, so with 50 sessions about **3.7%** (not measured: this is a guess, the history in the data is only ~9 entries).

Real-human distance: 1st percentile = **0.094**, 5th percentile = 0.117, median = 0.189.

## How many replayed sessions are caught (adaptive attacker: timing noise ±n, coordinates ±max(0.02, 0.4n) key widths)

| Noise ±n | 2.5% | 5.0% | 10.0% | 15.0% | 20.0% | 30.0% |
|---|---|---|---|---|---|---|
| Current threshold (0.085) | 1.00 | 1.00 | 1.00 | 0.86 | 0.09 | 0.00 |
| FPR 1% threshold (0.094) | 1.00 | 1.00 | 1.00 | 0.98 | 0.30 | 0.00 |
| FPR 5% threshold (0.117) | 1.00 | 1.00 | 1.00 | 1.00 | 0.92 | 0.03 |

## Trade-off by threshold (FPR measured at 3/5/8 old sessions; linear extrapolation to 50; catch rate by noise)

| Threshold | FPR @3 | FPR @8 | FPR @50 (extrapolated) | catch ±2.5% | catch ±5.0% | catch ±10.0% | catch ±15.0% | catch ±20.0% | catch ±30.0% |
|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 0.0001 | 0.0001 | 0.1% | 1.00 | 1.00 | 0.50 | 0.00 | 0.00 | 0.00 |
| 0.06 | 0.0003 | 0.0005 | 0.3% | 1.00 | 1.00 | 0.95 | 0.05 | 0.00 | 0.00 |
| 0.07 | 0.0007 | 0.0013 | 0.7% | 1.00 | 1.00 | 1.00 | 0.29 | 0.00 | 0.00 |
| 0.085 | 0.0028 | 0.0064 | 3.7% | 1.00 | 1.00 | 1.00 | 0.86 | 0.09 | 0.00 |
| 0.094 | 0.0061 | 0.0138 | 7.8% | 1.00 | 1.00 | 1.00 | 0.98 | 0.29 | 0.00 |
