# Innate — Project description and paper verification

> **Innate** (bẩm sinh, "innate") — pitch story: [`pitch-story.md`](pitch-story.md).

> Updated 24/11/2026. This document summarizes the idea, the state of the source code, and the results of checking the figures in the plan against the original papers in [`papers/`](../../papers/).
> Full plan: [`innate-momo-tech-contest.md`](innate-momo-tech-contest.md). Paper synthesis: [`../research/paper-report.md`](../research/paper-report.md).

## 1. Idea

**Innate** is a behavioral risk scoring layer (B2B SDK + API) for e-wallets and banks. When a phone is taken over, money still leaves through the victim's own app, PIN and device, so traditional authentication treats it as the legitimate owner. Innate answers two questions at the transaction confirmation step:

1. Is this interaction by a **human finger** or by a **machine** (Accessibility malware, `adb`, a script)?
2. If a human, does it **match the account owner's habits**?

Two scenarios: **A** remote-control malware (RedHook, Gigabud, SpyNote...), **B** an acquaintance/thief who knows the PIN.

The input consists only of touch timing and coordinates (key hold, interval between keys, offset from key center, contact size, swipes); the PIN content is not stored. The output: a human/machine score, an owner-match score, risk, an action `allow | step_up | hold`, reasons and an explanation sentence in Vietnamese. The system **only recommends** and never locks an account. An LLM is not on the decision path.

### Three scoring layers

| Layer | Method | Basis |
|---|---|---|
| Human or machine | "Naturalness" rules (baseline) → LightGBM/RF | BeCAPTCHA, Iliou 2021, Serwadda & Phoha 2013 |
| Is it the owner | Template from 3–5 entries, scaled Manhattan, update with a drift cap | Killourhy & Maxion 2009, Zheng 2014, Buschek 2015 |
| Fusion | Weighted sum after normalization, 3 zones by thresholds A/B | Freeman 2016, Wiefling 2020–2022 |

## 2. Current state (24/11/2026)

| Have | Not yet |
|---|---|
| FastAPI + SQLAlchemy backend, deployed on Vercel + Neon; endpoints `/v1/sessions`, `/enroll`, `/score`, `/export`, `/label` | JavaScript SDK, custom-drawn PIN keypad |
| Baseline scoring: `human.py` (rules), `owner.py` (Manhattan + drift cap), `fusion.py`, `explain.py` | Demo wallet, operations dashboard |
| Hacker simulator with 4 tactics + `adb` | Real-human data, LightGBM/RF models |
| 7 + 7 tests | Real evaluation figures (FAR@FRR 5%, EER, DET) |
| 52 paper PDFs + synthesis report | Slides, video, 1-page PDF, submission README |

The existing baseline figures (catches 100% of tactics 1–2, 0% of tactic 3, 5–30% of tactic 4) were measured on **fake** people and are not for slides.

## 3. Verifying the figures against the original papers

PDF text was extracted and compared.

| Claim in the plan | Result of the check |
|---|---|
| Zheng 2014: EER 3.65–7.34% when entering a PIN | **Correct.** PIN `3-2-4-4` 3.65%, `1-1-1-1` 6.96%, `5-5-5-5` 7.34%, 8-digit PIN ~4.5%. 80+ people, 85 training entries per person, and **uses acceleration, pressure, contact size and timing together**. |
| Buschek 2015: adding touch position cuts EER by 26.4–36.8% | **Correct.** 28 people, 2 weeks. Evaluating within a single session gives EER less than half that of across sessions. |
| FETA 2022: EER 4.9% → 13.8% | **Correct.** Reviewed 30 papers, all made at least one error. Putting impostor data into training flatters results by 2.55 points, mixing device generations by 3.2–5.8 points. |
| BioTouchPass2: EER 2.38% | **Correct.** 217 people, 4-digit PIN, RNN model. Under imitation attacks, EER is 10.4–15%. |
| Lovisotto 2020: template poisoning >70% with <10 injections | **Correct.** Detection catches >99% after 2 injections. |
| Touchalytics 2012 | Median EER 0% same session, 2–3% across sessions, <4% after one week. The authors themselves conclude it is **not sufficient as standalone authentication**, only suitable as part of a multi-signal system. |
| TypeNet 2021 | EER 9.2% on touchscreen keyboards (free text, >100k people). Stragapede 2022 (Transformer): 3.84% on Aalto with 5 enrollment sessions. |
| Freeman 2016 (LinkedIn) | Weighted signal combination, AUC 0.913 → 0.955. Uses login context, not touch biometrics. |
| BeCAPTCHA 2021 | Adding the accelerometer clearly improves results, keeping the bot catch rate >90% when training is diverse. The "agnostic" mode (unseen bots) is much worse. The "~60% → 80–90%" figure in the plan was **not found verbatim**. |
| Killourhy 2009: scaled Manhattan is best | The abstract gives the two best sets as EER 9.6% and 10.2%. Not confirmed which set reaches 9.6%. |
| Scenario A: Accessibility malware has high privileges | **Correct.** Cloak & Dagger (2017): Accessibility + overlay control the whole UI feedback loop, capture the PIN, install apps. Diao 2019: design flaws in the Accessibility framework. AccessiLeaks 2019: 72% of top financial apps leak information. |

