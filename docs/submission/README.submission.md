<p><img src="web/public/brand/lockup.svg" alt="innate" height="44"></p>

# Innate: human verification for digital wallets

*Your behavior is your signature.* Powered by **Odylytics** · MoMo Tech Contest 2026 · Topics: Cybersecurity + Anti-fraud

Innate runs silently when a payment is confirmed. It scores how the person touches and types and answers two questions before the money moves: is this a **human or a bot** (Accessibility malware, `adb`, scripts), and if human, is it **the owner**? The result is `allow`, `step_up` or `hold`, each with a plain-language reason. Innate recommends and never locks an account. It complements PIN, OTP and face checks and does not replace them.

## 1. Try it

| | |
|---|---|
| Demo website | **https://innate.odylytics.com/** (no login). Wallet at `/#/demo`, guided story at `/#/demo?story=1`, data collection at `/#/collect` |
| Scoring API | https://nhip-api-taupe.vercel.app · Swagger at `/docs` · status at `/health` |
| Demo credentials | None needed. Demo PIN `159357` (6 digits). The SDK key is built into the web app |

Demo flow: enroll your rhythm 3 times, send a transfer as the owner (allowed), hand the phone to someone who knows the PIN (step-up), then run the malware simulator (held). The product stays online until 11 Dec 2026. Check it any time with `python backend/scripts/check_online.py <API URL>`.

## 2. How it works

Features (timing, coordinates, event type, character count) feed three checks, fused into one decision. No LLM sits on the decision path.

- **Human or bot:** rules plus a LightGBM model trained on real people and simulated bots, and a replay check against the account's recent sessions.
- **The owner:** normalized distance to the enrollment template with population shrinkage, then a LightGBM model on the deviations.
- **Fusion:** weighted risk score, thresholds A and B, Vietnamese or English reasons.
- **Innate Challenge:** when unsure, the app asks for a short random phrase (server-issued, signed, single-use token) for extra timing signal.

Design notes: [`docs/plan/how-it-works.md`](docs/plan/how-it-works.md), positioning: [`docs/plan/positioning.md`](docs/plan/positioning.md).

## 3. Run locally

```bash
cd backend && uv sync && uv run uvicorn app.main:app --reload --port 8000   # Swagger at /docs, default key demo-key
uv run pytest -q                                                            # backend tests
cd ../attacker && uv sync && uv run pytest -q                               # bot simulator tests
cd .. && node --test sdk/innate-compose.test.js                             # phone input SDK tests
cd web && npm install && npm test && npm run dev                            # website and demo wallet (Vite)
```

Environment: `DATABASE_URL`, `NHIP_API_KEYS` (SDK), `NHIP_OPS_KEYS` (dashboard), `NHIP_ML_KEYS` (ML export), `NHIP_CORS_ORIGINS`, `NHIP_THRESHOLD_A/B`, `NHIP_HUMAN_MODEL=off`, `NHIP_OWNER_MODEL=off`, `NHIP_POP_PRIOR=off`, `NHIP_REPLAY_THRESHOLD`. The `NHIP_*` prefix is a legacy identifier kept so the live deployment keeps working.

## 4. Stack

Python 3.11+, FastAPI, SQLAlchemy (SQLite locally, Postgres in production), LightGBM models evaluated by a pure-Python reader (`backend/app/scoring/lgbm_text.py`, so the server needs no native libraries), React 18 + TypeScript + Vite website in `web/`, a JavaScript SDK, and a phone input SDK (`sdk/innate-compose.js`). Hosting: Vercel (API and web) and Neon Postgres.

## 5. Assets, open-source libraries, AI tools and data

### Open-source libraries
| Library | Used for |
|---|---|
| FastAPI, Uvicorn, SQLAlchemy, psycopg (LGPL-3.0, used unmodified) | Backend API and storage |
| LightGBM, NumPy, scikit-learn, pandas | Training and experiments in `research/` only; the backend reads the model file with `lgbm_text.py` (our code) |
| React, React DOM, Vite, TypeScript, Vitest, Lenis, Tailwind CSS, qrcode-generator, DiceBear | Website and demo wallet in `web/`. Avatars are Notionists by Zoish, CC0 1.0 |
| pytest, httpx | Tests |

### Data
| Source | Used for | License / terms |
|---|---|---|
| **StrokePIN** (Yao & Wang, IEEE TDSC 2026, DOI 10.21227/thft-4721) | Owner evaluation, human/bot training, `population_prior.json` | **CC BY-NC-SA 4.0**. The models in `backend/app/models/` and the prior are derivatives, so the whole package is released under CC BY-NC-SA 4.0 (`LICENSE`). Commercial use needs the data owner's permission |
| CMU DSL-StrongPassword (Killourhy & Maxion 2009) | Few-shot experiments in `research/` | No license stated; cite DSN-2009. Nothing derived ships |
| Touchalytics (Frank et al. 2013) | Swipe-rule checks in `research/` | No license stated. Nothing derived ships |
| Aalto typing37k (Palin et al. 2019) | Typing experiments and the TypeFormer fine-tune in `research/` | No data license stated. Nothing derived ships |
| Team-collected data | Consented volunteers via `/#/collect` | Consent form; timing, coordinates and event types only. Counts: `TODO: people, sessions, dates` |

