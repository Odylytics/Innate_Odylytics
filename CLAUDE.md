# CLAUDE.md

Innate — behavioral risk scoring (touch/PIN dynamics) for e-wallets. Entry for MoMo Tech Contest 2026.
Docs are in Vietnamese; keep user-facing text (reasons, explanations) in Vietnamese.

## Where things are
Start at `docs/INDEX.md` (folder map + which doc answers what) and `research/EXPERIMENTS.md` (E1-E32: script, result file, one-line conclusion). Licence decision (25/11): whole repo CC BY-NC-SA 4.0 (`LICENSE`) because models derive from StrokePIN; third-party list in `THIRD_PARTY_NOTICES.md` (Aalto/Touchalytics/CMU state NO data licence: research only, nothing derived shipped; psycopg is LGPL-3.0; avatars CC0).

## Naming
- Project/product name: **Innate** ("bẩm sinh"). History: "Nhịp" → TIBOM → Innate (24/11/2026). Use Innate in all user-facing text, docs, slides. Pitch line: *PIN can be stolen, innate touch habits are hard to steal* (see `docs/plan/pitch-story.md` for the honest framing).
- Vietnamese word "nhịp" (rhythm: "nhịp PIN", "nhịp gõ", "đăng ký nhịp") is NOT a brand; keep it where it means rhythm.
- Technical identifiers still say `nhip` on purpose, to avoid breaking the live deploy: env vars `NHIP_*`, Python package `nhip_attacker`, Vercel project `nhip-api` / URL `nhip-api-taupe.vercel.app`, Neon DB `nhip-db`, localStorage keys `nhip_*`. Rename them together with a redeploy (and a new URL for the submission PDF) if/when wanted.

## Status 27/11/2026 (hand-in pack, deck, fine-tune)
- Live: website https://innate.odylytics.com, API https://nhip-api-taupe.vercel.app. Team name **Odylytics** ("Powered by Odylytics", shown on the deck cover only). Brand: Innate kit + official asset pack in `docs/brand/asset-pack/`; Odylytics logos are derived PNGs in `tools/assets/`.
- Hand-in pack = `submission/{Product,Slide,Document}`, rebuilt by `tools/build_submission.sh` (macOS + Microsoft PowerPoint: the PDF is exported from the PPTX by `tools/lib/export_pdf.applescript`; Chrome headless renders the 1-page guide; `npm --prefix tools i pptxgenjs` once; fonts Sora + Manrope in `tools/fonts/`, install them before editing the PPTX). Source of truth: `tools/build_pptx.js` (deck), `tools/product-guide.html` (guide), `docs/submission/README.submission.md` (README, English). The zip is git-ignored.
- Deck rules agreed with the user: English; numbered sections 01-09 with progress dots; italic grey "Sources:" line in every footer (not on the closing slide); no MoMo name/logo (say "the wallet"); thin line arrows centred in gaps, never block arrows; symmetric blocks centred with equal line counts; no accent stripes/underlines; doughnut/bar charts are native and editable; every figure must trace to `research/` (E29 for decision mix). Order is a generic pitch order (problem, solution, how it works, what changes, product, AI + research, evidence, roadmap, impact), NOT a verified YC/Sequoia flow.
- E32 (`research/finetune/`): TypeFormer fine-tuned on StrokePIN, EER 0.292 to 0.203 and FAR@FRR5% 0.706 to 0.418 on 30 unseen people; one run, no CI, research only. Putting it in the API needs a numpy/ONNX path (Vercel has no torch).
- Still open: `TODO` data counts in the README, video not recorded, real consented data and `adb` bots, `docs/submission/pitch-script.md` still Vietnamese and not synced to the new slides, teammate branch `docs/fix-flow-docs` (unmerged doc fixes from 25/11) not reviewed.

