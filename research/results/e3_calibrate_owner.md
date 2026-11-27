# E3 — owner score calibration (StrokePIN, 6-digit PIN, enrollment on 3 sessions)

Platt fit on half A (18634 sessions): score = sigmoid(-1.216·d + 1.390). Tested on half B (18788 sessions, entirely different people).

| Mapping | Owner with score ≥ 0.5 | PIN-knowing impostor with score ≥ 0.5 |
|---|---|---|
| current (d=2→0.5) | 0.96 | 0.84 |
| Fitted Platt (class-balanced) | 0.90 | 0.27 |

d threshold for FRR 5% (half B): d=1.37; FAR there = 0.50. Median d: owner 0.73, impostor 1.37.

Conclusion: see the numbers above. Platt only shifts the threshold and adds no separation; FAR@FRR5% is still decided by the features (E9/E12b).

## Is it wired into the backend? Tried (26/11): there is a switch, NOT on by default

`owner.py` has `NHIP_OWNER_MAP=platt` (default `legacy`). E24 rerun with Platt (`e24_platt_map.md`, rerun 27/11):
- The columns **with the learned model are unchanged**: for 6-digit PINs the owner score comes from `owner_model` (LightGBM), and Platt only changes the fallback distance path (4-digit PIN, model off, missing features).
- Fallback path, known recipient: PIN-knowing impostor passes 89% -> 77%, owner 96% -> 94%. A slight benefit.
- Fallback path, **new recipient**: owner allow 91% -> 3%, PIN-knowing impostor 61% -> 0%. The maximum owner score under Platt is only ~0.63, so the owner's fused risk is always >= 0.13, and adding 0.15 for a new recipient exceeds A=0.25: everyone gets `step_up`.
- `UPDATE_MIN_OWNER = 0.8` is also never reached under Platt, so the template stops updating (the `test_full_flow` test fails when it is on).

To turn Platt on, A/B and `UPDATE_MIN_OWNER` must be moved at the same time and E24/E25 re-measured. That is only worth doing if the fallback path is really used, and it should be done on the team's data instead of StrokePIN.
