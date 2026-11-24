# Innate

**A human-verification layer for digital-wallet transactions.** Innate runs silently at the moment a payment is confirmed and uses AI to match *how* the person touches and types against (a) the account owner's enrolled habits and (b) what real humans look like — answering two questions before the money moves:

1. **Is a human or a machine operating this phone?** (accessibility-service malware, `adb`, scripts)
2. **If it is a human, is it the account owner?** (someone who watched the PIN over a shoulder)

> *A PIN can be stolen. Innate-style touch habits are very hard to steal.* — "innate" (Vietnamese: *bẩm sinh*).
> Built for the **MoMo Tech Contest 2026** (themes: cybersecurity + anti-fraud). Most project documents are in Vietnamese; this README is the English entry point.

**Innate is a risk signal, not a lock.** It never replaces the PIN, OTP, or face check, and it never freezes an account by itself. When it is unsure it recommends `step_up` (ask for a stronger factor) instead of blocking. Measured numbers and limits are listed honestly [below](#measured-results-honest-version).

---

## Contents
[The problem](#the-problem) · [How it works](#how-it-works) · [Where it sits in the security stack](#where-it-sits-in-the-security-stack) · [API at a glance](#api-at-a-glance) · [What the AI does](#what-the-ai-does) · [Measured results](#measured-results-honest-version) · [Limitations](#limitations-and-threat-model) · [Repository layout](#repository-layout) · [Quick start](#quick-start) · [Configuration](#configuration) · [Data, licenses, third-party assets](#data-licenses-and-third-party-assets) · [Privacy](#privacy) · [Documentation](#documentation) · [Status](#status)

## The problem

When a phone is taken over, money leaves through the victim's *own* app, PIN and device, so every classic check says "legitimate".

| | Scenario A — remote-controlled malware | Scenario B — someone holding the phone who knows the PIN |
|---|---|---|
| How it happens | Victim installs a fake APK and grants Accessibility permission; the malware reads the screen and OTPs and taps through a transfer (families such as RedHook, Gigabud, SpyNote were reported in 2026) | A relative or thief watched the PIN |
| Why it slips through | PIN, OTP and device are all "correct" | Same |
| What gives it away | The touch is **not a human finger**: too regular, exactly on key centres, text set without keystrokes, replayed | The touch is human but **does not match the owner's habits** |

Mobile ATT&CK files accessibility-driven abuse under *Input Injection* (T1516). Innate does not detect the malware; it detects the *effect* of the malware on how the screen is touched.

## How it works

```
First use (enrolment)     enter the PIN / a transfer 3–5 times  ->  store a small "habit template"
Every later transaction   behave as usual  ->  compare with the template + check "human or machine?"
                          ->  allow | step_up (stronger auth) | hold   + human-readable reasons
```

Two different things are called "training" — keep them apart:

| | Offline training (once, by us) | Enrolment (per user, at first use) |
|---|---|---|
| Data | Many people (public data now, the team's data later) | 3–5 entries by that one user |
| What is learned | What humans and bots look like; population priors | **No per-user model**: only the mean and spread of each feature |

Three matchings run on every scored session. All are **1:1 verification**, not identification:

| Check | Compares | Needs enrolment? | Catches |
|---|---|---|---|
| **Human vs machine** | current session ↔ pattern of real humans (rules + LightGBM) | No | scripts, `adb`, naive malware (A) |
| **Owner match** | current session ↔ the owner's template | Yes | someone who knows the PIN (B) |
| **Replay** | current session ↔ the account's own past sessions (suspiciously identical) | No | malware that recorded the victim's real input |

The three outputs are fused with transaction context (new recipient, unusual amount) into `allow | step_up | hold`, plus a Vietnamese explanation built from fixed templates. **No LLM sits on the decision path** (latency, consistency, auditability).

## Where it sits in the security stack

```
1. Device / app integrity   (attestation, root/hook checks)     "is this device clean?"
2. Authentication           (PIN, OTP, face, fingerprint)        "does this person know/have/are?"
3. INNATE                   (passive behaviour)                  "human or machine? the owner?"
4. Transaction risk         (amount, recipient, history)         "is this transaction unusual?"
5. Operations               (dashboard, step-up, review)
```

It complements the other layers: sophisticated malware may pass layer 1 and a shoulder-surfer passes layer 2, but neither reproduces the owner's touch behaviour. Details: [`docs/plan/positioning.md`](docs/plan/positioning.md), [`docs/plan/how-it-works.md`](docs/plan/how-it-works.md).

## API at a glance

FastAPI service with a JavaScript SDK (Pointer Events; a demo wallet at `backend/app/static/wallet.html`). The SDK records **only timings, coordinates, event kinds and character counts — never content.**

| Method | Path | Key scope | Purpose |
|---|---|---|---|
| GET | `/health` | none | liveness |
| POST | `/v1/sessions` | SDK | upload a session (PIN taps, swipes, screens, optional text-field events) |
| POST | `/v1/users/{id}/enroll` | SDK | mark a session as an enrolment entry (template from the 3rd; **409** once a template exists) |
| GET | `/v1/users/{id}` | SDK | enrolment status |
| POST | `/v1/sessions/{id}/score` | SDK | score at confirmation: `{recipient_is_new, amount}` -> score, action, reasons |
| GET | `/v1/sessions` | ops | dashboard list (flagged sessions) |
| POST | `/v1/sessions/{id}/label` | ops | analyst marks `fraud` / `legit` |
| GET | `/v1/export` | ml | paged export for research (`limit <= 2000`, `X-Next-Offset`) |

Example `/score` response (reasons are codes; the explanation text is Vietnamese):

```json
{
  "session_id": "s_8f21c3a90d4b",
  "human_score": 0.97,
  "owner_match": 0.31,
  "risk": "medium",
  "risk_score": 0.403,
  "action": "step_up",
  "reasons": ["pin_rhythm_slower_40pct", "tap_offset_right", "new_recipient"],
  "explanation_vi": "Thao tác giống người thật nhưng không khớp thói quen của chủ tài khoản (...). Đề nghị xác thực khuôn mặt trước khi chuyển."
}
```

Interactive docs at `/docs` (Swagger). Full data contract (including the optional `fields` events for amount / recipient / note): [`backend/README.md`](backend/README.md).

## What the AI does

| Component | Method | Where |
|---|---|---|
| Features | per-key hold/flight times, tap offset from key centre (normalised by key size), swipe shape, text-field rhythm | `backend/app/scoring/features.py`, `bot_features.py` |
| Owner match | enrolled mean + spread, scaled distance; spread of **timing** features is *shrunk toward a population prior* (few-shot), offset features keep a spread floor | `owner.py`, `population_prior.json` |
| Human vs machine | naturalness rules **plus** an optional LightGBM model (trained on real human PIN sessions + generated bots; see [limits](#limitations-and-threat-model)) | `human.py`, `human_model.py`, `app/models/` |
| Replay check | distance to the account's last 50 sessions; near-duplicate => replay | `replay.py` |
| Template safety | slow, drift-capped template updates so an attacker cannot "teach" the template (poisoning, Lovisotto 2020) | `owner.py` |
| Fusion + explanation | normalised weighted sum -> `allow` / `step_up` / `hold` (thresholds configurable); reasons from per-feature contributions | `fusion.py`, `explain.py` |
| Text fields | amount / recipient / note: typing rhythm, paste vs typed vs **text set without keystrokes** (`ACTION_SET_TEXT`-style) | `features.py`, `human.py` |

Every method choice is backed by an experiment in `research/` and logged in [`docs/research/ai-research.md`](docs/research/ai-research.md).

## Measured results (honest version)

All numbers below come from **public data from other people** (StrokePIN, CMU DSL). **No number yet comes from the team's own data**, and **all bots are generator-made** (no real malware).

| Question | Setting | Result |
|---|---|---|
| Owner match | StrokePIN, 97 users, 6-digit PINs, attacker **knows the PIN**, 3 enrolment entries, same posture | **EER 0.146**; at FRR 5% the false-accept rate is **0.495** (0.663 before the population-shrinkage change; paired CI excludes 0) |
| Owner match, posture change | enrol sitting, test walking | EER ~0.35, FAR@FRR5% 0.94 — the signal is mostly lost |
| Human vs machine | real humans + generator bots, person-disjoint splits | naive bots (constant rhythm / exact centres): **100%** caught; replay of a real human: 12–26%; population-sampling bot: 20–73% |
| Replay check | threshold 0.07, calibrated on real humans | catches 100% of replays with up to ±10% added noise, 29% at ±15%, 0% from ±20%; human false-positive ~0.1% (8 past sessions) |
| Poisoning (synthetic) | slow template "teaching" | without a drift cap the attacker is accepted 100% and the owner is locked out; the cap bounds but does not remove the damage |

What this means: the owner signal is **weaker than papers suggest** (EER 16–20%, not "a few percent") and must be used as a **risk signal that triggers step-up**, never as a gate.

## Limitations and threat model

- Behavioural habits are *hard*, not *impossible*, to imitate: published imitation attacks raise error rates to 10–15%; adaptive system-level agents were reported to defeat touch + IMU detectors 71–77% of the time (Wang 2026, ActReal, preprint).
- Enrolment must cover several postures and sittings; a sit-only template barely works while walking. The current **enrolment lock (409)** conflicts with that need — a controlled re-enrolment path is not designed yet.
- Web SDKs cannot see text set without keystrokes and get no touch coordinates on the system keyboard; a native SDK is needed for the strongest signals.
- The LightGBM model and the population prior are **interim**: trained on public people (StrokePIN) and generated bots. Replace with the team's data and real `adb` / `dispatchGesture` bots.
- Browsers may report contact size as 1 when hardware cannot measure it, so contact-size features are excluded from the learned model.
- Out of scope: detecting the malware itself, content-based scam detection, replacing authentication.

## Repository layout

| Path | Content |
|---|---|
| `backend/` | FastAPI service, scoring code (`app/scoring/`), optional LightGBM model (`app/models/`), demo wallet + SDK (`app/static/wallet.html`), tests |
| `attacker/` | Bot simulator: 4 tactics (even taps → timing noise → replay → sampling from human distributions) and a real-phone `adb` attack |
| `research/` | Experiment code (`experiments/`), result tables (`results/`), downloaded data (`data/`, **git-ignored**) |
| `docs/` | `contest/` rules and submission checklist · `plan/` positioning, how it works, pitch · `research/` research plan, AI research log, datasets · `submission/` README skeleton for the contest |
| `papers/` | Reference PDFs (not part of the submission) |
| `CLAUDE.md` | Conventions and known gaps for AI-assisted work in this repo |

## Quick start

Requirements: Python 3.11+, [`uv`](https://docs.astral.sh/uv/).

```bash
cd backend
uv sync --extra ml                 # `ml` = LightGBM + NumPy (optional; without it the rule baseline is used)
uv run uvicorn app.main:app --reload --port 8000
# http://localhost:8000        demo wallet (demo PIN 159357)
# http://localhost:8000/docs   Swagger (local SQLite default SDK key: demo-key)
uv run pytest -q                   # 25 tests

cd ../attacker && uv sync && uv run pytest -q    # 7 tests
```

Reproduce the experiments (needs `numpy pandas scikit-learn lightgbm`; data is downloaded separately):

```bash
git clone https://github.com/Litraveler/StrokePIN.git research/data/StrokePIN    # CC BY-NC-SA 4.0
cd research
python experiments/e9_strokepin_owner.py        # owner match on real PINs
python experiments/e10b_backend_path.py         # the backend's own owner.py, leave-one-user-out prior
python experiments/e4b_human_bot_real.py        # human vs machine, real humans
python experiments/e5b_replay_real.py           # replay-threshold calibration
```

Each script writes a table to `research/results/`; the list of experiments (E1–E10b) and what each one showed is in [`docs/research/ai-research.md`](docs/research/ai-research.md). Dataset links, sizes and licences: [`docs/research/datasets.md`](docs/research/datasets.md).

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./nhip.db` | SQLite locally, Postgres in production |
| `NHIP_API_KEYS` | `demo-key` on local SQLite only | SDK key(s); no public default when a real database is connected |
| `NHIP_OPS_KEYS` / `NHIP_ML_KEYS` | none (routes closed) | dashboard / ML-export keys; wrong scope returns 403 |
| `NHIP_CORS_ORIGINS` | `*` | set to the real wallet/dashboard origins |
| `NHIP_THRESHOLD_A` / `_B` | `0.25` / `0.55` | risk below A → `allow`, above B → `hold`, between → `step_up` |
| `NHIP_HUMAN_MODEL` | `on` | `off` disables the LightGBM model (rules only) |
| `NHIP_POP_PRIOR` | `on` | `off` disables the population prior (spread floor only) |
| `NHIP_REPLAY_THRESHOLD` | `0.07` | replay distance threshold |

The `NHIP_` prefix is a legacy identifier from an earlier project name; it is kept so the deployed service does not break.

## Data, licenses and third-party assets

| Asset | Used for | License / terms |
|---|---|---|
| **StrokePIN** (Yao & Wang, IEEE TDSC 2026) | owner-match evaluation; training the human/bot model; the population prior | **CC BY-NC-SA 4.0** (non-commercial, attribution, **share-alike**). The model files in `backend/app/models/` and `population_prior.json` are derived from it and are therefore under the same terms |
| CMU DSL-StrongPassword (Killourhy & Maxion 2009) | few-shot experiment (`research/` only) | no licence stated on the source page |
| Touchalytics, Aalto typing37k | inspected locally; not used in any reported number yet | licence to be checked before use |
| Open-source libraries | FastAPI, SQLAlchemy, LightGBM, NumPy, pandas, scikit-learn, pytest | their own licences |
| AI tooling | Claude Code (Anthropic) assisted with code, experiments and documentation; every reported number is produced by code in `research/` and can be re-run | — |

`papers/` contains third-party PDFs for reference only. **The repository code itself does not yet carry a licence — to be decided by the team.**

## Privacy

Innate stores timings, coordinates, event kinds and character counts. It **never stores PIN content, amounts, recipient numbers or message text.** Touch and typing dynamics are treated as sensitive biometric-like data (Vietnam's 2025 personal-data law and Decree 356/2025 apply from 2026-01-01): collect only with explicit consent. Habit templates live on the server in this design (unlike a phone's secure enclave), so they must be protected accordingly.

## Documentation

| Read this | For |
|---|---|
| [`docs/plan/positioning.md`](docs/plan/positioning.md) | what Innate is and is not, where it sits, how to pitch it |
| [`docs/plan/how-it-works.md`](docs/plan/how-it-works.md) | enrolment vs training, comparison with Face ID, enrolment advice |
| [`docs/research/ai-research.md`](docs/research/ai-research.md) | every experiment (E1–E10b), hypotheses, results, limits |
| [`docs/research/research-plan.md`](docs/research/research-plan.md) | open research questions (R1–R9) |
| [`docs/contest/submission-checklist.md`](docs/contest/submission-checklist.md) | what must be submitted and when |
| [`docs/submission/README.submission.md`](docs/submission/README.submission.md) | skeleton of the README that ships with the contest submission |
| [`backend/README.md`](backend/README.md), [`attacker/README.md`](attacker/README.md) | service data contract; bot simulator |

## Status

Work in progress for the contest (submission deadline **2026-12-03 23:59**; the product must stay online until 2026-12-11).

- Done: scoring API, owner match with shrinkage, replay check, learned human/bot model (interim), text-field signals, bot simulator, experiments E1–E10b, documentation.
- Next: collect real sessions from consenting participants (two sittings, one phone), real bots via `adb`/`dispatchGesture`, retrain and recalibrate on the team's data, a controlled re-enrolment path, deploy and a web front end.
