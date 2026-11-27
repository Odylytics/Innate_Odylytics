# Innate — AI Research

> 24/11/2026. Scope: the AI core behind Innate. The web/demo is built later by the team and is not covered in this document.
> Background: [`paper-report.md`](paper-report.md), [`notes/`](notes/), [`tech-notes.md`](tech-notes.md). Confidence is marked per claim: **[paper]** read in the team's PDF, **[search]** only seen as a search-result summary, **[inference]** my own idea, not yet verified by anyone.

## 1. The AI problem

From one session of interaction (PIN taps, swipes, screen rhythm), plus the transaction context, return a decision `allow | step_up | hold` with reasons. Three sub-problems:

| Problem | Input | Output | Training data available |
|---|---|---|---|
| **A. Human or bot** | One session | P(human) | Human sessions + generated bot sessions |
| **B. Is it the owner** | One session + 3–5 enrollment sessions of the owner | Match score | Owner sessions only (few-shot), population data optional |
| **C. Fusion + explanation** | A, B, new recipient, amount | Risk + reasons | Few or no fraud labels |

## 2. Current state of the code (backend/app/scoring)

| Problem | What it does now | Weaknesses seen when reading the code |
|---|---|---|
| A | Rules: timing CV, taps exactly on center, straight swipes; takes the **max** of the suspicion signals | Does not learn; any bot that gets under one threshold gets through; tactic 3 caught 0%, tactic 4 caught 5–30% (synthetic humans) |
| B | Template + scaled Manhattan; fixed σ floor; mapping `1/(1+e^{2(d−2)})` | σ estimated from 3–5 samples is very noisy; the mapping is uncalibrated and therefore too lenient |
| C | Weighted sum 0.40/0.35/0.15/0.10; thresholds 0.25/0.55 | Weights chosen by hand, no data yet to check them |

## 3. Research results per component

### A. Human or bot

