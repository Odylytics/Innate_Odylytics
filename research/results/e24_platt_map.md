> **Run with `NHIP_OWNER_MAP=platt` (E3), NOT the default configuration.** Default version: `e24_end_to_end.md`. The "no learned model" column is the fallback distance path; the columns with the learned model do not change because the learned owner model replaces the score when the PIN has all 6 keys.

# E24 / E25 / E27 — whole-system decisions on StrokePIN (real people) + bots

10 people never seen by either learned model; enrollment 3 sitting sessions per (person, PIN); replay history = the previous sessions. Current thresholds A=0.25, B=0.55. The PIN-knowing impostor uses a DIFFERENT DEVICE (confounded with device noise). Bots are the team's generator/scripts, not real bots.

## E24 — known recipient, normal amount

| Group | n | allow | step_up | hold | (no learned model) allow |
|---|---|---|---|---|---|
| owner, same posture (sitting) | 356 | 80% | 19% | 1% | 94% |
| owner, changed posture (walking) | 709 | 63% | 37% | 0% | 85% |
| PIN-knowing impostor (other person, other device) | 712 | 28% | 70% | 2% | 79% |
| T1 uniform bot | 356 | 0% | 0% | 100% | 0% |
| T2 timing-noise bot | 356 | 0% | 0% | 100% | 0% |
| T3 replay ±5% bot | 356 | 0% | 0% | 100% | 0% |
| T4 population-sampling bot | 356 | 7% | 67% | 26% | 65% |
| replay ±10% | 356 | 0% | 0% | 100% | 0% |
| replay ±15% | 356 | 58% | 13% | 30% | 71% |
| replay ±20% | 356 | 72% | 26% | 1% | 99% |
| replay ±30% | 356 | 48% | 48% | 4% | 99% |
| template-aware bot (scale 1.0) | 356 | 75% | 17% | 8% | 92% |
| template-aware bot (scale 0.5) | 356 | 82% | 6% | 12% | 90% |

## E24 — NEW recipient

| Group | n | allow | step_up | hold | (no learned model) allow |
|---|---|---|---|---|---|
| owner, same posture (sitting) | 356 | 17% | 79% | 4% | 2% |
| owner, changed posture (walking) | 709 | 2% | 95% | 3% | 0% |
| PIN-knowing impostor (other person, other device) | 712 | 1% | 86% | 14% | 0% |
| T1 uniform bot | 356 | 0% | 0% | 100% | 0% |
| T2 timing-noise bot | 356 | 0% | 0% | 100% | 0% |
| T3 replay ±5% bot | 356 | 0% | 0% | 100% | 0% |
| T4 population-sampling bot | 356 | 0% | 46% | 54% | 0% |
| replay ±10% | 356 | 0% | 0% | 100% | 0% |
| replay ±15% | 356 | 8% | 61% | 31% | 1% |
| replay ±20% | 356 | 6% | 90% | 4% | 0% |
| replay ±30% | 356 | 1% | 88% | 11% | 0% |
| template-aware bot (scale 1.0) | 356 | 20% | 71% | 9% | 7% |
| template-aware bot (scale 0.5) | 356 | 43% | 46% | 12% | 53% |

## E25 — sweep of threshold A (allow < A) and B (hold > B), known recipient, with learned models

Goal: the owner in the same posture almost always gets `allow` (hold ≤ 1%), and PIN-knowing impostors and bots are blocked (not `allow`) as often as possible.

| A | B | owner sitting: allow / hold | owner walking: allow | owner sitting, NEW recipient: allow | PIN-knowing impostor: not allow | T4: not allow | template-aware 1.0: not allow | replay ±15%: not allow |
|---|---|---|---|---|---|---|---|---|
| 0.25 | 0.55 | 80% / 1% | 63% | 17% | 72% | 93% | 25% | 42% | ← current
| 0.10 | 0.55 | 17% / 1% | 2% | 0% | 99% | 100% | 80% | 92% |
| 0.15 | 0.55 | 42% / 1% | 11% | 0% | 98% | 100% | 54% | 73% |
| 0.20 | 0.55 | 65% / 1% | 34% | 0% | 90% | 98% | 36% | 58% |
| 0.30 | 0.55 | 91% / 1% | 83% | 42% | 50% | 80% | 17% | 38% |
| 0.35 | 0.55 | 95% / 1% | 92% | 65% | 31% | 67% | 12% | 33% |
| 0.40 | 0.60 | 96% / 1% | 97% | 80% | 14% | 54% | 9% | 31% |
| 0.45 | 0.65 | 98% / 1% | 99% | 91% | 6% | 42% | 8% | 30% |
| 0.25 | 0.40 | 80% / 4% | 63% | 17% | 72% | 93% | 25% | 42% |
| 0.25 | 0.70 | 80% / 1% | 63% | 17% | 72% | 93% | 25% | 42% |

## E27b — sweep of the replay threshold (the backend currently uses 0.07), with learned models, known recipient

A session judged to be a replay gets `hold`. Trade-off: a higher threshold catches more noisy replay bots but wrongly blocks the owner.

| Threshold | owner sitting: hold | owner walking: hold | replay ±10% | ±15% | ±20% | ±30% | template-aware bot (1.0): hold |
|---|---|---|---|---|---|---|---|
| 0.050 | 1% | 0% | 100% | 30% | 1% | 4% | 8% |
| 0.070 | 1% | 0% | 100% | 30% | 1% | 4% | 8% |
| 0.085 | 3% | 0% | 100% | 86% | 11% | 4% | 11% |
| 0.100 | 6% | 0% | 100% | 99% | 47% | 4% | 17% |
| 0.120 | 17% | 1% | 100% | 100% | 95% | 8% | 33% |
| 0.150 | 38% | 6% | 100% | 100% | 100% | 51% | 58% |

