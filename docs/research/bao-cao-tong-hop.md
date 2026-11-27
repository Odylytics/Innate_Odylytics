# Innate consolidated report: project flow and experimental results

> Flow diagrams, template state and per-model cards: [`so-do-luong.html`](so-do-luong.html). Written 26/11/2026 from the code and results in the repo (`research/results/`, `research/EXPERIMENTS.md`, `backend/`). Every number links back to a result file. **All real-human data comes from public datasets (StrokePIN, Aalto, Touchalytics, CMU); we have no team data yet. Every bot is a generator built by the team; there are no real bots yet.** Read together with [`../plan/how-it-works.md`](../plan/how-it-works.md) and [`../plan/positioning.md`](../plan/positioning.md).

## 1. The project in one paragraph

Malware that uses the Accessibility permission to tap on the user's behalf, or a fraudster who knows the PIN, means the PIN and OTP no longer protect a transaction. Innate is a passive "real human" verification layer at the transaction confirmation step: it measures the rhythm and manner of touch while the PIN is entered (and, at the additional verification step, a randomly generated Vietnamese phrase that the user types), then recommends `allow`, `step_up` or `hold`. The system never locks an account by itself; ML and rules decide, and an LLM may only explain.

**Two separate questions**

| Question | Needs enrollment | Catches whom | Strength measured so far |
|---|---|---|---|
| Human or machine? | No | Malware, scripts, `adb` | Naive bots and replay with noise ≤±10%: held 100% (E24). Adaptive bots: 44–86% get through. |
| Is it the owner? | Yes (3 sessions) | Acquaintances, thieves who know the PIN | EER 16–20% (E9). Not strong enough to be a blocking gate. |

**Honest positioning:** the strong part is detecting automated control and replay. Owner recognition is an additional risk signal, fused by weights, not an AND gate.

## 2. System flow

```
Wallet app + Innate SDK (records events, not content)
  │  touch: coordinates, down/up time of each key, contact size, swipes
  │  text fields: only timing, kind (key/paste/delete/set_text), character count
  ▼
POST /v1/sessions           → features.extract (≈24 identity features + bot_features)
POST /v1/users/{id}/enroll  → after 3 sessions: owner.build_template (mu, sd shrunk toward the population), enrollment lock (409 afterwards)
  ▼
POST /v1/sessions/{id}/score   (scoring chain, runs in-process, p50 3.7 ms local)
  1. human.score (rules) + human_model (LightGBM)   → human/machine score; the bot rule takes the min with the model
  2. replay.is_replay (distance ≤0.07 to an old session) → forces hold, reason replayed_session
  3. owner.score (scaled Manhattan, sd with floor, shrinkage nu=5) → owner_model (LightGBM) replaces the score when the PIN has all 6 keys
  4. fusion.fuse: risk = 0.40·(1−human) + 0.35·(1−owner) + 0.15·new recipient + 0.10·amount anomaly
        hold if human < 0.3 or risk > B(0.55); step_up if risk ≥ A(0.25); otherwise allow
  5. explain: Vietnamese reasons from the rules and each feature's deviation
  ▼
The template is updated only when: not an enrollment session, action = allow, owner ≥ 0.8, human ≥ 0.8
  - drift cap of 1 sd per feature; if mean drift > 0.5 sd, freeze (E7, frozen flag)
```

**Two running configurations (important when quoting numbers).** The learned models (LightGBM human/machine and owner recognition) are optional with a rule fallback.
- **With learned models:** the configuration measured in E24, E29 (table 5.6) and the other experiments.
- **Rules only:** human/machine by rules alone, owner recognition by normalized distance alone (`/health` reports `models` false). This was the online configuration **until 26/11**, when lightgbm failed to load on Vercel (missing system library). It was fixed with a pure-Python model reader, `lgbm_text.py`; after redeploying, `/health` reports true (checked 26/11). Rules only remains the fallback mode and the mode when models are switched off. Its measurements are in the "Rules only" table in 5.6; it is clearly weaker against PIN-knowing impostors and adaptive bots.

**Two layers and four scenarios (design of 26/11, `../plan/bon-cong-pipeline.md` section 7).** Layer 1 is human or machine (no enrollment needed); layer 2 is person versus person (needs enrollment; only a risk signal, leading to `step_up`, never blocking by itself). The four scenarios are (Android or iPhone) × (remote takeover or stolen device). Android remote takeover leans on layer 1 (`hold`); a stolen device leans on layer 2 (`step_up`). iPhone remote takeover is out of scope according to the team's judgment, not verified against documentation. There are no measurements split by iPhone or Android yet.