- **Precedent:** BeCAPTCHA uses touch + accelerometer for one drag-and-drop gesture; the multimodal system doubles effectiveness in "agnostic" mode (unseen bots) and keeps the bot detection rate above 90% when trained on diverse bots [paper]. Training on only one kind of bot and then meeting another drops sharply [paper].
- **Design consequence:** evaluate with **leave-one-tactic-out** (train on 3 tactics, test on the remaining one), and never test on the same generator as the training set [inference, based on BeCAPTCHA's agnostic result].
- **Proposed additional signals** (all [inference], need measuring): timing quantization (injected events are often round to the millisecond, uniform), number of points between down and up, coordinate jitter while held, variation in `w`/`h`, noise entropy. An industry blog also argues that bots lack the "randomness and fluidity" of real touch [search, Radware].
- **Model:** start with Random Forest or LightGBM on ~40 features (precedent in BeCAPTCHA-Type [paper]). Data is small, so **prefer simple models with few parameters**: one small study reports that statistical algorithms beat deep learning when data is small [search]. Add **one-class** (trained on humans only) to catch unseen bots [inference].
- **Known limit:** ActReal (2026, preprint) shows that a system-level agent generating touch + IMU with matching timing succeeds 71–77% of the time [paper]. Layer A is strongest against naive bots; this must be stated plainly.
- **Replay detection (tactic 3):** no learning needed. Measure the distance to past sessions **of the same owner**; a real person does not repeat the rhythm to within ±5% [inference]. The threshold comes from the distribution of distances between real sessions of the same person.

### B. Is it the owner (few-shot)

| Approach | Data needed | Evidence | Decision |
|---|---|---|---|
| Scaled Manhattan (in use) | 3–5 samples | Best of 14 detectors, EER ~9.6% on computer keystroke data [paper] | **Keep as baseline** |
| Mahalanobis + **covariance shrinkage** | 3–5 samples | With few samples relative to the number of dimensions, the MLE estimate is poor; shrinking toward the diagonal is the common remedy, with the parameter chosen by cross-validation [search, a swipe study] | **Try it**; compare against Manhattan |
| Shrinkage toward the **population mean/variance** (empirical Bayes) | 3–5 samples + a population set | We did not find a source applying exactly this to few-shot keystroke [search, gap] | **The team's main idea to try** [inference]; could be a small novel contribution |
| Siamese/triplet (TypeNet) | Tens of thousands of people | EER 9.2% on touchscreen keyboards, free text, >100k people [paper]; the original plan states 10.7% (1 entry) → 7.3% (5 entries), a figure I have not re-checked against the PDF | **Not feasible** with ~25 people; only a small pairwise model if time remains |
| Transformer (Stragapede) | Large Aalto data | EER 3.84% with 5 enrollment sessions on Aalto [paper] | Not applicable; record as a reference ceiling |
| Per-person synthetic data (UserBoost) | A few real samples | Reduces the number of real samples needed for enrollment; but the study is on smartwatch gestures, not touchscreens [search] | A later idea; not a priority |

**Realistic expectation** (from Buschek and FETA [paper]): enrolling in the same sitting gives results twice as optimistic; rigorous evaluation raises EER from 4.9% to 13.8%. With ~25 people and 3–5 entries, a reasonable goal is **EER 10–15%**, reported with confidence intervals.

**Score calibration:** replace the fixed logistic mapping with a mapping learned from data (Platt or isotonic on the distribution of owner-vs-stranger distances) [inference]. Report at the operating point FAR@FRR 5% following ISO/IEC 19795-1 [paper, via notes].

**Safety of the template itself:** automatic updates can be poisoned (Biggio 2012; Lovisotto 2020: >70% success with <10 injections, and the detector catches >99% after 2 injections) [paper]. Keep a cap on drift and add a drift-direction check.

### C. Fusion and explanation

- A weighted sum after normalization (z-score/tanh) is the standard method; tanh handles outliers best [paper, Jain 2005 via notes]. Freeman 2016 (LinkedIn): combining signals with learned weights raises AUC 0.913 → 0.955 [paper].
- When there are **no fraud labels yet**, keep the hand weights but choose thresholds by FRR 5%. Once labels arrive from the dashboard, replace them with logistic regression under monotonicity constraints [inference].
- Explanation: each `w·x` term is already the exact contribution, so SHAP is not needed. For the LightGBM in problem A, use TreeSHAP (exact, polynomial time) to pull out the 2–3 most deviating features [paper].

## 3b. Signals beyond the PIN: amount, recipient, transfer note

A transaction has more input places than the PIN. Each is a source of signal, and each has different technical constraints. **Code skeleton already in place (24/11):** `SessionIn.fields`, features in `features.py`/`bot_features.py`, the rule `text_set_without_keys` in `human.py`, the collection SDK in `wallet.html`, 3 tests. **No experiment on input-field data has been run** and there are no real sessions yet; this needs R9 in [`research-plan.md`](research-plan.md). Data contract: [`backend/README.md`](../../backend/README.md).

| Input field | Signal | Who enters it, with what | Known constraint | Data/model to try |
|---|---|---|---|---|
| **Amount** | Typing rhythm of each digit; if the app draws its own number pad, also touch coordinates as with the PIN | Human: types each key. Bot: types keys, or sets the text directly | The amount field often uses a self-drawn number pad: then there is as much information as for the PIN | Same method as E1/E2/E9 |
| **Recipient account number/phone number** | As above; **paste** vs typing; error corrections | Human: types, or pastes from contacts/messages. Bot: fills in directly | System keyboard: only the time between keystrokes, **no coordinates** | StrokePIN does not have it; must be collected |
| **Name/transfer note (free Vietnamese text)** | Free-text typing rhythm: long strings, so many more signals than the PIN | Human: types; bot: often sets the text directly or types very evenly | System keyboard on the web: `keydown` often returns `keyCode` 229, not enough to know the key and no reliable release time; native has `TextWatcher` (text change timing) | **Exactly the domain of the Aalto data (free typing on phones) and the TypeFormer model (MIT, weights available)**; see below |

**Consequences for model choice:**
- **TypeFormer fits free-text fields** (transfer note, name), not the PIN. It learns long typing sequences on phone keyboards and produces embeddings for owner verification. For a 6-key PIN, statistics (E2/E9) still fit better. Proposal: E8 moves to free-text fields: compare TypeFormer with the statistical baseline on Aalto data (link already available, see `datasets.md`), then on the team's collected data.
- **The strongest human/bot signal may be here:** the Accessibility service has an API to set text directly into a field (`ACTION_SET_TEXT`) **without emitting key events**, so the text "appears" with no typing rhythm. I have not verified which method specific malware (RedHook, Gigabud...) uses, and this needs measuring on a real device (R9).
- **A session with several fields gives more signal than a single PIN,** so the "owner" score (the biggest weakness in E9) may be improved by pooling several sources: expected but **not yet measured**.

**Privacy (more important for text fields):** the transfer note and name are personal data. Keep the PIN principle: **store only timing and the raw character class** (letter, digit, whitespace, punctuation), never the content. If a model needs key codes, use only coarsely hashed codes or character classes. State this in the consent form (R7), because the 2025 Personal Data Protection Law (Luật BVDLCN 2025) treats biometrics as sensitive.

**Platform constraint to state honestly:** on mobile web the system keyboard sits outside the page, so the SDK sees no touch coordinates on it; only a self-drawn keyboard (like the PIN pad) gives coordinates. A native SDK also cannot read touch coordinates on the system keyboard. This is why the app should draw its own number pad for the amount if possible.

## 4. Proposed AI architecture (v1)

```
session ──► features (~40) ──┬─► A1: RF/LightGBM  (human vs bot, multi-tactic training)
                             ├─► A2: one-class    (humans only; catches unseen bots)
                             ├─► A3: replay       (distance to the owner's past sessions)
                             └─► B : shrunk Mahalanobis + Manhattan, calibrated on the population
A1,A2,A3 ─► human_score   B ─► owner_match
human_score, owner_match, new recipient, amount ─► fusion (normalization + weights) ─► allow / step_up / hold
                                                   └─► reasons (z-score / TreeSHAP) → Vietnamese sentence
```

## 5. Data

| Source | Used for | Access | To do |
|---|---|---|---|
| **Data the team collects itself** (~25 people × ≥2 sittings, one device) | Problem B and the final evaluation | Self-collected, with consent form | Draft the form (R7); this is the main source |
| **HuMIdb** (600 people, 14 sensors, BeCAPTCHA bot benchmark) | Problem A | Requires signing a license agreement and emailing the authors, then receiving a download account; ~5 GB [search, a GitHub mirror, needs confirming on the original BiDAlab page] | **Send the request early** because there is a waiting time |
| **Aalto typing37k** (37,370 people) | Estimating population variance for shrinkage; preliminary check of timing features | Data downloadable from the project page [paper, notes] | Check the license and size |
| BB-MAS, BehavePassDB, MobileTouchDB, FETA | Secondary comparison | License **not checked** | Check before use, record in the README |

Note: public data is not PINs on the team's self-drawn keyboard, so use it only to estimate the population distribution and for preliminary checks, not as a replacement for the team's data.

## 6. Experiment plan

| # | Hypothesis | Procedure | Metric | Real data needed? |
|---|---|---|---|---|
| E1 | Shrunk Mahalanobis ≥ scaled Manhattan with only 3–5 samples (**proxy run: no, it is worse**; not yet repeated on StrokePIN) | Same data split; compare by number of enrollment entries 1/3/5 | EER, FAR@FRR 5% + confidence intervals | Yes |
| E2 | Shrinkage toward the population beats a fixed σ floor (**run on DSL and StrokePIN; the deployable version = timing only, now in `owner.py`: FAR@FRR 5% 0.66 → 0.50, E10b**) | Estimate the prior from Aalto/team data; compare with the current floor | As E1 | Yes (Aalto for the prior) |
| E3 | Calibration (Platt/isotonic) lowers FAR at the same FRR | Fit on sitting 1, test on sitting 2 | FAR@FRR 5%, DET curve | Yes |
| E4 | RF/LightGBM beats the rules in problem A and **still catches unseen bots** (**run: E4 synthetic humans too optimistic; E4b real humans: catches 100% of naive bots, tactic 3 26%, tactic 4 20–73%, unseen bots weak**) | Leave-one-tactic-out over 4 tactics + `adb` as a separate test set | Catch rate per tactic | Needs real human sessions |
| E5 | The replay check catches tactic 3 without rejecting the real owner (**run: catches 100% at ±5–10% noise, loses from ±20%**) | Threshold from the distribution of distances between real sessions of the same person | Tactic 3 catch rate, added FRR | Yes |
| E6 | New signals (timing quantization, coordinate jitter) separate bots from humans | Add one feature group at a time, measure the improvement | Importance, ΔAUC/ΔFAR | Yes, together with `adb` data |
| E7 | Anti-poisoning: drift cap + drift-direction check blocks the "gradual teaching" sequence (**run: the cap bounds it but does not eliminate it; recommend freeze + flag**) | Simulate a sequence of bot sessions sitting just above the update threshold | Template drift after n updates | No (simulation) |

**Evaluation rules** (FETA [paper]): split by time, one phone, no impostor data in problem B training, leave-users-out if there is a pairwise model, report the error distribution per person (Eberz 2017).

## 6b. Experiment results already run (24/11)

**E1/E2 proxy version** on CMU DSL-StrongPassword (desktop keyboard, fixed password, 51 people, 31 timing features): enroll with k random samples from session 1, test on sessions 5–8, 10 sample draws per person, bootstrap confidence intervals by person, population prior taken only from **the other people**. Code: `research/experiments/e1_fewshot_owner.py`, full table: `research/results/e1_dsl.md`.

| k enrollment samples | Baseline EER (scaled Manhattan) | E2 change in EER (ν=5) | E2 change in FAR@FRR 5% (ν=5) |
|---|---|---|---|
| 3 | 0.211 | −0.011 [−0.022, +0.001] | **−0.112 [−0.153, −0.071]** |
| 5 | 0.198 | +0.000 [−0.010, +0.011] | **−0.087 [−0.122, −0.051]** |
| 10 | 0.194 | +0.001 [−0.006, +0.010] | **−0.066 [−0.097, −0.036]** |

Reading the results:
- **Shrinking the variance toward the population (E2) lowers FAR at the FRR 5% operating point** (about 7–11 percentage points, the paired confidence interval does not contain 0), strongest when there are only 3 samples. **EER is almost unchanged**. That means the improvement is in the tail (accepting few rejected owners), exactly the operating point Innate chooses.
- **Mahalanobis shrunk toward the diagonal (E1) is worse** than baseline at all three levels of k (EER 0.21–0.25 versus 0.19–0.21).
- **The current σ floor in `owner.py` is almost no different from baseline**, so it is not helping in the few-shot setting.
- EER ~0.20 is higher than the 9.6% of Killourhy & Maxion because they trained with 200 samples while here there are only 3–10 samples and testing is on later sessions. The numbers are not directly comparable.

**Limit to state honestly:** the data is a desktop keyboard, one fixed password, no touch position. This is evidence for the **method** (shrinkage toward the population helps when samples are few), not yet for Innate's own numbers. It needs repeating on the team's PIN data. E5 and E7 were run later, see below.

### E5 — replay detection (run, SYNTHETIC data)

Code: `research/experiments/e5_replay.py`; table: `research/results/e5_replay.md`. Installed in the backend: `app/scoring/replay.py` (wired into `/score`; a session judged to be a replay gets `human_score` ≤ 0.1, reason `replayed_session`, action `hold`), 1 new test.

- The attacker is **adaptive**: adds noise to both timing (±n) and coordinates (±max(2, 40n) px). The threshold is chosen so that only ~1% of real human sessions are mistaken for replays.
- The distance currently used: key hold/key gap times (relative) **plus center offset dx/dy**. The timing-only version is clearly weaker at high noise.

| Attacker noise level | ±5% (as in tactic 3) | ±10% | ±15% | ±20% | ±30% |
|---|---|---|---|---|---|
| Caught, 4-digit PIN | 1.00 | 1.00 | 0.59 | 0.07 | 0.00 |
| Caught, 6-digit PIN | 1.00 | 1.00 | 0.99 | 0.36 | 0.00 |

- **The original tactic 3 (±5%) is fully caught**; the replay check works well up to ±10–15% noise. From ±20–30% upward the attacker wins, because the replayed session then varies as much as a real person. This is a race, not a final answer.
- **A flaw found through the experiment:** a 4-digit PIN has only 7 timing features, so two real sessions can be close by chance; when compared against 200 past sessions, the rate of wrongly rejecting the owner rises to **7.5%** (6-digit PIN: 0%). The backend has cut the number of sessions compared to **50** (4-digit PIN then 3.3%). The demo wallet uses a 6-digit PIN. If a partner uses a 4-digit PIN, raise the threshold or reduce the number of sessions compared further.
- **Limit:** the personas are synthetic (the variation between sessions was set by me/the team), so the threshold of 0.085 **must be recalibrated on real human data**. It only compares against past sessions **of the same account**; replaying a session that was never sent to the server is not caught by this check.

### E5b — calibrating the replay check on real people (24/11)

Code: `research/experiments/e5b_replay_real.py`; table: `research/results/e5b_replay_real.md`. Real StrokePIN people (1,842 person-PIN pairs, 4–10 entries of the same PIN, both sitting and walking), using the backend's own `replay.distance`; the adaptive replay adds timing noise ±n and coordinate noise ±max(0.02, 0.4n) key widths.

- **The threshold of 0.085 (chosen on synthetic humans in E5) gives a real-human FPR of 0.28% → 0.40% → 0.64% when compared against 3 → 5 → 8 past sessions**: it grows almost linearly with the number of sessions. Linear extrapolation to 50 sessions (the backend compares up to 50) gives **~3.7%**: this could not be measured because the data has only ~9 entries per pair, so it is a guess. Since a replay is sent straight to `hold`, this level is too costly.
- Real-human distance percentiles: 0.1% = 0.071; 1% = 0.094; median 0.189. Median distance of replayed sessions: ±5% → 0.025; ±10% → 0.050; ±15% → 0.075; ±20% → 0.101.
- **The default threshold was changed to 0.07** (FPR ~0.1% at 8 sessions, ~0.7% extrapolated at 50). The price: it catches 100% of replays with noise up to ±10% but only **29% at ±15%** (old threshold: 86%) and 0% from ±20%. An adaptive attacker adding noise ≥15% still gets past this check; the session then looks like a different person and only the (weak) "owner" score stands in the way.
- **Limit:** the history in the data is short (~9 entries, one collection round), so the effect of many past sessions must be re-measured with the team's data (long histories, many days). The real people here typed a PIN assigned by the researchers, not their own memorized PIN, so they may be less or more regular than real users.

### E11 — human/bot on free-text fields, real Aalto people (24/11)

Code: `research/experiments/aalto_note_extract.py` (extracts typing rhythm from the mysqldump, **keeps only timing, event type and character class, never content**), `e11_text_field_bots.py`; bots: `attacker/nhip_attacker/fields.py` (`generate(..., with_fields=True)`); table: `research/results/e11_text_field_bots.md`. Humans: **33,522 real typed sentences from 2,260 people**, split by person. Bots only in the `note` field (Aalto has no amount/recipient field), 4 tactics: (1) set the text directly like `ACTION_SET_TEXT`, (2) even typing via an automation tool, (3) replay the rhythm of a real person, (4) sample distances from the population.

Real typing rhythm (for calibration): median gap between keys 223 ms (5–95th percentile: 84–1394 ms), the variation within a sentence has a median of **0.92** (very uneven), median deletion rate 3.4%, 63% of sentences have no prediction/paste events.

Share of bots caught at FRR 5% (LightGBM, the `fld_*` features currently in the backend; in parentheses: with extended features added):

| | T1 set text directly | T2 even typing | T3 replay | T4 population sampling |
|---|---|---|---|---|
| Bot type seen | **1.00** | **0.99** | 0.06 | 0.31 (0.58) |
| **Never seen** | 1.00 | **0.00** (AUC 0.20) | 0.05 | 0.04 |
| IsolationForest (humans only) | 0.00 | 0.00 | 0.05 | 0.01 |
| Current backend rules | 0.00 | 0.00 | 0.00 | 0.00 |

Reading the results:
- **The two naive bots (set text directly, even typing) are caught ~100% once the model has seen them**, because real human rhythm is very uneven (CV 0.92 versus 0.35 for the even-typing bot).
- **Unseen bots are the weak point:** leaving tactic 2 out of training catches **0%** (AUC 0.20: worse than random guessing; the even-typing bot looks "more human than humans" to a model trained on other bots). This is the same lesson as E4/E4b: a supervised model is only good against the bot families it has seen. IsolationForest (learns from humans only) **does not rescue it** at the FRR 5% threshold (catches 0% of the two naive bots, despite an AUC of 0.71–0.85).
- **Human-like bots cannot be caught by rhythm:** replay (T3) 6%, as predicted (that rhythm belongs to a real person). Population sampling (T4) 31%; **extended features (distance percentiles, successive deviation, standard deviation) raise it to 58% (AUC 0.85 → 0.93)**: the existing `fld_*` set lacks rhythm statistics. They were not added to `bot_features.py` because the deployed model was not trained on data with input fields.
- **That the current backend rules catch 0% on the note field is intentional:** a note field set without keystrokes is only penalized lightly (autofill, voice typing and paste are all legitimate). E11 does not evaluate the amount field (no real human data), so the rule "`set_text` on the amount field = machine" is **still unvalidated**.

**Limits, and the points where the figures are optimistic:**
1. I kept only real sentences with ≥ 15 keys, so people who entered text by voice, paste or autofill are **excluded in advance**. Separating "set text directly" from real humans (T1) is therefore easier than in reality. In real life, many people fill in the note field without any keystrokes.
2. The Aalto data is **copying English sample sentences** on phones (a typing speed test), unlike **composing** Vietnamese transfer content; composing rhythm has more thinking pauses.
3. The bots still come from a generator, one single field, no real bots yet.

### E12 / E12b — LEARNED owner verification model (task A, 24/11)

Code: `research/experiments/e12_learned_owner.py` (`--no-contact` for E12b), `train_owner_model.py`; tables: `research/results/e12_learned_owner.md`, `e12b_learned_owner_no_contact.md`. StrokePIN, split by **person** (58 train / 39 test, 3 splits), enrollment of 3 sitting entries, PIN-knowing impostor, prior from training people only. Replaces `mean(|z|)` (all features equal) with a classifier learned on the |z| vector.

| | Same posture: EER | Same posture: FAR@FRR5% | Posture change: EER | Posture change: FAR@FRR5% |
|---|---|---|---|---|
| E12 (with contact size) baseline | 0.149 | 0.558 | 0.354 | 0.943 |
| E12 LightGBM | 0.108 | 0.200 | 0.264 | 0.675 |
| **E12b (contact size removed)** baseline | 0.161 | 0.573 | 0.363 | 0.944 |
| E12b logistic regression | 0.206 (**+0.045, worse**) | 0.510 (confidence interval contains 0) | 0.319 | 0.737 |
| **E12b LightGBM** | 0.158 (−0.003, not significant) | **0.375 (−0.198 [−0.363, −0.085])** | **0.309 (−0.053 [−0.078, −0.033])** | **0.708 (−0.236)** |

Reading the results:
- **E12 looks good because of device noise:** the largest weights the regression learned are `tap_w_mean` and `tap_h_mean` (contact area size = different phones across people). The impostors in StrokePIN use *their own* phone; in a real scenario B the impostor holds the victim's actual phone, so this effect disappears. **The trustworthy number is E12b** (contact size removed), not E12.
- **E12b: the learned LightGBM still helps for real**, mainly at the FRR 5% operating point (impostor passes 0.573 → 0.375) and under posture change; **same-posture EER does not improve**. Logistic regression (linear weights) is **not** better than the old distance in EER.
- **Wired into the backend** (`app/scoring/owner_model.py`, `app/models/owner_lgbm.*`, optional; if a library or file is missing, or the PIN is not 6 keys, the old distance score is used; `NHIP_OWNER_MODEL=off` to turn it off). The score is mapped so the FRR 5% threshold = 0.5. On 29 held-out people: FRR 5.0% same posture, impostor passes 0.359; **after a posture change the owner is rejected 22.1%**.
- **Limit:** trained on 97 public people, each with one phone (device noise remains in the center offset due to normalizing by the estimated key size), 6-digit PIN assigned by the researchers, one collection round. The model is **temporary**; it must be retrained with the team's data.

### E13 — "Innate Challenge": are more keystrokes better? (24/11)

Code: `research/experiments/e13_length_effect.py`; table: `research/results/e13_length_effect.md`; design: [`../plan/innate-challenge.md`](../plan/innate-challenge.md). Real people typing sentences on phones (Aalto, timing only), truncated to the first n keys, **the test sentence differs in content from the enrollment sentence**.

| Number of keys n | Owner check: EER | FAR@FRR5% | Catching even-typing bot (AUC) | Catching population-sampling bot (AUC) |
|---|---|---|---|---|
| 6 | 0.364 | 0.807 | 0.915 | 0.719 |
| 10 | 0.337 | 0.733 | 0.969 | 0.764 |
| 20 | 0.279 | 0.591 | 0.996 | 0.848 |
| 30 | 0.245 | 0.489 | 0.995 | 0.891 |

More keystrokes clearly improve both the owner check and bot detection, and the confidence intervals do not overlap. **But the absolute numbers are still weak** (EER 24.5% at 30 keys with 6 rhythm features and 3 enrollment sentences); **it cannot be compared with the PIN** (Aalto has no key hold time or coordinates); people **copy English sample sentences**, rather than typing a random letter-digit string under stress; the bots are synthetic; PIN + sentence pooling has not been measured, and neither has friction.

### Task B — retraining with the team's data (pipeline ready, 24/11)

`research/experiments/train_human_model.py --export export.jsonl [--no-strokepin] [--no-generated]` takes the output of `GET /v1/export` (role `genuine`/`impostor` = humans, role `bot` = **real** bots), splits people by `participant_id`, sets the FRR 5% threshold on validation people, and reports real-bot catch rate on the test set. The default (no flags) gives a **byte-for-byte identical model** to the deployed one. The `--export` branch was tried on **simulated** team data: it runs correctly (results on synthetic data are meaningless). **The real training could not be done because the team has no data yet.**

### E7 — poisoning the template (run, SYNTHETIC data)

Code: `research/experiments/e7_poisoning.py`; table: `research/results/e7_poisoning.md`. **`owner.py` has not been changed**; this is a recommendation for the team to decide.

A strong attacker (can create arbitrary feature vectors) sends, at each step, a session just above the update threshold (owner ≥ 0.8). 100 owner/impostor pairs.

| Defense | Impostor accepted after injection (n=0 is 0.56) | Owner accepted after injection | Owner drifts +50% (count ≥ 0.8) |
|---|---|---|---|
| No cap | **1.00** (from n=25) | **0.58** (owner locked out) | 1.00 |
| Cap 1 sd/feature (**current**) | 0.85 | 1.00 | 0.67 |
| Cap 0.5 sd | 0.75 | 1.00 | 0.41 |
| Cap 0.25 sd | 0.67 | 1.00 | 0.28 |
| Freeze when mean drift > 0.5 sd (with flag) | 0.77 | 1.00 | 0.68 |

Reading the results:
- **No cap is a disaster:** the impostor is accepted 100% and the real owner is locked out (0.58). Having a cap in `owner.py` is necessary and correct.
- **The cap bounds the damage but does not eliminate it:** the template is pulled to the cap very quickly (~10 injections) and then stops. With the current cap, the impostor is accepted 0.85 versus 0.56 at the start.
- **Freezing on directional drift** beats the 1 sd cap: impostor 0.77 (lower than 0.85) at an equal cost for an owner who drifts strongly (0.68 versus 0.67), and it also raises a **warning flag** for operations. Tighter caps (0.5; 0.25 sd) reduce the impostor but cause strongly drifting owners to be rejected more (0.41; 0.28). **Recommendation:** switch to "freeze + flag", and require re-enrollment once frozen.
- **A finding more important than E7 itself:** right before poisoning (n=0), **56% of the impostor's real sessions were already accepted** (owner ≥ 0.5) on the synthetic personas. This is a consequence of the overly lenient score mapping `d=2 → 0.5` in `owner.py`, noted in section 2. Calibration (E3) has higher priority than choosing the anti-poisoning method.
- **Limit:** one attack strategy, synthetic personas, 100 pairs, no confidence intervals; the "owner drifts" scenario only changes timing. The cost of the cap shows only at the 0.8 threshold; at the 0.5 threshold every defense is ~1.00 because the 0.5 threshold is too lenient.

### E4 — LightGBM for the human/bot problem (run, SYNTHETIC data)

Code: `research/experiments/e4_human_bot_lgbm.py`; features: `backend/app/scoring/bot_features.py` (fixed-length vector, ~30 features, NaN if missing); table: `research/results/e4_human_bot_lgbm.md`; the model trained on synthetic data is stored in `research/models/` (**not for use in the submission**, and not yet wired into the backend). The threshold is chosen on humans in the validation set so that FRR = 5%, 3 independent data generations.

Share of bots caught (real FRR ~5%):

| Model | T1 | T2 | T3 | T4 |
|---|---|---|---|---|
| Baseline rules (`human.py`) | 1.00 | 1.00 | 0.04 | 0.01 |
| LightGBM, **saw all 4 tactics** in training | 1.00 | 1.00 | 0.85 | 0.97 |
| LightGBM, **that exact tactic left out** of training | **0.00** | 1.00 | 0.07 | 0.23 |
| IsolationForest (trained on humans only), unseen tactic | 1.00 | 1.00 | 0.12 | 0.47 |
| Ensemble (LightGBM or IsolationForest), unseen tactic | 1.00 | 1.00 | 0.11 | 0.41 |

Reading the results:
- **When the model has seen the bot type**, LightGBM is far better than the baseline rules (tactic 3: 0.85 versus 0.04; tactic 4: 0.97 versus 0.01). This nice number mostly reflects the fact that it learned the **fingerprints of the data generator**, so it is not for slides.
- **Against unseen bots LightGBM collapses**: leaving tactic 1 out of training catches **0%** (AUC 0.50) even though it is the most naive bot. I checked: it is a **shortcut**. In the synthetic data, humans always have a constant swipe time step (`swipe_dt_cv = 0`), while tactic 2 has noise so `swipe_dt_cv > 0`; the tree picks exactly that condition to separate tactic 2 completely. Tactic 1 also has `swipe_dt_cv = 0`, so it is ranked as human (P(human) = a constant 0.971). This is a real risk with real data: script-generated bots differ from humans in trivial details, the model learns those details and does not generalize.
- **IsolationForest (learns from humans only) generalizes better to unseen bots** (tactics 1, 2: 100% even though never seen; tactic 4: 38–47%, varying between runs because IsolationForest is random; the rerun after adding input-field features gave 0.47 instead of 0.38). So it is kept in the ensemble. The ensemble is essentially equal to the better of the two models in each case.
- **Tactics 3, 4 (human-like bots) remain hard against unseen bots**: 11–41% caught. Tactic 3 should be handed to the replay check (E5), not to the classifier.
- Removing the contact-size group (`tap_w/h`) barely changes the results on synthetic data; this group still needs verifying on real devices (R2).
- The most important features: `swipe_v_peak_ratio`, `swipe_lateral_dev`, `dy_std`, `tap_w_std`, `dx_std`. Most are swipe/center-offset features determined by the generator, so they need re-examining against real data.
**Consequence:** the human/bot problem needs **many different bot families produced by real tools** (`adb`, a `dispatchGesture` app, at least a few kinds), and real humans. Only then does a "leave one bot family out" evaluation mean anything.

### E4b — human/bot with REAL PEOPLE (run; real humans, bots still synthetic)

Code: `research/experiments/e4b_human_bot_real.py`; table: `research/results/e4b_human_bot_real.md`. Humans = real PIN sessions from StrokePIN, **split by person** (train 40 / val 12 / test 30 / attacker pool 15, no overlapping people, 3 splits). Bots = the group's 4 tactics, built on real PINs and the real human distribution; only the PIN part is compared (the bots' swipe/screen parts are dropped because StrokePIN has none). The FRR 5% threshold is chosen on humans in the validation set.