## Scope (24/11/2026)
- Focus is the AI core (`backend/app/scoring/`, `attacker/`). This repo holds the API (`backend/`), the AI research, the bot simulator and the website `web/` (landing page + web demo wallet + guided story + ops dashboard, one Vite app; see `web/README.md`); a mobile demo app is to come. The standalone `Innate_website` repo is superseded by `web/` (26/11/2026). Do NOT work on the `nhip-api` deploy unless asked. Code stays in the repo.
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
- `/` redirects to Swagger (`/docs`); the web demo wallet + JS SDK (`wallet.html`) was removed, no SDK in this repo yet.
- Population-variance shrinkage for TIMING features is in `owner.py` (`population_prior.json`, nu=5; off with `NHIP_POP_PRIOR=off`); offsets deliberately keep the sd floor (shrinking them hurts, E10). Human/bot LightGBM is wired in `/score` via `scoring/human_model.py` (optional, `NHIP_HUMAN_MODEL=off`; model files in `app/models/` are TEMPORARY: StrokePIN humans + generator bots). Both derive from CC BY-NC-SA 4.0 data: declare in the submission README.
- Text-field bot signals (E11, real Aalto typists, note field only): naive bots (set_text, even typing) caught ~100% only when the model has seen them; unseen even-typing bots 0%; replay 6%, population-sampling 31% (58% with extra rhythm stats not yet in `bot_features.py`). Amount-field `set_text` rule still unvalidated (no human data). Attacker can emit fields via `generate(..., with_fields=True)`.
- Learned owner verifier (E12b, no contact-size to avoid device confound): wired via `owner_model.py` (`NHIP_OWNER_MODEL=off`), TEMPORARY. LightGBM cuts FAR@FRR5% 0.573->0.375 same posture, no EER gain same posture; owner still can't be a gate. "Innate Challenge" (type a random letters+digits phrase at step-up): design in `docs/plan/innate-challenge.md`, E13 shows more keystrokes help (EER 0.364->0.245 from 6 to 30 keys, timing-only, Aalto); backend accepts `fields[name="challenge"]` with `expected_len`, no UI/phrase generator yet.
- Vietnamese challenge (Telex/VNI), phone-first: `GET /v1/challenge` (`scoring/challenge.py`, signed token, lowercase letters-only phrases with >=4 tone-choice syllables) -> app sends `fields[challenge].token` -> `features.extract` adds `vi_*` via `scoring/vi_ime.py`; only soft cue `challenge_no_ime` (<=0.3) in `human.py`; `vi_*` deliberately NOT in owner identity (no real Vietnamese data; Aalto is English). Transform keys = `key` with n=0; Telex-vs-VNI is NOT observable on phone web (keyCode 229, cls null). `sdk/innate-compose.js` (node tests, SIMULATED events) + `sdk/probe.html` for a person to verify on real Gboard/iOS. Design/limits: `docs/plan/innate-challenge-vi.md`. Token reuse not prevented.
- E19 (Touchalytics, 41 real people): old swipe rule `straight>0.999` flagged 13% of human sessions -> replaced by `swipe_robotic` (speed CV<0.3, 0/20896 human strokes); swipe features give owner AUC ~0.5 -> `swipe_*` removed from owner identity.
- Related work + E21/E21b (digraph normalisation barely helps, per-digraph profile hurts; Aalto, 1000 people): `docs/research/related-work.md`. No published work found on Telex/VNI or Pinyin-IME typing as a biometric: say "we did not find", not "nobody did".
- 4-evidence-channel design (motion, PIN, typed phrase, touch/swipe) in `docs/plan/bon-cong-pipeline.md`; fuse as risk evidence, NOT 4 sequential AND gates (FRR compounds). E23: IMU gives owner EER 0.04 same posture but it is a DEVICE confound (one phone per person) and useless after posture change; StrokePIN IMU is ~5 Hz. Do not claim IMU owner verification.
- E29 (E24 redone on all 97 people, 5-fold CV by person, models retrained per fold, CIs): PIN-knowing impostor allowed 22% [20,24], owner sit 76%, walk 49%, template-aware bot 72-87%; E30: FAR@FRR5% 0.857 (k=2) -> 0.503 (k=3) -> 0.429 (k=4); prefer these over the 10-person E24 numbers below. E29b = same with learned models OFF (the fallback; the online API ran like this until 26/11): PIN-knowing impostor allowed 89%. Run `python backend/scripts/check_online.py <API URL>` before recording and before each deadline.
- E24-E27 (whole-system decisions on StrokePIN, 10 unseen users): naive bots + replay <=+-10% held 100%; replay +-15..30% and template-aware bots mostly ALLOWED (48-82%); threshold A trades owner friction vs impostor blocking with no free optimum; `/score` p50 3.7 ms local; models are now preloaded at import in main.py (first call used to take ~1 s). `research/results/e24_end_to_end.md`.
- Team data pipeline (dry-run tested on SYNTHETIC data only): `research/experiments/team_data_dryrun.py` (local backend -> export -> analysis -> train), `team_analysis.py export.jsonl` (T1-T5 with bootstrap CIs by person), `train_human_model.py --export export.jsonl --out DIR` (--out or --overwrite is mandatory with --export so it cannot silently replace backend/app/models). Challenge tokens are single-use (`challenge_nonces` table, cue `challenge_token_replayed`).
- Not built yet: ops dashboard, trained LightGBM/RF model, real data. Replay check exists (`scoring/replay.py`, wired in `/score`, threshold from SYNTHETIC data, recalibrate on real data).