**Demo wallet flow (implemented, `web/src/Wallet.tsx`):** entering the PIN when opening the wallet is only recorded, not scored, not blocking; scoring happens once at the transfer confirmation step, and the session carries both the PIN rhythm and the transfer actions. Two test scenarios: Android remote takeover (malware, expected `hold`) and stolen device (someone who knows the PIN, expected `step_up`). This order differs from where E24 to E29 measured (PIN right at confirmation); the session features still include the PIN rhythm so the measurements are approximately valid, but it has not been measured separately.

**Action at `step_up`:** the explanation now returned is "Đề nghị gõ một câu ngắn để xác nhận trước khi chuyển" (Please type a short phrase to confirm before transferring) (Innate Challenge, a random phrase), and if still uncertain then face or OTP. Typing the phrase is **not a gate**: at 30 keys the impostor still gets through 43–52% (E22), so the result goes back into `fusion` as additional evidence.

**Innate Challenge (additional verification step):** `GET /v1/challenge` issues a random Vietnamese phrase with ≥4 syllables that have a tone-mark choice, with a signed, single-use token. The app sends `fields[challenge]` (token, length, events). `features.extract` adds `vi_*` features through `vi_ime.py`. Currently there is only the soft cue `challenge_no_ime` (≤0.3); `vi_*` is not yet in owner recognition because there is no real Vietnamese data.

**Design constraints:** store only timing, coordinates, key labels; do not store the PIN of a real account; do not rely on `pressure` or `isTrusted`; the template is not taught gradually; the system does not lock accounts. A deliberate exception: the `#/collect` page stores the digits of a throwaway PIN that the volunteer sets, with full name and email (with consent).

## 3. Team data collection flow

1. A volunteer opens `#/collect` on a phone: enters full name and email, reads the consent form.
2. Sets a 6-digit PIN (entered twice), then re-enters it 5 times through a fake transfer screen.
3. After each PIN entry, types a random Vietnamese phrase (signed token, paste blocked, with a skip button if the keyboard cannot type tone marks).
4. All 5 sessions are sent together with `meta` (hash from the email, full name, email, notes).
5. Analysis: `team_analysis.py export.jsonl` (T1–T5, bootstrap by person), `train_human_model.py --export ... --out DIR`.

**Status:** the pipeline was tried with synthetic data (`team_data_dryrun.py`); there is no real data yet. The export file contains personal data and is not put in the repo or the submission zip.

## 4. Evaluation protocol

- Per FETA: time split between enrollment and test, one device, no impostor data when training the owner model, split by person for pairwise models.
- Main metric: **FAR@FRR 5%**, with EER; 95% bootstrap confidence intervals by person.
- "PIN-knowing impostor" means another person entering the same PIN on a different device, so the measurement is confounded by the device and optimistic.
- Bots: 4 tactics generated by the team. T1 uniform, T2 timing noise, T3 replay (with ±n% noise), T4 sampling from the population distribution; plus a "template-aware" bot in E27.

## 5. Experimental results

### 5.1 Human or machine (no enrollment needed)

**E4b, real StrokePIN humans + generated bots, FRR 5% threshold, fraction of bots caught** (PIN part only):

| Model | T1 | T2 | T3 | T4 |
|---|---|---|---|---|
| LightGBM, sees all 4 tactics | 1.00 | 1.00 | 0.26 | 0.73 |
| Baseline rules (`human.py`) | 1.00 | 1.00 | 0.05 | 0.01 |
| LightGBM, **that exact tactic left out** of training (unseen bot) | 1.00 | 0.56 | 0.09 | 0.20 |

Naive bots are caught 100%; for human-like bots the model easily learns shortcuts. Lesson: unseen bots are the main weakness.

**E11, free text fields (Aalto, 33,522 sentences from 2,260 people):** LightGBM catches bots that set text directly 100% and even typing 99% once it has seen that bot type; with that exact tactic left out: even typing 0%, replay 5%, population sampling 4–5%. The backend's current rule on the note field catches 0%. The `text_set_without_keys` rule for the amount field is unverified (no human data).

