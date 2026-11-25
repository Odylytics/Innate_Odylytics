# Innate

**A human-verification layer for digital-wallet transactions.** Innate runs silently when a payment is confirmed and uses AI to match *how* the person touches and types against the owner's enrolled habits and against what real humans look like. It answers two questions before the money moves:

1. **Human or machine?** (accessibility-service malware, `adb`, scripts)
2. **If human, the account owner?** (someone who watched the PIN)

> *A PIN can be stolen. Touch habits are very hard to steal.* ("innate" = *bẩm sinh*) · Built for the **MoMo Tech Contest 2026**. Project documents are mostly in Vietnamese; this README is the English entry point.

**Innate is a risk signal, not a lock.** It never replaces the PIN, OTP or face check and never freezes an account by itself; when unsure it recommends `step_up` (a stronger factor). [Honest numbers and limits below.](#measured-results)

## How it works

```
First use      enter the PIN / a transfer 3–5 times  ->  store a small "habit template" (means + spreads, no content)
Each payment   compare with the template + "human or machine?" + "replay?"  ->  allow | step_up | hold  + reasons
Unsure?        Innate Challenge: type a short random letters+digits phrase shown on screen (~10 s) instead of OTP
```

| Check | Compares | Needs enrolment | Catches |
|---|---|---|---|
| Human vs machine | session ↔ pattern of real humans | no | scripts, `adb`, naive malware |
| Owner match | session ↔ the owner's template | yes | someone who knows the PIN |
| Replay | session ↔ the account's own past sessions | no | malware that recorded real input |

All are 1:1 verification. Outputs are fused with context (new recipient, unusual amount) into `allow | step_up | hold` plus Vietnamese reasons. **No LLM is on the decision path.** Where it sits in the security stack and what it does *not* do: [`docs/plan/positioning.md`](docs/plan/positioning.md).

**Innate Challenge** (design: [`docs/plan/innate-challenge.md`](docs/plan/innate-challenge.md)): more keystrokes give more signal. On 2,260 real typists, going from 6 to 30 keystrokes cut the false-accept rate at FRR 5% from 81% to 49%. It helps; it does not turn the owner score into a gate.

## What is inside

| Part | What | Where |
|---|---|---|
| API | FastAPI scoring service (the mobile demo app will send only timings/coordinates/event kinds, no content) | `backend/` |
| Learned models (interim) | LightGBM human-vs-bot and owner-match models, population prior; all optional with rule/distance fallback | `backend/app/models/`, `backend/app/scoring/` |
| Bot simulator | 4 tactics (even taps → timing noise → replay → sampling human distributions), text-field bots, real-phone `adb` attack | `attacker/` |
| Research | every experiment (E1–E13) with code and result tables | `research/`, `docs/research/ai-research.md` |

Endpoints (key scopes SDK / ops / ml): `POST /v1/sessions`, `POST /v1/users/{id}/enroll`, `GET /v1/users/{id}`, `POST /v1/sessions/{id}/score`, `GET /v1/sessions` and `POST …/label` (ops), `GET /v1/export` (ml), Swagger at `/docs`. Data contract: [`backend/README.md`](backend/README.md).

## Measured results

All from **public data of other people** (StrokePIN, Aalto, CMU DSL); **none yet from the team's own data**; **all bots are generator-made**.

| Question | Result |
|---|---|
| Owner match: 97 users, 6-digit PINs, attacker **knows the PIN**, 3 enrolment entries, person-disjoint, contact size excluded | distance baseline: EER 0.161, false-accept **0.573** at FRR 5% → learned model: EER 0.158, false-accept **0.375** (paired CI excludes 0). After a posture change (sit→walk): EER 0.31, false-accept 0.71 |
| Human vs machine: real humans, generator bots | naive bots (even rhythm, exact key centres, timing noise): **100%** caught; population-sampling bot 20–73%; unseen bot families are weak |
| Replay check (threshold calibrated on real humans) | catches 100% of replays with ≤ ±10% added noise, 29% at ±15%, 0% from ±20%; human false-positive ≈ 0.1% |

So the owner signal is **weaker than papers suggest** (EER 16%, not "a few percent"): use it to trigger step-up, never as a gate.

## Limitations

- Habits are *hard*, not *impossible*, to imitate; adaptive system-level agents were reported to beat touch+IMU detectors 71–77% of the time (ActReal 2026).
- Enrolment must cover several postures; a sit-only template barely works while walking. The enrolment lock (409 once a template exists) conflicts with that need; a controlled re-enrolment path is not designed yet.
- Web SDKs cannot see text set without keystrokes and get no coordinates on the system keyboard; a native SDK is needed.
- Models are **interim**: public people + generated bots. Retrain on team data with `research/experiments/train_human_model.py --export …`.
- Out of scope: detecting the malware itself, content-based scam detection, replacing authentication.

## Repository layout

`backend/` service, scoring, models, tests · `attacker/` bot simulator · `research/` experiments, results, git-ignored `data/` · `docs/` (`contest/` rules + checklist, `plan/` positioning / how-it-works / challenge / pitch, `research/` logs, `submission/` proposal, slides, scripts, README skeleton) · `papers/` reference PDFs (not submitted) · `CLAUDE.md` conventions and known gaps.

## Quick start

Python 3.11+, [`uv`](https://docs.astral.sh/uv/).

```bash
cd backend && uv sync --extra ml        # ml = LightGBM + NumPy (optional)
uv run uvicorn app.main:app --reload --port 8000    # Swagger at /docs (local default key: demo-key)
uv run pytest -q                        # 28 tests
cd ../attacker && uv sync && uv run pytest -q       # 8 tests
```

Reproduce an experiment (needs `numpy pandas scikit-learn lightgbm`; data is downloaded separately, see [`docs/research/datasets.md`](docs/research/datasets.md)):

```bash
git clone https://github.com/Litraveler/StrokePIN.git research/data/StrokePIN   # CC BY-NC-SA 4.0
cd research && python experiments/e12_learned_owner.py --no-contact              # owner match, learned model
```

Config (env): `DATABASE_URL`, `NHIP_API_KEYS` / `NHIP_OPS_KEYS` / `NHIP_ML_KEYS`, `NHIP_CORS_ORIGINS`, `NHIP_THRESHOLD_A/B` (0.25 / 0.55), `NHIP_HUMAN_MODEL` / `NHIP_OWNER_MODEL` / `NHIP_POP_PRIOR` (`off` disables), `NHIP_REPLAY_THRESHOLD` (0.07). `NHIP_` is a legacy prefix kept so the deployed service does not break.

## Data, licences, privacy

- **StrokePIN** (Yao & Wang, IEEE TDSC 2026) is **CC BY-NC-SA 4.0**; the models and `population_prior.json` derived from it are under the same terms. Aalto typing37k and CMU DSL are used for research experiments only (licences to be confirmed). Open-source libraries keep their own licences. Claude Code (Anthropic) assisted with code, experiments and docs; every reported number comes from code in `research/`. **The repository code itself has no licence yet; the team must decide.**
- Only timings, coordinates, event kinds and character counts are stored: **never PIN content, amounts, recipients or message text.** Touch and typing dynamics are sensitive biometric-like data (Vietnam's 2025 personal-data law, Decree 356/2025): collect only with explicit consent.

## Status

Contest deadline **2026-12-03 23:59** (product online until 2026-12-11). Next: collect real sessions from consenting participants, real bots via `adb`/`dispatchGesture`, retrain and recalibrate, a controlled re-enrolment path, deployment (the Vercel preview currently fails) and a mobile demo app. The landing page lives in its own repository (`Innate_website`). Submission material: [`docs/submission/`](docs/submission/).
