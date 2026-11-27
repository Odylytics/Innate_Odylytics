# Innate

**A human-verification layer for digital-wallet transactions.** Innate runs silently when a payment is confirmed and uses AI to match *how* the person touches and types against the owner's enrolled habits and against what real humans look like. It answers two questions before the money moves:

1. **Human or machine?** (accessibility-service malware, `adb`, scripts)
2. **If human, the account owner?** (someone who watched the PIN)

> *A PIN can be stolen. Touch habits are very hard to steal.* ("innate" = *bẩm sinh*) · Built for the **MoMo Tech Contest 2026** by **Team Odylytics** (Powered by Odylytics). All project documents are in English. The decision reasons and explanations that wallet users see, and the Vietnamese version of the website, stay in Vietnamese by design.

**Live demo: https://innate.odylytics.com** (no login; guided story at `/#/demo?story=1`) · API docs: https://nhip-api-taupe.vercel.app/docs

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

**Innate Challenge** (design: [`docs/plan/innate-challenge.md`](docs/plan/innate-challenge.md)): more keystrokes give more signal. On 2,260 real typists, going from 6 to 30 keystrokes cut the false-accept rate at FRR 5% from 81% to 49%. With the learned verifier and 3 enrolment phrases the false-accept rate stays around 43–52% (E22): it helps, it does not turn the owner score into a gate. The phrase is a random Vietnamese sentence served by `GET /v1/challenge` with a single-use signed token; typing it through Telex/VNI exposes extra style signals (tone-key position, corrections, whether an IME was used) that a replayed rhythm does not carry. **That Vietnamese channel is a hypothesis: no real Vietnamese typists have been measured yet** ([`docs/plan/innate-challenge-vi.md`](docs/plan/innate-challenge-vi.md)).

## What is inside

| Part | What | Where |
|---|---|---|
| API | FastAPI scoring service (the mobile demo app will send only timings/coordinates/event kinds, no content) | `backend/` |
| Learned models (interim) | LightGBM human-vs-bot and owner-match models, population prior; all optional with rule/distance fallback | `backend/app/models/`, `backend/app/scoring/` |
| Bot simulator | 4 tactics (even taps → timing noise → replay → sampling human distributions), text-field bots, real-phone `adb` attack | `attacker/` |
| Phone SDK + probe | text-input recorder for phones (IME "transform" keys), keyboard probe page | `sdk/` |
| Web | landing page, demo wallet, attacker console, data-collection page, ops view | `web/` |
| Submission pack | 1-page product guide, editable PPTX deck + PDF, source README; rebuilt with one command | `submission/` (generated), `tools/` |
| Research | every experiment (E1–E32) with code and result tables; team-data pipeline | `research/` ([`EXPERIMENTS.md`](research/EXPERIMENTS.md)), `docs/research/ai-research.md` |

Endpoints (key scopes SDK / ops / ml): `POST /v1/sessions`, `POST /v1/users/{id}/enroll`, `GET /v1/users/{id}`, `POST /v1/sessions/{id}/score`, `GET /v1/sessions` and `POST …/label` (ops), `GET /v1/export` (ml), `GET /v1/challenge` (random Vietnamese phrase + single-use token), Swagger at `/docs`. Data contract: [`backend/README.md`](backend/README.md).

## Measured results

All from **public data of other people** (StrokePIN, Aalto, CMU DSL); **none yet from the team's own data**; **all bots are generator-made**.

| Question | Result |
|---|---|
| Owner match: 97 users, 6-digit PINs, attacker **knows the PIN**, 3 enrolment entries, person-disjoint, contact size excluded | distance baseline: EER 0.161, false-accept **0.573** at FRR 5% → learned model: EER 0.158, false-accept **0.375** (paired CI excludes 0). After a posture change (sit→walk): EER 0.31, false-accept 0.71 |
| Human vs machine: real humans, generator bots | naive bots (even rhythm, exact key centres, timing noise): **100%** caught; population-sampling bot 20–73%; unseen bot families are weak |
| Replay check (threshold calibrated on real humans) | catches 100% of replays with ≤ ±10% added noise, 29% at ±15%, 0% from ±20%; human false-positive ≈ 0.1% |