- Learned models (human/owner LightGBM) are evaluated by `backend/app/scoring/lgbm_text.py` (pure Python parser of the `.txt` model, no lightgbm/numpy/libgomp; equals lightgbm within 1e-9, `tests/test_lgbm_text.py`). Why: on Vercel lightgbm failed to import (no libgomp) so the online API ran rules only (`/health` models false). lightgbm is now a dev/research dependency only. `/health` showed models true on the live API on 26/11 after the fix; `tests/test_api.py::test_learned_models_load_by_default` guards the default install.

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
- Store only timings + coordinates (+ key label). Never the PIN of a real account. Exception: the `#/collect` research page stores the digits of a throwaway PIN the volunteer creates (with name + email, consent, and a warning not to reuse any real password/PIN); never ship this into the product SDK. Touch data is sensitive under VN law (Luật BVDLCN 2025) — consent required.
- Don't rely on `pressure` or `isTrusted`.
- Evaluation per FETA: time-split enroll/test, one device, no impostor data in owner-model training, leave-users-out for pairwise models. Headline metric FAR@FRR=5%.
- Owner template updates only after confident `allow` + correct PIN; keep the drift cap.
- No MoMo branding/UI copying. List all existing assets, OSS libs and AI tools used in the submission README (omission = disqualification).
- Synthetic-human results (attacker README table) must not go on slides; re-measure on real data.

## Known gaps
- **Open enrollment (demo, 27/11):** `/enroll` with `keep_open=true` keeps enrolling up to 10 entries until `/enroll/finish`; web demo uses it with name login (`judge_<name>`, no password) and an "Accuracy check" bar (E30 measured k<=4, extrapolated above). See `docs/research/person-vs-person.md`.
- **Enrollment lock vs multi-posture enrolment:** `/enroll` now returns 409 once a template exists (security fix by tuannghia2457, prevents injecting someone else's rhythm). But E9 shows enrolment must cover several postures/sittings (sit->walk breaks the signal), so a controlled re-enrol path (e.g. after a step-up authentication) is still needed. Not designed yet.
- API keys are scoped by role: SDK `NHIP_API_KEYS`, dashboard `NHIP_OPS_KEYS`, ML export `NHIP_ML_KEYS` (ops/ml closed when unset).
- Replay (tactic 3): threshold 0.07, calibrated on REAL humans (E5b): catches 100% up to ±10% attacker noise, 29% at ±15%, 0% from ±20%. Human FPR grows with history size (~0.1% at 8 sessions, extrapolated ~0.7% at 50); recalibrate on team data with long histories.
- `owner.py` score mapping (d=2 → 0.5) is uncalibrated and too lenient (also: owner signal alone is weak, E9/E10b/E12b: false-accept 38-57% at FRR 5%): on synthetic data 56% of real impostor sessions already score >= 0.5 before any poisoning (E7). Calibrate on real data (E3). E3 on StrokePIN (`research/results/e3_calibrate_owner.md`): old mapping lets 84% of PIN-knowing impostors score >=0.5; balanced Platt gives 27% (owner 90%) and is wired behind `NHIP_OWNER_MAP=platt` but OFF by default: the learned owner model replaces the score for 6-digit PINs, and Platt (max score ~0.63) breaks new-recipient decisions and the 0.8 template-update gate until A/B and `UPDATE_MIN_OWNER` are retuned (`research/results/e24_platt_map.md`). "Freeze + flag" (E7) is applied in `owner.update` (drift > 0.5 sd => `tpl["frozen"]`); not surfaced in the API yet. Re-enrol design: `docs/plan/dang-ky-lai.md` (not built).
- Bot model train/test share the same 4 generators; keep `adb`/real malware sessions as an independent test set.
