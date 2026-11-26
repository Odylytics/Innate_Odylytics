# Third-party components, datasets and licences

> Checked on **2026-11-25** (by reading the pages, READMEs and package metadata named in each row). Not legal advice. The contest requires every existing asset, open-source library, AI tool and data source to be declared; keep this file and `docs/submission/README.submission.md` §5 in step.
> Licence of this repository: **CC BY-NC-SA 4.0** (`LICENSE`). Third-party components keep their own licences.

## 1. Datasets (research data is NOT shipped in the submission; only models derived from StrokePIN are)

| Dataset | Owner / citation | Licence found | Where we use it | Ships in the repo/zip? | Action |
|---|---|---|---|---|---|
| **StrokePIN** | Yao & Wang, IEEE TDSC 2026, DOI 10.1109/TDSC.2026.3667918 (Nankai University). https://github.com/Litraveler/StrokePIN | **CC BY-NC-SA 4.0**. Dataset README: non-commercial use free with attribution, derivatives under the same licence; **commercial use needs written authorisation** (jingyuyao@mail.nankai.edu.cn). It also states "Anonymization has been completed". (The IEEE DataPort page title says "Creative Commons Attribution": we follow the stricter README.) | E4b, E5b, E9, E10, E12, E23, E24; training of the shipped models (`human_lgbm.*`, `owner_lgbm.*`) and `population_prior.json` | **Derived models and prior: yes** (hence this repo is CC BY-NC-SA). Raw data: no (`research/data/` is git-ignored) | Cite; keep the licence; ask the owner before any commercial use |
| **Aalto typing37k** | Palin, Feit, Kim, Kristensson, Oulasvirta, MobileHCI 2019. https://userinterfaces.aalto.fi/typing37k/ | **No data licence stated.** The page and the paper say the code and dataset are made "openly available"; the page names the ERC funding and contact (Antti Oulasvirta). Only the capture software in `source_code.zip` has a licence (MIT). | E11, E12, E13, E21/E21b, E22 (typing rhythm of real typists, research only) | **No** (neither data nor derived models) | Cite the paper. Treat as "openly available for research"; **ask the authors in writing** if any derived data or model is ever redistributed. The experiments publish only aggregate tables |
| **Touchalytics** | Frank, Biedert, Ma, Martinovic, Song, IEEE TIFS 8(1), 2013. http://www.mariofrank.net/touchalytics/ | **No licence stated** on the page or in `readme_data.txt`; data offered for download; the page lists the 2013 paper as the corresponding publication and says not to test with the label columns of the feature files. | E19 (swipe rule and owner check). The swipe rule threshold (speed CV < 0.3) was chosen by looking at this data; no data or model is derived from it | **No** | Cite; contact the author if redistribution or a derived dataset is ever needed |
| **CMU DSL-StrongPassword** | Killourhy & Maxion, DSN 2009. https://www.cs.cmu.edu/~keystroke/ | **No licence stated**; the site asks users to cite the DSN-2009 paper | E1/E2 (few-shot proxy), research only | **No** | Cite |

## 2. Software libraries

Python (`backend/pyproject.toml`, `attacker/pyproject.toml`; licences from installed package metadata):

| Package | Licence | Note |
|---|---|---|
| FastAPI, SQLAlchemy, pydantic, pytest | MIT | |
| Uvicorn, Starlette, httpx | BSD-3-Clause | |
| **psycopg / psycopg-binary** | **LGPL-3.0-only** | Used unmodified as a dependency (Postgres driver); not copied into this repo. Keep it replaceable (do not vendor it) |
| LightGBM | MIT | optional extra `ml` |
| NumPy, scikit-learn, pandas | BSD-3-Clause (NumPy bundles BSD/0BSD/MIT/Zlib/CC0 parts) | `research/` only (scikit-learn, pandas) |

Web (`web/package.json`; licences from the npm registry):

| Package | Licence |
|---|---|
| React, React DOM, Lenis, Vite, Vitest, @vitejs/plugin-react, qrcode-generator | MIT |
| TypeScript | Apache-2.0 |
| @dicebear/core, @dicebear/notionists (dev dependencies, used to pre-render avatars) | MIT |
| Tailwind CSS (landing page only, per `web/README.md`) | MIT (`TODO: confirm it is still used; it is not in package.json`) |

Research-only code in `research/external/` (git-ignored, not shipped): **TypeFormer** (MIT, Stragapede et al.).

## 3. Design, fonts, images, sound

| Asset | Source | Licence | Note |
|---|---|---|---|
| Avatars (`web/public/avatars/*.svg`) | "Notionists" by Zoish, rendered with DiceBear | **CC0 1.0** (verified on https://www.dicebear.com/styles/notionists/) | No attribution required; credited anyway |
| Fonts Sora, Manrope, JetBrains Mono | Google Fonts, loaded from fonts.googleapis.com | SIL Open Font License 1.1 (per Google Fonts) | Sora has no Vietnamese glyphs; Manrope covers Vietnamese headings |
| Design system and frontend shell | **Movago web demo by team Odylytics** (one of this team's members), reused: `styles.css`, `ui.tsx`, `smooth.ts`, `sound.ts`, `Intro.tsx`, `StoryBar.tsx`, ... | Own work, earlier project | **Declared as a pre-existing asset** (see `web/README.md`). All Innate content, wallet, SDK, API client, pages and line art are new |
| Layout reference | Movora template (Framer Marketplace), via Movago's `DESIGN.md` | Third-party commercial template | Grid, spacing, shapes only; no Movora images, logos or text |
| Sound | Generated in the browser with the Web Audio API (`web/src/sound.ts`), no audio files | n/a | |
| MoMo | No MoMo logo, name or UI is used | n/a | Contest rule |

## 4. AI tools

| Tool | Use |
|---|---|
| Claude Code (Anthropic), model Claude Sonnet 5.5 | Code, experiments, documents, paper review. Every reported number is produced by code in `research/` and can be re-run |
| Claude (Anthropic) web search and the claude.ai Artifact feature | Related-work search; two private helper pages (statistics chart, phone keyboard probe) |

## 5. Papers

`papers/` (52 PDFs) is the team's reading list for the experiments. They are the property of their publishers: **not part of the submission zip** (listed with DOIs in `docs/research/paper-report.md`).