| Share of bots caught | T1 | T2 | T3 | T4 | Real FRR |
|---|---|---|---|---|---|
| Baseline rules (`human.py`) | 1.00 | 1.00 | 0.05 | 0.01 | 0.058 |
| LightGBM, saw all 4 tactics | 1.00 | 1.00 | **0.26** | **0.73** | 0.059 |
| LightGBM, **that exact tactic left out** | 1.00 | 0.56 | 0.09 | 0.20 | 0.059 |
| IsolationForest (humans only), with contact size | 1.00 | 0.86 | 0.07 | 0.03 | 0.046 |
| IsolationForest, **without** contact size | **0.33** | **0.31** | 0.07 | 0.03 | 0.056 |

Compared with E4 (synthetic humans):
- **The synthetic E4 was too optimistic.** Tactic 3: 0.85 → **0.26**; tactic 4: 0.97 → **0.73**. With real humans, human-like bots are much harder to catch.
- **The "0% collapse" seen in E4 disappears** (leaving out T1 still catches 100%): it was a shortcut caused by swipe details of the synthetic-human generator, as diagnosed. But **unseen bots are still hard**: leaving out T2 leaves 0.56, leaving out T3 leaves 0.09, leaving out T4 leaves 0.20.
- **IsolationForest separates naive bots only thanks to contact size:** without this group, tactics 1, 2 drop to 0.31–0.33. A bot using `w=h=1` is too easy to spot in synthetic data; a real bot can set any value, and the browser also returns 1 for real humans when the device cannot measure it (R2). This group must not be relied on.
- **The supervised LightGBM still catches tactics 1, 2 at 100% even without contact size** (thanks to even rhythm and exact-center taps), so this is the most solid part.
- **Real FRR of 5.8–6.4% versus the 5% target:** the test people use different devices than the validation people. The threshold needs calibrating per device.

