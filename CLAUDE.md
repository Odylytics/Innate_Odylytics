# CLAUDE.md

Innate — behavioral risk scoring (touch/PIN dynamics) for e-wallets. Entry for MoMo Tech Contest 2026.
Docs are in Vietnamese; keep user-facing text (reasons, explanations) in Vietnamese.

## Naming
- Project/product name: **Innate** ("bẩm sinh"). History: "Nhịp" → TIBOM → Innate (24/11/2026). Use Innate in all user-facing text, docs, slides. Pitch line: *PIN can be stolen, innate touch habits are hard to steal* (see `docs/plan/pitch-story.md` for the honest framing).
- Vietnamese word "nhịp" (rhythm: "nhịp PIN", "nhịp gõ", "đăng ký nhịp") is NOT a brand; keep it where it means rhythm.
- Technical identifiers still say `nhip` on purpose, to avoid breaking the live deploy: env vars `NHIP_*`, Python package `nhip_attacker`, Vercel project `nhip-api` / URL `nhip-api-taupe.vercel.app`, Neon DB `nhip-db`, localStorage keys `nhip_*`. Rename them together with a redeploy (and a new URL for the submission PDF) if/when wanted.

## Scope (24/11/2026)
- Focus is the AI core (`backend/app/scoring/`, `attacker/`). The web/demo is built later by other team members: do NOT work on the wallet (`app/static/wallet.html`), the `nhip-api` deploy, or the dashboard unless asked. Code stays in the repo.
- AI research: `docs/research/ai-research.md` (design, experiments E1–E7), `docs/research/datasets.md` (verified dataset links), `research/` (experiment code; E1/E2 proxy done on DSL-StrongPassword).

## Deadlines (2026)
- 27/11 23:59 — registration + clarification questions to BTC
- 03/12 23:59 — submission (zip + README, slides ≤10pp PDF, video ≤3min, 1-page PDF). No edits after.
- 11/12 — final; product must stay online until then.

## Layout
- `backend/` — FastAPI + SQLAlchemy (SQLite local, Neon Postgres on Vercel). Entry `app/main.py`, Vercel entry `index.py`.
  - `app/scoring/`: `features.py` (extract), `human.py` (bot-vs-human, rule baseline), `owner.py` (scaled Manhattan template + drift-capped update), `fusion.py` (weighted risk, thresholds A/B), `explain.py` (Vietnamese reasons).
  - `tests/synth.py` generates fake human sessions for tests.
- `attacker/nhip_attacker/` — 4-tactic bot simulator (`tactics.py`), CLI (`__main__.py`: `generate`, `report`, `adb`), real-phone attack (`adb.py`).
- `docs/plan/innate-momo-tech-contest.md` — the full plan (architecture, models, evaluation, demo script, roles). Source of truth for intent.
- `docs/plan/positioning.md` — WHAT Innate is: a human-verification layer (passive behavioral security) at transaction confirmation; complements attestation/auth/fraud engines; AI does 1:1 matching (human-vs-bot, owner, replay). Read before writing any pitch/README text. Do NOT use the phrase "HUMAN Security" (a company name).
- `docs/plan/mo-ta-du-an-va-kiem-chung.md` — description, state, paper verification, conclusions.
- `docs/contest/` — rules summary + `submission-checklist.md` (what must be submitted, by 03/12).
- `docs/research/` — `research-plan.md` (R1–R8), `tech-notes.md` (findings), `paper-report.md`, `notes/`. `papers/` — PDFs (keep out of the submission zip).
- `SessionIn.fields` = text-field events (amount/recipient/note): only time, kind (key/paste/delete/set_text) and char count, NEVER content. `set_text` on `amount` => rule `text_set_without_keys` (unvalidated, R9). Web SDK cannot emit `set_text`.
- `backend/app/static/wallet.html` — demo wallet + JS SDK (6-digit demo PIN 159357), served at `/`.
- Population-variance shrinkage for TIMING features is in `owner.py` (`population_prior.json`, nu=5; off with `NHIP_POP_PRIOR=off`); offsets deliberately keep the sd floor (shrinking them hurts, E10). Human/bot LightGBM is wired in `/score` via `scoring/human_model.py` (optional, `NHIP_HUMAN_MODEL=off`; model files in `app/models/` are TEMPORARY: StrokePIN humans + generator bots). Both derive from CC BY-NC-SA 4.0 data: declare in the submission README.
- Not built yet: ops dashboard, trained LightGBM/RF model, real data. Replay check exists (`scoring/replay.py`, wired in `/score`, threshold from SYNTHETIC data, recalibrate on real data).

## Commands (PowerShell-style in READMEs; uses `uv`)
- Backend: `cd backend; uv sync; uv run uvicorn app.main:app --reload --port 8000` (Swagger at /docs, key `demo-key`)
- Backend tests: `cd backend; uv run pytest -q`
- Attacker tests: `cd attacker; uv run pytest -q`
- Attacker CLI: `uv run python -m nhip_attacker report --enroll-synth --n 40` (needs `NHIP_API_KEY`)
- Deploy: `cd backend; vercel deploy --prod`

## Env vars (backend)
`DATABASE_URL`, `NHIP_API_KEYS`, `NHIP_CORS_ORIGINS`, `NHIP_THRESHOLD_A` (0.25), `NHIP_THRESHOLD_B` (0.55).

## Design rules — do not break
- ML/rules decide; an LLM may only explain, never sit on the decision path.
- System recommends `allow | step_up | hold`; it never locks accounts.
- Store only timings + coordinates (+ key label). Never PIN content. Touch data is sensitive under VN law (Luật BVDLCN 2025) — consent required.
- Don't rely on `pressure` or `isTrusted`.
- Evaluation per FETA: time-split enroll/test, one device, no impostor data in owner-model training, leave-users-out for pairwise models. Headline metric FAR@FRR=5%.
- Owner template updates only after confident `allow` + correct PIN; keep the drift cap.
- No MoMo branding/UI copying. List all existing assets, OSS libs and AI tools used in the submission README (omission = disqualification).
- Synthetic-human results (attacker README table) must not go on slides; re-measure on real data.

## Known gaps
- **Enrollment lock vs multi-posture enrolment:** `/enroll` now returns 409 once a template exists (security fix by tuannghia2457, prevents injecting someone else's rhythm). But E9 shows enrolment must cover several postures/sittings (sit->walk breaks the signal), so a controlled re-enrol path (e.g. after a step-up authentication) is still needed. Not designed yet.
- API keys are scoped by role: SDK `NHIP_API_KEYS`, dashboard `NHIP_OPS_KEYS`, ML export `NHIP_ML_KEYS` (ops/ml closed when unset).
- Replay (tactic 3): threshold 0.07, calibrated on REAL humans (E5b): catches 100% up to ±10% attacker noise, 29% at ±15%, 0% from ±20%. Human FPR grows with history size (~0.1% at 8 sessions, extrapolated ~0.7% at 50); recalibrate on team data with long histories.
- `owner.py` score mapping (d=2 → 0.5) is uncalibrated and too lenient (also: owner signal alone is weak, E9/E10b: FAR ~50% at FRR 5%): on synthetic data 56% of real impostor sessions already score >= 0.5 before any poisoning (E7). Calibrate on real data (E3). E7 recommends "freeze + flag" over the per-feature 1 sd cap (not yet applied).
- Bot model train/test share the same 4 generators; keep `adb`/real malware sessions as an independent test set.