**E19, swipes (Touchalytics, 41 people, 20,896 strokes):** the old rule `straight>0.999` wrongly flagged 13.4% of human sessions; replaced by `swipe_robotic` (velocity CV <0.3): 0/20,896 human strokes wrongly blocked. A straight-swipe bot is caught 100%; adding 2 px of lateral noise leaves 43%, 5 px leaves 4%. Swipe features give AUC ~0.5 for owner recognition, so they were removed from identity.

**E13, number of keys in the typed phrase (Aalto), bot AUC:** T2 0.915 (6 keys) → 0.995 (30 keys); T4 0.719 → 0.891.

### 5.2 Replay

**E5b, calibration on real humans (1,817 person-PIN pairs):** the backend threshold 0.085 (synthetic data) was lowered to **0.07**. The rate at which a human session is mistaken for a replay grows with the number of old sessions (0.08% at 2 sessions, 0.14% at 3, 0.20% at 4 at the 0.07 threshold; extrapolated ~3.0% at 50, a guess). Catch rate by replay attacker noise:

| Threshold | ±5% | ±10% | ±15% | ±20% | ±30% |
|---|---|---|---|---|---|
| **0.07 (chosen)** | 1.00 | 1.00 | 0.28 | 0.00 | 0.00 |
| 0.085 | 1.00 | 1.00 | 0.85 | 0.10 | 0.00 |
| 0.088 (FPR 1%) | 1.00 | 1.00 | 0.92 | 0.16 | 0.00 |
| 0.107 (FPR 5%) | 1.00 | 1.00 | 1.00 | 0.73 | 0.01 |

A higher threshold catches more but wrongly blocks the owner: in E27b, a threshold of 0.12 made the owner get held 15% of the time.

### 5.3 Owner recognition

**E9, StrokePIN (97 people, 6-digit PIN), 3-session enrollment, PIN-knowing impostor:**

| Condition | EER | FAR@FRR5% |
|---|---|---|
| Timing, backend | 0.201 | 0.686 |
| Timing, **shrinkage toward the population (E2)** | 0.199 | 0.565 |
| Timing + offset from center + touch size | 0.155 | 0.656 |

Touch size may carry a device signal (one phone per person). Numbers re-run 27/11.

**E12b, learned model, without touch size:**

| Model | EER | FAR@FRR5% |
|---|---|---|
| baseline mean |z| | 0.160 | 0.549 |
| LightGBM | 0.140 | 0.316 |

**E1/E2 (CMU, computer keyboard) and E10:** shrinking the variance toward the population lowers FAR@FRR5% by 9–16 points, EER unchanged; put into `owner.py` (`population_prior.json`, nu=5).

**E13, number of keys (Aalto, timing only):** EER 0.364 → 0.245 and FAR 0.807 → 0.489 when going from 6 to 30 keys. This is the basis for Innate Challenge. **E14:** owner typing 6 new digits gets EER 0.33. **E22:** the learned model lowers FAR by a further ~7 points on the typed phrase; the holding-angle feature is optimistic so it was dropped.

**E23, motion (IMU):** IMU alone reaches EER 0.038–0.068 (FAR@FRR5% 0.03–0.09), but it is a **device confound** (one phone per person). **Do not claim owner recognition by IMU.**

**E21/E21b:** per-digraph normalization barely changes anything; a per-digraph profile makes it worse.

**E18, E20 (Vietnamese, simulated):** a phrase has 3–6.6 bits of Telex/VNI typing variation (theoretical ceiling). Typing-style AUC 0.66 (1 syllable) → 0.89 (8 syllables); choose phrases with ≥4. There are no real people typing Vietnamese yet. Telex or VNI cannot be observed on a phone web page (keyCode 229).

### 5.4 Whole system (E24, E25, E27, E28)

10 people never seen by either learned model, 3 enrollment sessions, thresholds A=0.25 B=0.55, known recipient (re-run 27/11):

| Group | hold | step up | allow |
|---|---|---|---|
| Owner | 1% | 18% | 81% |
| PIN-knowing impostor (different phone) | 1% | 71% | 28% |
| Uniform bot / timing noise / replay ±5% / ±10% | 100% | 0% | 0% |
| Population-sampling bot (T4) | 23% | 72% | 5% |
| Replay ±15% | 28% | 13% | 60% |
| Replay ±20% | 1% | 26% | 72% |
| Replay ±30% | 3% | 53% | 44% |
| Template-aware bot (scale 1.0) | 6% | 15% | 79% |
| Template-aware bot (scale 0.5) | 9% | 5% | 86% |

New recipient: the owner is allowed only 18% (step_up 79%).