**Consequences:**
1. The human/bot problem will reliably catch **naive bots** (tactics 1, 2; `adb`, scripts). This is the number that can be stated.
2. **Tactic 3 (replay) must be handed to the replay check (E5)**, not to the classifier: the classifier catches only 9–26%.
3. **Tactic 4 (sampling from the population) is caught only 20–73%** depending on whether it has been seen. State this plainly as a limit.
4. The bots are still **synthetic**: no real bots yet. Results on real bots could differ in either direction.

### E10 / E10b — shrinkage toward the population, deployable version, now in `owner.py` (24/11)

Code: `research/experiments/e10_deployable_prior.py` (compares variants), `e10b_backend_path.py` (checks the backend code itself), `make_population_prior.py` (generates the prior); tables: `research/results/e10_deployable_prior.md`, `e10b_backend_path.md`. Data: StrokePIN, real people, **leave-one-person-out** prior.

E9 used a prior specific to (PIN, posture), but at runtime the PIN is not known in advance. E10 tried a prior **shared across all PINs and both postures**:
- **Timing only:** the shared prior lowers FAR@FRR 5% by ~8–11 points, close to the per-PIN upper bound (−0.11).
- **Adding center offset: shrinkage for center offset makes it WORSE** (EER +0.04, FAR +0.06; even the per-PIN prior makes EER worse by +0.03). The variation in center offset differs too much between people and devices. **This is a correction to the E9 conclusion** (at that time I said E2 should apply to all features).
- **The hybrid variant wins:** shrinkage **for timing only**, keeping a floored sd for center offset.

