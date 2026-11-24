# CLAUDE.md

Nhịp — behavioral risk scoring (touch/PIN dynamics) for e-wallets. Entry for MoMo Tech Contest 2026.
Docs are in Vietnamese; keep user-facing text (reasons, explanations) in Vietnamese.

## Deadlines (2026)
- 27/11 23:59 — registration + clarification questions to BTC
- 03/12 23:59 — submission (zip + README, slides ≤10pp PDF, video ≤3min, 1-page PDF). No edits after.
- 11/12 — final; product must stay online until then.

## Layout
- `backend/` — FastAPI + SQLAlchemy (SQLite local, Neon Postgres on Vercel). Entry `app/main.py`, Vercel entry `index.py`.
  - `app/scoring/`: `features.py` (extract), `human.py` (bot-vs-human, rule baseline), `owner.py` (scaled Manhattan template + drift-capped update), `fusion.py` (weighted risk, thresholds A/B), `explain.py` (Vietnamese reasons).
  - `tests/synth.py` generates fake human sessions for tests.
- `attacker/nhip_attacker/` — 4-tactic bot simulator (`tactics.py`), CLI (`__main__.py`: `generate`, `report`, `adb`), real-phone attack (`adb.py`).
- `nhip-momo-tech-contest.md` — the full plan (architecture, models, evaluation, demo script, roles). Source of truth for intent.
- `the-le-cuoc-thi.md` — contest rules summary. `reports/`, `research_notes/`, `papers/` — literature.
- Not built yet: JS SDK, demo wallet (custom PIN keypad), ops dashboard, trained LightGBM/RF model, real data.

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
- Tactic 3 (replay) is uncaught: add "near-duplicate of an old session" check in backend.
- `owner.py` score mapping (d=2 → 0.5) is uncalibrated and too lenient (tactic 4); calibrate on real data.
- Bot model train/test share the same 4 generators; keep `adb`/real malware sessions as an independent test set.
