> **Run with `NHIP_OWNER_MAP=platt` (E3), NOT the default configuration.** Default version: `e24_end_to_end.md`. The "no learned model" column is the fallback distance path; the columns with the learned model do not change because the learned owner model replaces the score when the PIN has 6 keys.

# E24 / E25 / E27 — whole-system decisions on StrokePIN (real people) + bots

10 people never seen by either learned model; enrollment 3 sessions per (person, PIN); replay history = the previous sessions. Current thresholds A=0.25, B=0.55. The PIN-knowing impostor uses a DIFFERENT DEVICE (confounded with device noise). Bots are the team's generator/scripts, not real bots.

## E24 — known recipient, normal amount

| Group | n | allow | step_up | hold | (no learned model) allow |
|---|---|---|---|---|---|
| owner | 356 | 81% | 18% | 1% | 94% |
| PIN-knowing impostor (other person, other device) | 712 | 28% | 71% | 1% | 77% |
| T1 uniform bot | 356 | 0% | 0% | 100% | 0% |
| T2 timing-noise bot | 356 | 0% | 0% | 100% | 0% |
| T3 replay ±5% bot | 356 | 0% | 0% | 100% | 0% |
| T4 population-sampling bot | 356 | 5% | 72% | 23% | 68% |
| replay ±10% | 356 | 0% | 0% | 100% | 0% |
| replay ±15% | 356 | 60% | 13% | 28% | 70% |
| replay ±20% | 356 | 72% | 26% | 1% | 97% |
| replay ±30% | 356 | 44% | 53% | 3% | 97% |
| template-aware bot (scale 1.0) | 356 | 79% | 15% | 6% | 96% |
| template-aware bot (scale 0.5) | 356 | 86% | 5% | 9% | 90% |

## E24 — NEW recipient

| Group | n | allow | step_up | hold | (no learned model) allow |
|---|---|---|---|---|---|
| owner | 356 | 18% | 79% | 3% | 3% |
| PIN-knowing impostor (other person, other device) | 712 | 0% | 87% | 13% | 0% |
| T1 uniform bot | 356 | 0% | 0% | 100% | 0% |
| T2 timing-noise bot | 356 | 0% | 0% | 100% | 0% |
| T3 replay ±5% bot | 356 | 0% | 0% | 100% | 0% |
| T4 population-sampling bot | 356 | 0% | 45% | 55% | 0% |
| replay ±10% | 356 | 0% | 0% | 100% | 0% |
| replay ±15% | 356 | 8% | 64% | 28% | 0% |
| replay ±20% | 356 | 7% | 89% | 4% | 0% |
| replay ±30% | 356 | 1% | 91% | 8% | 0% |
| template-aware bot (scale 1.0) | 356 | 21% | 72% | 7% | 8% |
| template-aware bot (scale 0.5) | 356 | 39% | 52% | 9% | 51% |

## E25 — sweep of threshold A (allow < A) and B (hold > B), known recipient, with learned models

Goal: the owner almost always gets `allow` (hold ≤ 1%), and PIN-knowing impostors and bots are blocked (not `allow`) as often as possible.

| A | B | owner: allow / hold | owner, NEW recipient: allow | PIN-knowing impostor: not allow | T4: not allow | template-aware 1.0: not allow | replay ±15%: not allow |
|---|---|---|---|---|---|---|---|
| 0.25 | 0.55 | 81% / 1% | 18% | 72% | 95% | 21% | 40% | ← current
| 0.10 | 0.55 | 18% / 1% | 0% | 100% | 100% | 79% | 92% |
| 0.15 | 0.55 | 43% / 1% | 0% | 98% | 100% | 51% | 72% |
| 0.20 | 0.55 | 64% / 1% | 0% | 90% | 99% | 33% | 52% |
| 0.30 | 0.55 | 90% / 1% | 43% | 54% | 82% | 13% | 34% |
| 0.35 | 0.55 | 95% / 1% | 64% | 34% | 70% | 8% | 30% |
| 0.40 | 0.60 | 97% / 1% | 81% | 13% | 55% | 7% | 28% |
| 0.45 | 0.65 | 99% / 1% | 90% | 6% | 39% | 6% | 28% |
| 0.25 | 0.40 | 81% / 3% | 18% | 72% | 95% | 21% | 40% |
| 0.25 | 0.70 | 81% / 1% | 18% | 72% | 95% | 21% | 40% |

## E27b — sweep of the replay threshold (the backend currently uses 0.07), with learned models, known recipient

A session judged to be a replay gets `hold`. Trade-off: a higher threshold catches more noisy replay bots but wrongly blocks the owner.

| Threshold | owner: hold | replay ±10% | ±15% | ±20% | ±30% | template-aware bot (1.0): hold |
|---|---|---|---|---|---|---|
| 0.050 | 1% | 100% | 28% | 1% | 3% | 6% |
| 0.070 | 1% | 100% | 28% | 1% | 3% | 6% |
| 0.085 | 3% | 100% | 85% | 10% | 3% | 10% |
| 0.100 | 6% | 100% | 99% | 50% | 3% | 16% |
| 0.120 | 15% | 100% | 100% | 96% | 7% | 33% |
| 0.150 | 37% | 100% | 100% | 100% | 50% | 55% |