**Applied to `owner.py`** (function `_sd`, `population_prior.json`, ν=5): only `pin_hold_i`, `pin_flight_i`, and `pin_total` (only when the PIN has exactly 6 keys); can be turned off with `NHIP_POP_PRIOR=off`.

E10b runs **`owner.build_template`/`owner.score` themselves** with all identity features as in the real backend, k=3:

| Test posture | Shrinkage | EER | FAR @ FRR 5% |
|---|---|---|---|
| Same (sitting) | off (old) | 0.153 | 0.663 |
| Same (sitting) | **on** | 0.146 | **0.495** |
| | paired difference | −0.007 [−0.011, −0.004] | **−0.167 [−0.190, −0.114]** |
| Changed (walking) | off / on | 0.352 / 0.355 | 0.943 / 0.943 |

Reading the results:
- A real improvement and **no EER trade-off** in the same posture: impostors getting through drop from 66% to 50% at FRR 5%.
- **It does not rescue the posture-change case** (0.943 unchanged). That problem needs enrollment across several postures, not shrinkage.
- A FAR of 50% is still very high: the "owner" score still cannot serve as a blocking gate.
- **Interaction with the new security fix (24/11):** `/enroll` now returns 409 once a template exists (this stops someone else injecting their own rhythm into an enrolled account). This **conflicts with the E9 recommendation to enroll across several postures**: a controlled re-enrollment path (e.g. after strong authentication) is needed, not yet designed.