| **Whole system** (E29: `/score` chain on 97 people, 5-fold cross-validation by person, models retrained per fold, known recipient) | owner sitting: 76% allow / 23% step_up / 1% hold (walking: 49% allow); PIN-knowing stranger (other phone): 22% / 77% / 1%; naive bots and replay ≤ ±10%: **100% hold**; population-sampling bot: 3% allow; with learned models off (rules only) the PIN-knowing stranger is allowed 89% of the time |
| **Adaptive attackers** (E29) | replay with ±15–30% noise: 32–58% **allowed**; a bot that knows the victim's template: 72–87% allowed. The replay threshold is 0.07 (E5b, real humans): raising it to 0.085 would catch ±15% replay (86% instead of 29%) but its false-hold rate on long histories extrapolates to about 3.7% at 50 sessions (about 0.7% at 0.07) |
| Swipe rule (E19: Touchalytics, 41 people, 20,896 strokes) | uniform-speed rule: 0 human strokes flagged, 100% of uniform bots caught; the old "straightness" rule flagged 13% of human sessions (replaced). Swipes do **not** identify the owner (AUC ≈ 0.5) |
| Fine-tuned TypeFormer (E32: Aalto-pretrained Transformer fine-tuned on StrokePIN, 30 unseen people, 3 enrolments) | EER 0.292 → **0.203**, false-accept at FRR 5% 0.706 → **0.418** (walking: 0.848 → 0.661). One run, no CI, not the 97-person protocol, **not in the API** |
| Latency (E26, local) | `/score` p50 3.7 ms, p99 14 ms (no network, Vercel cold start or Neon) |

So the owner signal is **weaker than papers suggest** (EER 16%, not "a few percent"): use it to trigger step-up, never as a gate.

## Limitations

- Habits are *hard*, not *impossible*, to imitate; adaptive system-level agents were reported to beat touch+IMU detectors 71–77% of the time (ActReal 2026).
- Enrolment must cover several postures; a sit-only template barely works while walking. The enrolment lock (409 once a template exists) conflicts with that need; a controlled re-enrolment path is not designed yet.
- Web SDKs cannot see text set without keystrokes and get no coordinates on the system keyboard; a native SDK is needed.
- Bots that replay with ≥ 15% noise or know the owner's template **pass**; four evidence channels (motion, PIN, typed phrase, touch/swipe) raise the bar but are not proven against adaptive attackers ([`docs/plan/bon-cong-pipeline.md`](docs/plan/bon-cong-pipeline.md)). Phone motion sensors looked excellent for owner matching (EER 0.04) only because each person used a different phone and they fail after a posture change (E23): not claimed.
- Models are **interim**: public people + generated bots. Retrain on team data with `research/experiments/train_human_model.py --export …`.
- Out of scope: detecting the malware itself, content-based scam detection, replacing authentication.

## Repository layout

Start at **[`docs/INDEX.md`](docs/INDEX.md)** (map of every folder and document) and **[`research/EXPERIMENTS.md`](research/EXPERIMENTS.md)** (index of experiments E1–E32 with code, result tables and one-line conclusions).

`backend/` service, scoring core (`app/scoring/`), models, tests · `attacker/` bot simulator · `sdk/` phone text-input SDK + keyboard probe · `web/` landing, demo, data-collection page · `research/` experiments, results, `finetune/` (TypeFormer, E32), git-ignored `data/` and `external/` · `tools/` builds the submission files (`build_submission.sh`, editable deck `build_pptx.js`) · `submission/` generated hand-in pack · `docs/brand/` brand kit and asset pack · `docs/` (`contest/` rules + checklist + BTC questions, `plan/` positioning / how-it-works / challenge / data collection, `research/` logs and related work, `submission/` proposal, slides, scripts, README skeleton) · `papers/` reference PDFs (not submitted) · `LICENSE`, `THIRD_PARTY_NOTICES.md` · `CLAUDE.md` conventions and known gaps.

## Quick start

