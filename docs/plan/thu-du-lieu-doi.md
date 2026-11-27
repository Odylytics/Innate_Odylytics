# Team data collection plan (small group, 25/11/2026)

Goal: replace the "temporary" numbers (a model trained on public data and generated bots) with measurements under **the team's own conditions**: same device, the PIN and challenge sentences of the same person. This is the most valuable remaining task (see `ai-research.md`, E22).

## Scale and schedule
- **10–20 volunteers** (friends, acquaintances), each doing **2 sessions at least 1 day apart** (session 1 enrolls, session 2 tests across time exactly as in FETA). Finish collecting before 01/12 so the numbers make it into the slides; **after 03/12 the slides cannot be changed**.
- Each person uses **their own phone** (a keyboard they know), holding the phone as usual.
- Collection page `#/collect` (version of 25/11): it asks only for full name + email and a consent box, then a 10-digit keypad: **create your own 6-digit PIN** (stored, see below), 5 entries in total (later entries must match the first; wrong entries are not recorded); only after all 5 are done are the 5 sessions sent. It does not ask for sitting number or role. Original plan: 3 entries of PIN `1593` (enrollment), 5 entries of the test PIN, 5 random challenge sentences (`GET /v1/challenge`), and a few rounds where a second person (a PIN-knowing impostor) taps on that person's account.
- Bots: use `attacker/` (4 tactics) and `adb` on 1–2 real devices to get a bot set independent of the generator.

## Using the existing infrastructure
The backend already has the data-collection labels `meta` (`participant_id`, `sitting`, `role` genuine/impostor/bot, `tactic`, `note`) in `POST /v1/sessions` and `GET /v1/export` (ML key). Retraining: `research/experiments/train_human_model.py --export export.jsonl` (not yet tried on real data). The web demo must attach `meta` when collecting: `TODO` the web team confirms how to turn on collection mode.

## Data stored
Only **timing, coordinates, touch size, event type, character count, character class**. **Not stored:** phone numbers, transfer notes. **Deliberate exception (25/11):** the collection page stores the **PIN digits** that participants choose themselves (`pin_taps[].key`, which together give the PIN) for per-key / key-pair research; the page reminds participants twice (consent form + confirmation box) that this code must not match any real password or PIN. **From 25/11 the collection page writes full name + email straight into the `meta` of each session** (participants consent on the page); `participant_id` is a hash of the email. Therefore the `/v1/export` file contains personal data: do not put it in the repo or the submission zip; only the holder of the ML key may export.

## Consent form (template; the team adapts it and **asks someone with legal expertise to review it**)

> **CONSENT FORM FOR PARTICIPATING IN INTERACTION DATA COLLECTION**
> Team <TEAM NAME> collects touch and typing data for research for its entry in the MoMo Tech Contest 2026.
> 1. **Data collected:** the time and position of touches, touch area size, the time and type of keys typed (the content of the PIN or of the sentence is not recorded), the kind of interaction. No images, voice, contacts, location, or messages are collected.
> 2. **Purpose:** to train and evaluate the team's bot-detection and account-owner-recognition models; to present aggregated figures in the contest entry.
> 3. **Storage and sharing:** data is tagged with an anonymous code and kept within the research group, **not** sold or shared with any third party; published figures are aggregated only. Raw data <is/is not> in the submission package (TODO: decide).
> 4. **Retention:** raw data will be deleted after <date> (proposed: after the final on 11/12/2026) if you ask, or when the purpose ends.
> 5. **Your rights:** you may decline or withdraw at any time, ask to see or delete your data, and contact <team email>.
> 6. Interaction data may be **sensitive data** under the 2025 Law on Personal Data Protection and its guiding documents; collection is based on your consent on this form.
>
> Full name: ____ · Date: ____ · Signature / confirmation: ____ · Participation code (filled in by the team): ____

## Running the analysis (one command)
```bash
# 1) export the data (ML key), page by page until the X-Next-Offset header is gone
curl -s -H "X-API-Key: $NHIP_ML_KEY" "https://nhip-api-taupe.vercel.app/v1/export?limit=500&offset=0" > page0.json   # repeat with the offset from X-Next-Offset, merge into export.jsonl
# 2) T1–T5 in one command, writes research/results/team_analysis.md
python research/experiments/team_analysis.py export.jsonl
# 3) retrain human/machine: --out is REQUIRED so the running model is not overwritten
python research/experiments/train_human_model.py --export export.jsonl --out /tmp/models --no-strokepin --no-generated
```
Try the pipeline with FAKE data before the real collection: `research/experiments/team_data_dryrun.py` (starts a local backend, sends sessions with `meta`, exports, runs the two steps above; **the printed numbers are fake**, only to catch pipeline bugs). The dry run of 25/11 caught one backend bug (`owner.score` overflow, see the commit) and two script bugs.

## Analysis after collection (code already exists)
- Owner recognition across time (session 1 vs 2): `research/experiments/e9_strokepin_owner.py` as the template, swapping the data source.
- Human/machine on real bots: `train_human_model.py`, keeping the `adb` bots as an independent test set.
- Calibrate the replay threshold (E5b), the `fusion.py` thresholds, the `owner.py` score mapping (d=2 → 0.5 is currently loose).
- Vietnamese sentences: check whether `vi_tone_late` and `vi_ime_coverage` are stable between the 2 sessions (see `innate-challenge-vi.md`).
- Report: FAR@FRR 5% with bootstrap confidence intervals by person; **state the small sample size clearly**, do not compare with figures published on thousands of people.