**Limit:** the prior in `population_prior.json` is computed on **all 97 people** (the real build), so scoring it again on StrokePIN itself would leak; E10b uses leave-one-out to avoid that. The prior is a statistic derived from CC BY-NC-SA 4.0 data: state it in the README. Only tested on 6-digit PINs on phones in one collection round.

### Human/bot model wired into the backend (24/11, TEMPORARY)

- `backend/app/scoring/human_model.py` loads LightGBM (`backend/app/models/human_lgbm.txt` + `.json`); **optional**: if `lightgbm` is missing, the file is missing, or `NHIP_HUMAN_MODEL=off` is set, the baseline rules are used. Wired into `/score`: takes the more pessimistic score of the rules and the model (if the rules lack data, the model score is used); if the model raises a flag that the rules cannot explain, the reason `ml_bot_pattern` is added.
- The model score is mapped so that the FRR 5% threshold (on validation people) = 0.5.
- Training: `research/experiments/train_human_model.py` on **real StrokePIN humans + bots generated by `tactics.py`**, split by person, **without contact size**. This model is **temporary**: it is not the team's data, and there are no real bots yet.
- Results on 20 people **never seen**: FRR 3.3%; catches tactic 1: 100%, 2: 100%, 3: 12%, 4: 61% (consistent with E4b). The synthetic humans of `tests/synth.py` are not treated as machines (0/200), and a tactic 1 bot scores 0.0.
- **License:** the model is trained on StrokePIN (CC BY-NC-SA 4.0, derivatives shared under the same license). State it in the submission README.
- Installation: `pip install lightgbm` (the optional `ml` group in `pyproject.toml`); `uv.lock` has not been updated.

### Open weights available (verified on 24/11 through the GitHub API)

| Candidate | License | Weights? | Used for | Fits Innate? |
|---|---|---|---|---|
| **TypeFormer** (`gstrag/TypeFormer`) | **MIT** | **Yes**: `pretrained/TypeFormer_pretrained.pt` (14.8 MB) and `preliminary_transformer_pretrained.pt` (3.7 MB) | Problem B (owner verification via mobile typing embeddings) | Partly: see below |
| TypeNet, SwipeFormer, KVC, MobileTouchDB, HuMIdb (BiDAlab) | **No license** on the repo | **No**: the repo has only a README/figures, data is granted through an email agreement | | Cannot be used as weights |
| Model for problem A (human/bot) | | **No pretrained model found** | | Must be trained ourselves (LightGBM) |

TypeFormer details: trained on the Aalto mobile typing set; the input is a sequence of keys, each with 5 features (hold time, press-to-press, release-to-release, between keys, key code/255); the output is an embedding, verified by distance to the enrollment embeddings. A copy was cloned to `research/external/TypeFormer` (commit `8bf1342`, gitignored; code based on the old torch 1.13).

**Domain gap to check before "pulling it in for fine-tuning":**
1. TypeFormer learns **free-text typing** (long sequences, many keys); a 6-digit PIN has only 6 keys, very short.
2. Its input has **no touch position**, while Buschek 2015 shows that spatial features cut error by 26–37%. Throwing this information away may be counterproductive.
3. Fine-tuning needs **the team's real PIN data** (not available yet). With ~25 people the risk of overfitting is high; E2 already achieved an improvement with statistical shrinkage alone.
4. Disclosure: using these weights must be stated in the submission README (existing assets + paper citation), and the fact that Aalto is the training data source should be weighed.

**Proposed E8:** embed PIN sessions through TypeFormer (padding the sequence), compare with Manhattan + population shrinkage (E2) on the **same real PIN data** under the same evaluation procedure. Choose it only if it wins at FAR@FRR 5%. A first version could be tried zero-shot on DSL, but that is a desktop keyboard so it would only be a pipeline check.

### E9 — owner verification on REAL phone PINs (StrokePIN)

This is the first experiment on **real-human data, 6-digit PIN, with touch coordinates**, run with the backend's **own `features.py` and `owner.py`**. Data: StrokePIN (97 people, 17,895 valid entries, 20 shared PINs, sitting/walking; CC BY-NC-SA 4.0; see `datasets.md`). Code: `research/experiments/strokepin_loader.py`, `e9_strokepin_owner.py`; table: `research/results/e9_strokepin_owner.md`.

Setup: enroll with k=3 **sitting** entries; test the owner (same posture or changed to **walking**); the impostor **knows the PIN** (another person enters the same PIN); scores pooled over all (person, PIN) pairs; 95% bootstrap CI by person. Each pair has only ~5 sitting entries, so with k=5 there are no sitting entries left to test the same posture.

**Same posture (sitting), k=3, current backend (floored sd):**

| Feature set | EER | FAR @ FRR 5% |
|---|---|---|
| Timing | 0.201 [0.195, 0.208] | 0.697 |
| + center offset | 0.166 [0.158, 0.177] | 0.734 |
| + center offset + contact size | 0.158 [0.147, 0.167] | 0.718 |

**Posture change (sitting → walking), k=3:** EER 0.32–0.36, FAR@FRR 5% 0.84–0.94.

Reading the results:
- **The "owner" signal is real but weak with 3 enrollment entries:** EER 16–20% when the impostor knows the PIN. At the FRR 5% operating point, **FAR is still 57–73%**: most impostors get through. That means the "owner" score cannot serve as a blocking gate; this fits the `step_up` design and the pooling of bot and context signals. This figure is the first real measurement, so it replaces the 10–15% expectation derived from papers.
- **A posture change destroys nearly the whole signal** (EER 0.32–0.40, FAR@5% 0.75–0.94). Enrolling only while sitting and then entering the PIN while walking is nearly useless; center offset even makes it worse (0.32 → 0.36). Design consequence: enrollment must cover several postures/contexts, or the "owner" score must be down-weighted when a posture change is detected (motion sensors).
- **Center offset and contact size improve EER** (0.201 → 0.166 → 0.158), consistent with Buschek 2015. **But they do not yet improve FAR@FRR 5%** (0.70 → 0.73 → 0.72, wide CI).
- **The floored sd of `owner.py` is clearly better than plain scaled Manhattan** on real PINs (EER 0.158 versus 0.227 using all three feature groups). On DSL the two are about equal (E1/E2 proxy). The floor helps when there are only 3 samples and the PIN is short.
- **E2 (shrinking the variance toward the population) replicates on real data:** it lowers FAR@FRR 5% relative to the current backend, paired by person: timing −0.140 [−0.161, −0.107]; timing + center offset + size −0.159 [−0.198, −0.117]; EER nearly unchanged (−0.001 and +0.005). For the "timing + center offset" set alone, EER is **worse** by +0.031 [+0.026, +0.037]. The effect is consistent with DSL: the improvement is in the tail, not in EER.