Could not be downloaded (paywalled or the source blocks automated download): Tey 2013 (NDSS), Serwadda & Phoha 2013, Biggio 2013, Pisani 2016, Jain 2005, ISO 19795-1, Patel 2016, Stylios 2021, Vijayanand 2025. DOIs are in `docs/research/paper-report.md`.

## 4. Most important finding

**ActReal (Wang 2026, preprint)**: a privileged system-level agent can generate touch and IMU sensor data that match in time. The average attack success rate is 77.5% against detectors based on touch trajectory/timing, and **still 71.1% when the detector uses both touch and IMU**. This means sufficiently sophisticated malware can fool the "human or machine" layer. This is a bigger obstacle than any EER figure.

Other points:
- The best figures come from favorable conditions (Zheng: 85 enrollment entries, many sensors; BioTouchPass2: 217 people, RNN). Innate has ~25 people, one phone, 3–5 entries, **no pressure** (Pointer Events returns 0.5). A realistic expectation is **10–15% EER**.
- Imitation attacks (scenario B) have concrete figures (10–15% EER) and belong in the slides.
- For unseen bots, a classifier trained on pre-generated bots drops sharply (BeCAPTCHA, BeCAPTCHA-Type: few-shot is a challenge). Training and testing on the team's own 4 bot generators gives figures that look too good.
- Eberz 2017: mean EER hides systematic errors, so the per-person distribution should be reported.
- Ahmed 2026: report error at the operating point (FAR@FRR) with confidence intervals, not a standalone ROC-AUC.

## 5. Conclusions

1. **The direction has a real academic basis.** Typing rhythm, touch position during PIN entry and swipes distinguish person from person (EER a few % to ~10%) and person from naive bot. Most figures in the plan match the papers.
2. **It should only be a risk signal, not an authentication gate.** Touchalytics, Zheng and FETA all say so. The design of `step_up` rather than hard blocking is right.
3. **The strongest part for the demo is catching naive bots** (tactics 1–2, `adb`, basic malware). This is the most realistic behavior of today's Accessibility malware.
4. **The weakest part is adaptive bots** (tactics 3–4, ActReal). This must be said plainly in the pitch, a replay check added, and measurement done with an independent bot source, not the generator used for training.
5. **Differentiating value**: transparent reasons, `step_up`, an open API usable for any wallet, and honest evaluation following FETA. Pitch it that way and do not promise figures.

## 6. To do

| Priority | Task |
|---|---|
| 1 | Register for the contest and send questions to the organizers **before 23:59 on 27/11** |
| 2 | Web demo wallet + Pointer Events SDK + custom-drawn PIN keypad (currently blocking everything else) |
| 3 | Collect real data: ≥ 2 collection rounds, one phone, with consent forms |
| 4 | Backend: "duplicate of an old session" check to catch tactic 3 |
| 5 | Model 1 (LightGBM/RF), keeping the `adb` bot source separate as an independent test set |
| 6 | Calibrate `owner.py` (the mapping d=2 → 0.5 is too lenient) on real data |
| 7 | Evaluation: FAR@FRR 5%, DET, confidence intervals, per-person error distribution, bot catch rate by tactic |
| 8 | Slides ≤10 pages, video ≤3 minutes, 1-page PDF, README declaring assets/OSS/AI tools. Submit before **23:59 on 03/12** |