Bots in `attacker/` are generated by our simulator (4 tactics), not real malware.

### Other assets
| Asset | Source | Notes |
|---|---|---|
| Website design system and frame | **Movago**, an earlier demo site by a team member (Odylytics), reused: `styles.css`, `ui.tsx`, `smooth.ts`, `sound.ts`, `Intro.tsx`, `StoryBar.tsx` | Innate content, wallet, SDK, API client, pages and illustrations are new |
| Innate logo, symbol, wordmark, backgrounds, palette | Innate Brand Identity Kit v1.0 and the brand asset pack (`docs/brand/asset-pack/`, also `web/public/brand/`), made by the team | No third-party brand or logo is used |
| Odylytics logo | Odylytics Brand System, owned by the team | Used on slides and documents as "Powered by Odylytics" |
| Layout reference | Movora template (Framer Marketplace) via Movago `DESIGN.md` | Grid, spacing and shapes only; no images, logos or text |
| Fonts | Sora, Manrope, JetBrains Mono (SIL OFL, Google Fonts) | |

Full list with how each was checked: `THIRD_PARTY_NOTICES.md`.

### AI tools
| Tool | Used for |
|---|---|
| Claude Code (Anthropic, Claude Sonnet 5.5) | Writing code, experiments, documents and paper review. Every reported number comes from code in `research/` that can be re-run |
| **TypeFormer** (Stragapede et al., MIT; pretrained on Aalto) with PyTorch | Research only, in `research/finetune/`: fine-tuned on StrokePIN and compared with LightGBM. **Not in the API.** Third-party code stays in `research/external/` and is not packaged |

### Papers
Not included in the package; DOIs are in `docs/research/paper-report.md`: Zheng 2014, Buschek 2015, Killourhy & Maxion 2009, Georgiev 2022 (FETA), Acien 2021, Fratantonio 2017, Lovisotto 2020, Wang 2026 (ActReal), Stragapede 2023 (TypeFormer).

## 6. Results (public real-human data, not team-collected)

| Test | Result |
|---|---|
| Owner check, StrokePIN, 97 people, PIN-knowing impostor, 3 enrollments, split by person | Baseline distance: EER 0.161, impostor passes 57.3% at 5% owner rejection. **Learned model: EER 0.158, 37.5%.** After a posture change (sit → walk): EER 0.309, 70.8% |
| Human vs bot (real humans, simulated bots) | Naive bots 100%; replay 12–26% for the classifier alone; population-sampling bots 20–73% |
| Replay check (threshold 0.07) | Catches 100% of replays with noise up to ±10%, 29% at ±15%, 0% from ±20%. Human false-positive rate about 0.1% at 8 past sessions |
| Innate Challenge (2,260 people typing sentences, timing only) | Impostor passes at 5% rejection: 81% (6 keys) → 49% (30 keys). Vietnamese phrases not yet measured on Vietnamese typists |
| Swipe rule (Touchalytics, 41 people) | "Uniform speed" rule flags 0 human strokes and catches 100% of uniform simulated swipes; swipe-based owner matching is near chance (AUC 0.48–0.60) and was dropped |
| Digraph normalization (Aalto, 1,000 people) | No meaningful gain (EER 0.249 → 0.238), not shipped |
| **Full system, 97 people, 5-fold by person (E29)** | With learned models: PIN-knowing impostor allowed 22% [20, 24], owner allowed 76% sitting and 49% walking, template-aware bot 72–87%. Rules only: impostor allowed 89% |
| Adaptive bots (E29) | Replay with ±15–30% noise passes 32–58%; template-aware bots 72–87% |
| **Fine-tuned TypeFormer** (Aalto → StrokePIN; 60 train, 7 validation, 30 unseen test people; 3 enrollments) | Before: EER 0.292, impostor passes 70.6%. **After: EER 0.203, 41.8%.** Sit → walk: EER 0.311, 66.1%. Single run and split, no confidence interval, not directly comparable with the 97-person rows, not in the API |
| Team-collected data | `TODO` |

Details and rerun instructions: [`docs/research/ai-research.md`](docs/research/ai-research.md) and `research/`.

## 7. Package layout

```
backend/   API, models, tests            attacker/   bot simulator (4 tactics, adb)
web/       website + demo wallet         sdk/        phone input SDK
research/  experiments and results       docs/       plans, explanations, research
tools/     builds the submission files
```

Excluded from the zip: `papers/` (copyrighted PDFs), `research/data/` and `research/external/` (third-party data and code), `.env*`, `*.db`, `.venv`, `__pycache__`.

## 8. Privacy and legal

Only timing, coordinates, event types and character counts are stored, never the PIN, amount or message text. Touch and typing data is treated as sensitive under Vietnam's Personal Data Protection Law 2025 and Decree 356/2025 (effective 1 Jan 2026); volunteers consented through the form in `docs/plan/thu-du-lieu-doi.md`. No third-party logo or brand name appears in the product; the demo UI is illustrative.