**Important limits; the figures above are inflated in two ways:**
1. **Device differences between people.** There are 94 different key-size pairs across 97 people, so each person most likely uses their own phone. Center offset and contact size therefore carry **device** information as well. In a real scenario B, the impostor holds **the victim's actual phone**, so this difference disappears. Hence the improvement from center offset/size (0.201 → 0.158) is an upper bound; the number closer to reality is the "timing" row (EER ~0.20).
2. PINs were assigned by the researchers (20 shared PINs, many weak ones such as 111111, 123456), users did not type their own memorized PIN; each pair has only ~5 entries per posture, and enrollment and testing happen in the same collection round (no multi-day gap yet).

### E18–E20 — Vietnamese challenge phrase and swipes on real people (25/11)

- **E18** (`research/experiments/e18_vi_variation.py`): counts in theory the number of ways to type a sentence with Telex/VNI; a ceiling of 3.0 bits for "Hôm nay trời đẹp quá" ("The weather is so nice today") and 6.6 bits for a sentence with many tone marks. Not a measurement on people.
- **E19 — Touchalytics, 41 real people, 20,896 swipe strokes** (`e19_touchalytics.py`, `results/e19_touchalytics.txt`):
  - The old rule `swipe_straight_max > 0.999` **wrongly flagged 13.4% of real-human 3-stroke sessions** (strokes with few points are almost straight by themselves: 30% of strokes with 3–5 points).
  - **Constant velocity** (velocity CV < 0.3) occurred **0/20,896 times in real people**, catching 100% of constant-swipe bots and bots with ±6 ms timing noise (including bots with 5–10 px lateral noise that the old rule missed). The rule was replaced (`swipe_robotic`, cue `swipe_uniform_speed`, max 0.7). The 95% upper bound of the per-stroke FPR ≈ 3/20,896 = 0.014%; **the bots are still the team's generator**, and real bots could fake human velocity.
  - **Owner check from 5 swipe features: AUC 0.48–0.60 (about guessing)**, even on the same day with the same task (FAR@FRR5% 0.88–0.97). `swipe_*` was **removed from the owner check** (`owner.is_identity_feature`). Limits: only 5 features, pixels differ by device so comparisons were within the same device, 11 people had enough data to allow a test of day 1 vs 7–14 days later.
- **E20 — simulation** (`e20_vi_style_sim.py`): under the assumption that each person has a fixed probability of typing tone marks late, AUC rises from 0.66 (1 syllable with a choice point) to 0.78 (4) and 0.89 (8) for the pair p = 0.8 vs 0.4; and is 0.64 for the pair 0.8 vs 0.6. Used to choose the sentence (≥ 4 syllables with choice points), **not** evidence about real Vietnamese people.

### E21 / E21b — normalization by key pair (following TypeNet, Gunetti–Picardi), Aalto 1,000 people (25/11)

Code: `research/experiments/aalto_note_chars.py` (keeps letters, gitignored, research only), `e21_digraph_norm.py`, `e21b_digraph_profile.py`; tables: `research/results/e21_digraph_norm.md`, `e21b_digraph_profile.md`. E13 protocol, test sentence differs from the enrollment sentence.

| Features (30 keys) | EER | FAR@FRR5% |
|---|---|---|
| E13 raw (6) | 0.249 [0.243, 0.259] | 0.498 [0.473, 0.524] |
| key-pair normalization (6) | 0.245 [0.236, 0.253] | 0.479 [0.456, 0.501] |
| raw + normalization (12) | **0.238** [0.228, 0.245] | **0.467** [0.446, 0.489] |
| common key-pair profile only (E21b) | 0.326 | 0.772 |

**The result is nearly unchanged** (improvement ≤ 1.1 points of EER, confidence intervals touch). Comparing a profile per key pair **makes it worse** because two random sentences share only ~6.5 common key pairs at 30 keys. Conclusion: with a sentence that changes every time, content normalization is not a lever; a sentence-independent channel (Vietnamese typing style) and more keystrokes matter more. Not put into the backend. Related work: [`related-work.md`](related-work.md).

### E22 — ways to reduce the FAR of the Innate Challenge (Aalto, 939 evaluated people, 30 keys, 25/11)

Code: `research/experiments/aalto_note_orient.py`, `e22_improve_far.py`; table: `research/results/e22_improve_far.md`. E13 protocol (test sentence differs from the enrollment sentence); bootstrap confidence intervals by person.

| Configuration | EER | FAR@FRR5% |
|---|---|---|
| 6 raw features, K=1 enrollment sentence | 0.288 | 0.625 |
| K=3 (as in E13) | 0.253 | 0.517 |
| K=5 | 0.246 | 0.471 |
| K=8 | 0.235 | 0.457 |
| raw + key-pair normalization (12), K=3 | 0.248 | 0.502 |
| **+ learned model (LightGBM on the deviation vector), K=3** | **0.227** | **0.429** |
| + holding posture (tilt angle), K=3 | 0.144 | 0.277 |

- **Adding enrollment sentences helps but with diminishing returns:** going from 1 to 3 sentences cuts FAR by 10 points, going from 3 to 8 sentences adds only 6 points.
- **A learned model helps by ~7 points of FAR** (0.502 → 0.429), in the same direction as E12b.
- **Device tilt angle gives the best number (FAR 0.277) but should NOT be trusted:** all of a person's sentences fall within one session, so posture coincides between enrollment and test (E9: a posture change nearly wipes out the signal, EER 0.309). On a real phone it requires asking for sensor permission (iOS Safari), is sensitive data, and measures only "how the phone is being held". Not to be put into the product without two-session data.
- FRR/FAR trade-off table (raw E13, 30 keys): FRR 5% → FAR 49%; 10% → 39%; 20% → 29%; 30% → 22%; 40% → 17%.

### E23 — adding phone motion to the owner check (StrokePIN, 97 people, 25/11)

Code: `research/experiments/e23_imu_fusion.py`; table: `research/results/e23_imu_fusion.md`. E9 protocol; IMU features: gravity (mean, deviation per axis), accelerometer and gyroscope jitter. E2 detector (shrinkage toward the population), k = 3 enrollment entries.

| Feature set | Same posture (sitting): EER / FAR@FRR5% | Posture change (walking): EER / FAR@FRR5% |
|---|---|---|
| PIN (timing + center offset) | 0.197 / 0.692 | 0.374 / 0.936 |
| Motion only | 0.038 / 0.030 | 0.441 / 0.913 |
| PIN + motion | 0.057 / 0.075 | 0.420 / 0.910 |