Python 3.11+, [`uv`](https://docs.astral.sh/uv/).

```bash
cd backend && uv sync --extra ml        # ml = LightGBM + NumPy (optional)
uv run uvicorn app.main:app --reload --port 8000    # Swagger at /docs (local default key: demo-key)
uv run pytest -q                        # 43 tests
cd ../attacker && uv sync && uv run pytest -q       # 8 tests
cd ../web && npm install && npm run dev            # website + demo wallet (needs VITE_SDK_KEY for live scoring)
```

Build the submission files (macOS with PowerPoint; the PDF is exported from the PPTX; Sora + Manrope fonts in `tools/fonts/`):

```bash
npm --prefix tools i pptxgenjs && tools/build_submission.sh   # -> submission/{Product,Slide,Document}
```

Reproduce an experiment (needs `numpy pandas scikit-learn lightgbm`; data is downloaded separately, see [`docs/research/datasets.md`](docs/research/datasets.md)):

```bash
git clone https://github.com/Litraveler/StrokePIN.git research/data/StrokePIN   # CC BY-NC-SA 4.0
cd research && python experiments/e12_learned_owner.py --no-contact              # owner match, learned model
```

Config (env): `DATABASE_URL`, `NHIP_API_KEYS` / `NHIP_OPS_KEYS` / `NHIP_ML_KEYS`, `NHIP_CORS_ORIGINS`, `NHIP_THRESHOLD_A/B` (0.25 / 0.55), `NHIP_HUMAN_MODEL` / `NHIP_OWNER_MODEL` / `NHIP_POP_PRIOR` (`off` disables), `NHIP_REPLAY_THRESHOLD` (0.07). `NHIP_` is a legacy prefix kept so the deployed service does not break.

## Data, licences, privacy

- **Licence of this repository: CC BY-NC-SA 4.0** ([`LICENSE`](LICENSE)). Reason: the models and `population_prior.json` are derived from **StrokePIN** (Nankai University, CC BY-NC-SA 4.0: share derivatives under the same licence; commercial use needs written authorisation from the dataset owner). Third-party libraries, fonts and avatars keep their own licences: see [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) (checked 2026-11-25).
- **Aalto typing37k, Touchalytics, CMU DSL**: state no data licence ("openly available", cite the paper); used for research experiments only, no data or derived model is shipped. Contact the authors before redistributing anything derived.
- Open-source libraries keep their own licences (note: psycopg is LGPL-3.0, used unmodified). Claude Code (Anthropic) assisted with code, experiments and docs; every reported number comes from code in `research/`.
- Only timings, coordinates, event kinds and character counts are stored: **never PIN content, amounts, recipients or message text.** Touch and typing dynamics are sensitive biometric-like data (Vietnam's 2025 personal-data law, Decree 356/2025): collect only with explicit consent ([`docs/plan/thu-du-lieu-doi.md`](docs/plan/thu-du-lieu-doi.md)).

## Status

*Updated 2026-11-27.* Contest deadline **2026-12-03 23:59** (product online until 2026-12-11).

- **Online:** website https://innate.odylytics.com and API https://nhip-api-taupe.vercel.app (`/health` 200, learned models on). Tests: backend 43, attacker 8, phone SDK 4.
- **Submission pack built** (`submission/`): 1-page product guide (PDF), 10-slide deck (editable PPTX + PDF, English), source zip + README. Remaining placeholder: team-collected data counts in the README (`TODO`). The video is not recorded yet.
- **Research:** E1-E32. Newest: E31 fusion tuning (marginal), E32 TypeFormer fine-tune (EER 0.29 to 0.20 on 30 unseen people; research only, not in the API).
- **Open:** real consented data and real `adb` bots; retrain and recalibrate; native SDK (text set directly, device motion); controlled re-enrolment; ship the fine-tuned model behind the API (needs a numpy/ONNX path, Vercel has no torch).

Map of all folders and documents: [`docs/INDEX.md`](docs/INDEX.md). Licence: CC BY-NC-SA 4.0 ([`LICENSE`](LICENSE), [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)).