**E25, sweep of threshold A (B=0.55):**

| A | Owner allowed | PIN-knowing impostor not allowed |
|---|---|---|
| 0.10 | 18% | 100% |
| 0.20 | 64% | 90% |
| **0.25 (current)** | **81%** | **72%** |
| 0.30 | 90% | 54% |
| 0.40 | 97% | 13% |

There is no optimum for both sides.

**E28, PIN length (simulated by cutting the first 4 taps):** a 4-digit PIN makes the owner model unable to run, and a PIN-knowing impostor is allowed 68% (6 digits: 28%). **Conclusion applied: the web demo switched to the 6-digit PIN `159357`.** With 6 digits and AI on, a new owner is allowed 16/25 times in the demo scenario (`docs/plan/web-demo.md`).

**E3, owner score calibration:** the old mapping (d=2→0.5) lets 84% of PIN-knowing impostors exceed 0.5 (owner 96%); class-balanced Platt leaves 27% (owner 90%). At FRR 5% FAR is still ~50%. Wiring it into the backend (`NHIP_OWNER_MAP=platt`) only changes the fallback path, drops the owner at a new recipient from 91% to 3% allowed, and blocks template updates, so it is **left off by default** (`e24_platt_map.md`).

**E7, template poisoning (synthetic data):** without a drift cap the impostor is accepted 100% and the owner is locked out (0.58). Freezing when drift >0.5 sd gives 0.77 (versus 0.85 for the 1 sd cap), with a warning flag. Implemented in `owner.update`; the flag is not yet exposed in the API.

### 5.6 Rechecked on all 97 people (E29, E30): these numbers replace the 10-person table in 5.4 when quoting

**E29:** E24 rerun with 5-fold cross-validation by person. Each fold retrains the two learned models only on people outside that fold. 97 people, up to 6 PINs per person, bootstrap confidence intervals by person. Known recipient, A=0.25, B=0.55:

| Group | hold | step up | allow |
|---|---|---|---|
| Owner | 1% | 22% | 77% [74, 80] |
| PIN-knowing impostor (different phone) | 1% | 82% | **17% [15, 19]** |
| Uniform bot / timing noise / replay ±5% / ±10% | 100% | 0% | 0% |
| Population-sampling bot (T4) | 34% | 63% | 2% |
| Replay ±15% | 32% | 20% | 49% [45, 52] |
| Replay ±20% | 4% | 39% | 56% [53, 59] |
| Replay ±30% | 8% | 65% | 27% [24, 31] |
| Template-aware bot (scale 1.0) | 4% | 19% | 77% [73, 80] |
| Template-aware bot (scale 0.5) | 5% | 6% | 89% [87, 91] |

- The conclusion of E24 does not change, and is narrower: a PIN-knowing impostor gets through **17% (not 28%)**. Numbers re-run 27/11.
- New recipient: the owner is allowed only 15%, a PIN-knowing impostor 0%, the template-aware bot 18% (scale 1.0) to 40% (scale 0.5).
- Sweep of A: A=0.20 blocks a PIN-knowing impostor 96% but the owner only gets through 55%; A=0.30 lets the owner through 89% but blocks a PIN-knowing impostor 67%.
- **Distribution by victim:** the median share of PIN-knowing impostors allowed is 17%, the 90th percentile is 29%, the maximum 46%, Gini 0.33. No victim is allowed above 50%. That is, no one is "always exposed" in this configuration.

**Online demo configuration (rules only, learned models off), same 97 people, known recipient** (`e29_rules_only.md`):

| Group | hold | step up | allow |
|---|---|---|---|
| Owner | 0% | 3% | 96% [95, 98] |
| PIN-knowing impostor (different phone) | 0% | 10% | **89% [88, 91]** |
| Uniform bot / timing noise / replay ±5% / ±10% | 100% | 0% | 0% |
| Population-sampling bot (T4) | 0% | 18% | 82% [80, 84] |
| Replay ±15% | 30% | 1% | 69% [66, 72] |
| Replay ±20% / ±30% | 1% / 0% | 1% / 1% | 98% / 99% |
| Template-aware bot (scale 1.0 / 0.5) | 0% / 4% | 3% / 1% | 96% / 96% |