**This number cannot be trusted:** each person has one phone, so acceleration/gravity carry the **device fingerprint** (sensor bias, holding angle) and not only the person's habits; the impostors in the data use a different phone. The same flaw that removed contact size (E12b). The scenario of an impostor holding the victim's actual phone is not simulated. **With a posture change it all vanishes (EER 0.42–0.48).** StrokePIN records acceleration/gyroscope at ~5 Hz, so matching the touch moment and the jerk could not be checked. Conclusion: motion is a candidate for an anti-bot gate ("a hand is holding it"), and has not been shown for the owner check. 4-channel design: [`../plan/bon-cong-pipeline.md`](../plan/bon-cong-pipeline.md).

### E24–E27 — whole-system decisions, threshold sweep, adaptive bots, latency (StrokePIN, 25/11)

Code: `research/experiments/e24_end_to_end.py` (includes E25, E27, E27b), `e26_latency.py`; full tables: `research/results/e24_end_to_end.md`, `e26_latency.md`. Runs the exact `/score` chain (rules + human/bot model, replay check, owner check + owner model, fusion) in-process, on **10 people never seen by either learned model** (small sample in number of people, hundreds of sessions per group). PIN-knowing impostor = another person entering the same PIN on their own phone (confounded with device noise). Bots come from the team's generator/script.

**E24, known recipient, current thresholds (A=0.25, B=0.55):**
| Group | allow | step_up | hold |
|---|---|---|---|
| owner, sitting | 80% | 19% | 1% |
| owner, posture changed (walking) | 63% | 37% | 0% |
| PIN-knowing impostor (other phone) | 28% | 70% | 2% |
| bot T1, T2, T3 (replay ±5%) | 0% | 0% | **100%** |
| bot T4 (population sampling) | 7% | 67% | 26% |
| replay ±10% | 0% | 0% | **100%** |
| replay ±15% | **58%** | 13% | 30% |
| replay ±20% | **72%** | 26% | 1% |
| replay ±30% | **48%** | 48% | 4% |
| **template-aware** bot (samples from the victim's mean/spread) | **75–82%** | 6–17% | 8–12% |

- **With a new recipient**, the owner is only `allow`ed 17% (79% `step_up`): the "new recipient" weight of 0.15 pushes risk past A. This is by design, but it is a large friction.
- **The learned models matter:** with both learned models off, the PIN-knowing impostor is `allow`ed 90% (only the rules and distance remain).
- **The real weakness (E27):** replay bots with noise ≥ 15% and bots that know the victim's template **fool the system** (allow 48–82%). The system reliably blocks naive bots and low-noise replay; it cannot block an adaptive attacker.

**E25, sweep of threshold A** (B has little influence): there is no optimum for both sides. A=0.25 (current): owner sitting allow 80%, PIN-knowing impostor not-allowed 72%, template-aware bot not-allowed 25%. A=0.30: 91% / 50% / 17%. A=0.20: 65% / 90% / 36%. A=0.10: 17% / 99% / 80% (nearly all owners are bothered). Choose by policy (how many real people we accept asking for extra verification); this should be settled once the team has same-device data.

**E27b, replay threshold** (currently 0.07): 0.085 catches ±15% replay 86% (versus 30%) with the owner held 3% (short history here; E5b extrapolates a higher FPR for long histories); 0.10: catches ±20% 47% but the owner is held 6%. The threshold has not been changed; decide after measuring the team's long histories (T3).

**E26, local latency (TestClient, SQLite, no network):** `POST /sessions` p50 2.2 ms / p95 2.9 ms; `/score` p50 3.8 ms / p95 4.7 ms / p99 6.2 ms. **The first call used to take ~1 s** (lazy loading of the LightGBM models). **Fixed on 25/11:** `main.py` preloads both models at startup; re-measured: `/score` p50 3.7 ms, p99 14.2 ms, max 36.5 ms. The loading cost moved to the cold start on Vercel (Vercel/Neon not measured).

### E28 — 4-digit PIN (web demo) versus 6-digit PIN (25/11)

Code: `research/experiments/e28_pin_length.py`; table: `research/results/e28_pin_length.md`. Same 10 people never seen by either learned model and E24 protocol (known recipient). The 4-digit PIN is simulated by cutting the first 4 taps of a real 6-digit session (**an approximation**).

| PIN | Learned owner model runs? | Owner sitting: allow / step_up / hold | PIN-knowing impostor: allow / step_up / hold |
|---|---|---|---|
| 6-digit | yes | 81% / 19% / 0% | 28% / 70% / 2% |
| **4-digit** | **no** (falls back to distance) | 90% / 7% / 3% | **68% / 30% / 2%** |

`owner_model.predict` returns None when the 6-key features are missing, and the web demo uses PIN 1593 (4 digits): the scenario "a second person who knows the PIN gets `step_up`" would happen only ~30% of the time (the impostors here use a different phone, so the real number may differ). **The demo PIN should be changed to 6 digits** (the data collection page already uses 6 digits) or an owner model should be trained for 4-digit PINs.

### E33 — false alarms by posture, mixed sitting/walking enrollment (StrokePIN, 27/11)

Full `/score` chain, 10 people never seen, known recipient. Enrolling 3 sitting entries: the owner is asked for extra verification 17% when sitting, **41% when walking**; PIN-knowing impostors get through 24–31%. Enrolling **2 sitting + 2 walking**: the owner is asked for extra verification ~18–20% in both postures, but PIN-knowing impostors getting through rises by ~10 points (34–39%). The owner is almost never held (0–1%). With the learned models off (96 people): false alarms are low but PIN-knowing impostors get through 85–94%. Risk analysis and proposal: [`false-alarm-posture.md`](false-alarm-posture.md). Code: `research/experiments/e33_posture_false_alarm.py`.

## 7. Order of work

1. **Send the HuMIdb request**, check the Aalto license (runs in the background, has a waiting time).
2. **E5 and E7** (no real data needed, cheap to fix, recovers points for tactic 3 and template safety).
3. Build the **evaluation framework** (time split, FAR@FRR, DET, confidence intervals) running on synthetic data, so that when real data arrives only the source needs to be swapped.
4. Once data is available: E1 → E3 → E4 → E6 → E2.

## 8. Open questions

1. What is the minimum realistic number of enrollment entries for B to separate people at an acceptable level?
2. Which injection signals are exposed to the SDK, and do they differ between web and native? (R1)
3. Does shrinkage toward the population really help? No source confirms it; it needs measuring.
4. Some sources here are only search-result summaries; the originals of UserBoost (arXiv 2407.09104), Ffinger (arXiv 2504.17271) and the Bayesian swipe study (arXiv 2008.01013) need reading before citing.

## New sources in this round

- ActReal: https://arxiv.org/pdf/2608.30038
- UserBoost: https://arxiv.org/abs/2407.09104
- Contrastive Learning for Continuous Touch-Based Authentication: https://arxiv.org/abs/2504.17271
- Few-shot continuous authentication (Applied Sciences 12(20), 10365): https://www.mdpi.com/2076-3417/12/20/10365
- Swipe dynamics, Bayesian unsupervised: https://arxiv.org/abs/2008.01013
- Review of keystroke dynamics methods: https://arxiv.org/abs/2502.16177
- Radware, attestation + behavioural anomaly detection: https://www.radware.com/blog/application-protection/complementing-attestation-with-behavioural-anomaly-detection-in-mobile-applications/
- HuMIdb (mirror, license procedure): https://github.imc.re/BiDAlab/HuMIdb
