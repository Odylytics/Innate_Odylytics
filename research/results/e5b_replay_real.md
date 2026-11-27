# E5b — calibrating the replay check on real humans (StrokePIN)

1817 (person, PIN) pairs, each with ~5 entries of the same PIN. Current threshold in the backend: **0.07** (chosen on synthetic data in E5). Distance = the backend's `replay.distance`.

## Are new real humans mistaken for replays? (nearest distance to their own history)

| Old sessions compared | Trials | Median distance | FPR at current threshold | FPR at 0.5x threshold |
|---|---|---|---|---|
| 2 | 8969 | 0.185 | 0.0008 | 0.0001 |
| 3 | 8969 | 0.174 | 0.0014 | 0.0001 |
| 4 | 8505 | 0.167 | 0.0020 | 0.0002 |

Real-human distance percentiles: 0.1% = 0.064; 0.5% = 0.082; 1% = 0.088; 5% = 0.107. Median distance of replayed sessions by noise: ±2.5% -> 0.019, ±5.0% -> 0.025, ±10.0% -> 0.050, ±15.0% -> 0.075, ±20.0% -> 0.100, ±30.0% -> 0.150.

**Linear extrapolation** of FPR by number of old sessions (data only goes up to 4): ~0.061 percentage points per additional old session, so with 50 sessions about **3.0%** (not measured: this is a guess, the history in the data is only ~4 entries, a very long extrapolation, so for reference only).

Real-human distance: 1st percentile = **0.088**, 5th percentile = 0.107, median = 0.176.

## How many replayed sessions are caught (adaptive attacker: timing noise ±n, coordinates ±max(0.02, 0.4n) key widths)

| Noise ±n | 2.5% | 5.0% | 10.0% | 15.0% | 20.0% | 30.0% |
|---|---|---|---|---|---|---|
| Current threshold (0.07) | 1.00 | 1.00 | 1.00 | 0.28 | 0.00 | 0.00 |
| FPR 1% threshold (0.088) | 1.00 | 1.00 | 1.00 | 0.92 | 0.16 | 0.00 |
| FPR 5% threshold (0.107) | 1.00 | 1.00 | 1.00 | 1.00 | 0.73 | 0.01 |

## Trade-off by threshold (FPR measured at 2/3/4 old sessions; linear extrapolation to 50; catch rate by noise)

| Threshold | FPR @2 | FPR @4 | FPR @50 (extrapolated) | catch ±2.5% | catch ±5.0% | catch ±10.0% | catch ±15.0% | catch ±20.0% | catch ±30.0% |
|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 0.0001 | 0.0002 | 0.3% | 1.00 | 1.00 | 0.51 | 0.00 | 0.00 | 0.00 |
| 0.06 | 0.0003 | 0.0006 | 0.6% | 1.00 | 1.00 | 0.95 | 0.05 | 0.00 | 0.00 |
| 0.07 | 0.0008 | 0.0020 | 3.0% | 1.00 | 1.00 | 1.00 | 0.28 | 0.00 | 0.00 |
| 0.085 | 0.0050 | 0.0111 | 15.0% | 1.00 | 1.00 | 1.00 | 0.85 | 0.10 | 0.00 |
| 0.094 | 0.0126 | 0.0226 | 25.2% | 1.00 | 1.00 | 1.00 | 0.98 | 0.31 | 0.00 |