- **Rules only can barely tell someone who knows the PIN from the owner:** 89% are allowed, versus 17% with the learned models. Distribution by victim: median 92%, 49/97 victims allowed above 90%.
- The owner has an easier time (96% through) because the system is less suspicious, not because it discriminates better.
- The rule part still firmly catches naive bots and replay ≤±10% (100% hold).
- **Consequence for the demo:** the scenario "Bảo knows the PIN and gets `step_up`" uses a synthetic persona with clearly different habits, so it works on the rules-only build; with the learned models on, the demo outcome changes (earlier measurement: Bảo was `hold` 14/25 times) and must be re-recorded as a trial. On real people, rules only lets 89% through and the learned models 17%. Do not use the demo (simulated sessions) as evidence of "blocks someone who knows the PIN"; use the E29 measurements.

**E30, number of enrollment sessions (owner recognition by distance, 97 people):**

| k | EER | FAR@FRR5% |
|---|---|---|
| 2 | 0.167 | 0.857 [0.661, 0.923] |
| 3 | 0.146 | 0.503 [0.421, 0.627] |
| 4 | 0.138 | 0.429 [0.360, 0.534] |

More enrollment means fewer impostors get through, with the clearest drop from 2 to 3 sessions. k=1 cannot compute a standard deviation; k=5 leaves no test session because StrokePIN has at most 5 sessions per person-PIN, and k=4 tests on only 1 session. The population prior is taken from the backend's file and does not exclude each victim separately, so it may be slightly optimistic.

**E31, tuning the fusion weights and threshold A on the E29 data** (tune on 3 folds, test on 2 other folds by person): the best configuration found (wb 0.50, wo 0.30, A 0.26) does not raise the average not-allowed rate of the 7 adaptive attack groups on the test folds (54% → 54%; tune folds 55% → 56%), while lowering PIN-knowing impostor blocking from 86% to 81% (re-run 27/11). The improvement is smaller than the fluctuation between folds, so **keep the current weights and thresholds**. Lesson: this is not a parameter-tuning problem but a limit of the signal.

### 5.5 Performance and infrastructure

- **E26:** `/score` p50 3.7 ms, p95 5.2 ms, max 36.5 ms (local, after models are preloaded; before that the first call took ~1 s). Excludes network and cold start.
- **R6:** 100 `GET /health` calls to `nhip-api-taupe.vercel.app`: min 0.16 s, p50 0.22 s, p95 0.48 s, max 1.27 s. `/score`, cold start after idle time, and free-tier limits not yet measured.
- Tests: backend 50, attacker 8, web 8 tests all pass; `vite build` succeeds.

## 6. Known limitations (should be stated verbatim on the slides)

1. No team data and no real bots; bot training and test share the same 4 generators.
2. **When the learned models are off (load error or switch), the system falls back to rules only and a PIN-knowing impostor is allowed 89% on real people (E29 rules only)**; the better number (17%) holds only with the learned models on. A test and the script `check_online.py` exist to watch for this.
3. Owner recognition by touch rhythm is weak (FAR ~50% at FRR 5%); the PIN-knowing impostor in the measurements uses a different phone, so the numbers are optimistic.
4. Template-aware bots get past 77–89% and replay ±15% to ±20% gets past 49–56% (E29, 97 people); no countermeasure yet (ActReal reports adaptive attack success of 71–77%).
5. The learned models use StrokePIN data (CC BY-NC-SA 4.0), so the whole repo follows that license; the models are temporary until team data exists.
6. No controlled re-enrollment path yet (design in `../plan/dang-ky-lai.md`); there is no way to unfreeze a frozen template.
7. Vietnamese typing style is not verified on a real keyboard; `vi_*` is not yet wired into owner recognition.

## 7. Remaining work (until 03/12)

| Task | Needs |
|---|---|
| Collect team data, run `team_analysis`, retrain | Participants |
| Real bots via `adb` as an independent test set | Android phone |
| Measure touch size (R2) on Android Chrome and iOS Safari | Real phones |
| Re-record the demo trial with learned models on (on since 26/11) and fix the script wording for the Bảo step; run `check_online.py` before recording and before 03/12, 11/12 | Team |
| Redeploy the web with the 6-digit PIN, record the video | Deploy decision |
| Fill in the submission file (team name, URL, demo key, README, slides) | Team |
| If Platt is wanted: move A/B and `UPDATE_MIN_OWNER`, remeasure E24/E25 | Team data |
| Expose the `frozen` flag in the API, implement re-enrollment | One round of backend code |

Deadlines: 27/11 23:59 registration and questions to the organizers; 03/12 23:59 submission; 11/12 final, the product must stay online.
