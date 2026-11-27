# Innate — Behavioral risk scoring layer for e-wallets

> **Innate** ("innate") — a PIN can be stolen, innate touch habits are very hard to steal. Pitch story: [`pitch-story.md`](pitch-story.md).
> **Positioning (24/11, latest):** Innate is a **human verification layer** running silently at the transaction confirmation step, complementing PIN/OTP/face: [`positioning.md`](positioning.md). The numbers in this document are the original plan; real measurements are in `../research/ai-research.md`.

> Entry plan for **MoMo Tech Contest 2026** · Theme: Cybersecurity + Anti-fraud
> Team of 3 · Updated: 23/11/2026

---

## 1. Contest summary

| Item | Details |
|---|---|
| Name | MoMo Tech Contest 2026 (part of MoMo Tech Series · *Imagine The Future Workspace — Human Centered. AI Powered*) |
| Eligibility | University/college students in Vietnam, Vietnamese nationality, aged 18–23; teams of 2–3; no individual entries; people working/interning at MoMo may not enter |
| Registration | 10:00 13/11 → **23:59:59 27/11/2026** (team leader registers at techday.momo.vn) |
| Deadline for clarification questions | **23:59:59 27/11/2026** |
| Submission deadline | **23:59:59 03/12/2026** — no edits after the deadline, including the product at the submitted link |
| Top 5 announced | 08/12/2026 |
| Final | 11/12/2026, in person in Ho Chi Minh City (The Adora Premium, Tan My) — 5 teams present + answer judges; all members must attend; own expenses |
| Prizes | First 50 million · Second 30 million · Third 20 million (tax included) · Top 3 go straight to the Leadership Interview round of MoMo Talent 2027 |
| Judging criteria | Creativity · Quality & completeness (product runs stably at submission time) · Impact potential. Weights not published. Each entry is scored independently by ≥ 3 judges |
| Judges | CTO, Head of AI & Data and AI/Software Engineering leads at MoMo → technically oriented |
| Product uptime | Online continuously until the end of 11/12/2026 |
| Organizer contact | techday@mservice.com.vn |

### Submission components

| Component | Requirement |
|---|---|
| Product | PDF guide ≤ 1 A4 page, with an online trial link + demo account |
| Source code | .zip of all code + README (how to run, technology, **existing assets, open-source libraries, AI tools used**, data sources) |
| Slides | ≤ 10 pages PDF, stating the problem & solution — **also used as-is for the final, cannot be edited** |
| Video | ≤ 3 minutes MP4, recording the product running for real |

### Disqualification conditions to avoid

- Submitting a product that already existed for this very problem / copying
- People outside the team taking part in building it
- Sharing code between teams
- Editing the product after the deadline
- Hiding the use of existing assets (must be listed in the README)
- Personal/business data without stated source and basis for use

---

## 2. The problem

**The phone is taken over → money is transferred out using the victim's own app and PIN.**

Two scenarios:

| | Scenario A — Remote-controlled malware | Scenario B — Someone else holds the phone and knows the PIN |
|---|---|---|
| How it happens | The victim is tricked into installing a fake APK and grants the Accessibility permission. The malware watches the screen, reads OTPs, opens the app itself and taps the transfer itself (e.g. RedHook, Gigabud, Hirudo, SpyNote — warned about in 2026 by the police and security vendors) | An acquaintance, or a thief who shoulder-surfed the PIN |
| Why it gets through | PIN/OTP/device are all "correct" — traditional authentication treats it as the genuine owner | Same as left |
| Signal to detect | The actions are **not a human finger**: rhythm too even, swipe too straight, tapping exactly at the button center | The actions are a human's, but **do not match the account owner's habits** |

**The question the product answers:** *"Is the person operating a real human — and are they the account owner?"*

---

## 3. The product

**Innate** is a **B2B (SDK + API)** behavioral risk scoring layer for e-wallets and banks. A partner embeds the SDK in its app and calls the API at the transaction confirmation step to receive a risk score, a recommended action and the reasons.

### Submission components

| # | Component | Description | How judges use it |
|---|---|---|---|
| 1 | **JavaScript SDK** | Records taps, swipes, scrolls, PIN rhythm (only time + coordinates, **content is not stored**) | Runs silently in the demo wallet |
| 2 | **Scoring API** (core) | `POST /v1/sessions/{id}/score` | Try it through Swagger with the demo API key |
| 3 | **Demo wallet** | A wallet app with **its own brand** (does not copy MoMo's interface/logo), flow: Home → Transfer → Enter account number → Enter PIN | Enroll the rhythm, then let others try |
| 4 | **Operations dashboard** | List of suspicious sessions + explanation + a correct/incorrect marking button | Fits the "Future Workspace" spirit |

### Example API response

```json
{
  "session_id": "s_8f21",
  "human_score": 0.97,
  "owner_match": 0.31,
  "risk": "high",
  "action": "step_up",
  "reasons": ["pin_rhythm_slower_40pct", "tap_offset_right", "new_recipient"],
  "explanation_vi": "Thao tác giống người thật nhưng không khớp thói quen của chủ tài khoản. Đề nghị xác thực khuôn mặt trước khi chuyển."
}
```

(`explanation_vi` in English: "The actions look like a real person but do not match the account owner's habits. Face authentication is recommended before the transfer.")

`action`: `allow` (let through) · `step_up` (require extra authentication, e.g. face) · `hold` (hold the order, notify the user). **The system only recommends, and never locks accounts on its own** — the "Human Centered" point.

### How it differs from what MoMo already has

MoMo publicly states it has PIN, OTP, face biometrics (iProov, Flashmask), AI transaction analysis and "AI behavior analysis" (without stating clearly whether touch/swipe biometrics are used). Innate differs in:

1. **Transparency**: lets users and operations see *why* a session is suspected.
2. **Extra authentication instead of hard blocking**.
3. **Dedicated detection of actions produced by a machine/emulation** (Accessibility malware).
4. An **API usable by any wallet/bank**.

---

## 4. Architecture

```
┌────────────────────────────────────────────┐
│ Wallet app + signal-collecting SDK         │  tap · swipe · scroll · PIN rhythm
└───────────────────┬────────────────────────┘
                    ▼
┌──────────── Session scoring API (< 200 ms) ─────────────┐
│  [ML] Human or machine?   [ML] Is it the owner?   [ML] Fusion │
└──────────┬─────────────────────────────────────┬────────┘
           ▼                                     ▼
  Instant decision                       [LLM] Explanation
  allow / step_up / hold                 for users & operations
                                                 ▼
                                      Operations team dashboard
                                      (mark correct/incorrect → update the model)
```

**Principle:** ML makes the decision; the **LLM only explains and is not on the decision path** (because of latency, consistency, auditability).

### Technology

| Part | Technology |
|---|---|
| API & ML | Python, FastAPI, scikit-learn, LightGBM (models preloaded in memory) |
| Storage | Postgres (e.g. Supabase): sessions, templates, labels |
| Frontend | Next.js (demo wallet + dashboard), SDK in TypeScript |
| Deploy | API on an always-on platform (no sleeping); frontend on Vercel |
| LLM | Claude/OpenAI API, called asynchronously, with a cost cap |

---

## 5. AI layer in detail

### 5.0 Feature extraction (~40 features per session)

| Group | Features | Role |
|---|---|---|
| PIN rhythm | Hold time of each key (4), gap between keys (3), total time | **Strongest when combined with touch position** — adding touch position to rhythm reduces EER by 26–37% (Buschek 2015) |
| Touch position | Offset from the button center (dx, dy), touch area size | Personal habit of tapping off-center; also a human/machine signal |
| Swipe & scroll | Time, length, mean/peak velocity, acceleration, curvature, start point | **Secondary** signal: 1 swipe ~13% EER, needs 11–12 swipes to get down to 2–3% (Touchalytics) |
| Motion sensors *(new, optional)* | Accelerometer around the tap time (`devicemotion`) | Human vs machine: adding the accelerometer raises the bot catch rate from ~60% to 80–90% (BeCAPTCHA 2021). iOS needs a permission prompt |
| Session rhythm | Time sitting still on the screen, time to the first action | Being coached / being controlled — **the team's hypothesis**, no academic study yet |

Technical notes:
- The PIN keypad is **drawn in-app** + Pointer Events → gives coordinates, press/release times, touch size (avoiding the on-screen keyboard problem of mobile web).
- Do not rely on `pressure`: the W3C Pointer Events standard says that a device that cannot measure pressure returns a fixed 0.5; FETA notes that most Android devices estimate pressure from touch size.
- Do not rely on the `isTrusted` flag to catch bots (scripts can create fake events; Accessibility malware taps at the system level) — detection is based on the rhythm and shape of the actions.

### 5.1 Model 1 — Human or machine?

- **"Human" data**: real sessions collected by the team.
- **"Machine" data**: a hacker simulator generates sessions following 4 tactics (easy → hard):
  1. Taps evenly spaced, exactly at the button center
  2. Adds random noise to timing
  3. Replays a real human session with added noise
  4. Samples timing from the real human distribution
- **Model**: LightGBM / Random Forest + "naturalness" features (rhythm variation, swipe straightness, spread of touch positions).
- **Report** the catch rate **per tactic**; acknowledge that tactic 4 is hard.
- **Add one real attack source** beyond the simulator: `adb shell input tap` from a laptop (and if time allows, an app using an AccessibilityService `dispatchGesture` — exactly the mechanism malware uses). This is also the "hacker console" in the demo.
- **Basis**: the 4 tactics match the literature — (1)(2) manual bots in BeCAPTCHA/Iliou 2021; (3) adjusted replay (ActReal 2026, preprint); (4) sampling from the human distribution (Serwadda & Phoha CCS 2013, BeCAPTCHA-Type "Universal"). GAN-generated bots get past touch-only detectors (~60%) → the reason for adding motion sensors.
- **Stating it at the right level in the pitch**: no paper has measured the rhythm/touch position of real Accessibility malware. The sentence "rhythm too even, tapping exactly at the button center" is **the team's hypothesis**, tested with the simulator, not a published result.

### 5.2 Model 2 — Is it the account owner? (few-shot)

**Version 1 — Compare against a template (done first)**
- Enroll 3–5 rounds → mean + variation of each feature.
- Score = **scaled Manhattan** (|x − mean| / standard deviation, summed) — the best of the 14 detectors in Killourhy & Maxion 2009 (EER 9.6%); Zheng 2014 also uses it.
- Easy to explain ("PIN 40% slower").
- **Realistic expectation**: papers reach EER 3–7% with dozens of enrollment rounds; 3–5 rounds in **one sitting** will be worse, and same-session results are twice as optimistic as cross-session (Buschek 2015). → Split enrollment across **≥ 2 sittings** where possible; measure and report the real numbers.

**Version 2 — Pairwise verifier**
- Learn one shared model: *"do these two sessions come from the same person?"*
- Input: feature differences between two sessions; label: same person / different person.
- ~25 people × 5 sessions → thousands of pairs.
- A new user needs only a few enrollment rounds (TypeNet: EER 10.7% with 1 round → 7.3% with 5 rounds on phones).
- **Leave-users-out evaluation is mandatory**: people in the test set have no pairs in the training set. 25 people is very small (TypeNet learns from >100k people) → only do it if version 1 runs well; if there is not enough time, drop it from the submission.

**Updating over time:** update the template only after a session that was allowed with a high match score **and** the correct PIN on a known device. That is not enough against "gradual teaching" (Biggio 2012; Lovisotto 2020: attack succeeds >70% with <10 injections) → add:
- **Drift cap**: each update moves the template by only a small amount (e.g. a moving average with factor 0.1), and the total deviation from the original enrollment template has a ceiling.
- **Drift direction check**: if many consecutive updates pull in the same direction → stop updating and flag it for operations (Lovisotto 2020: catches >99% after 2 injections).

### 5.3 Model 3 — Risk fusion

No real fraud data yet → use a weighted, explainable scoring function:

```
risk = w1·(1 − human_or_machine) + w2·(1 − owner_match)
     + w3·(new recipient) + w4·(amount unusual vs history)
```

- **Normalize before summing**: bring each score to [0,1] using z-score/tanh before applying weights — tanh tolerates outliers best (Jain, Nandakumar & Ross 2005).
- 3 zones: < A → `allow` · A–B → `step_up` · > B → `hold`.
- Choose thresholds that prioritize bothering the real owner as little as possible (e.g. FRR ≈ 5%), and report FAR at that threshold.
- **A, B are configurable** per partner: small threshold changes strongly affect both security and experience (Wiefling 2021, 780 people).
- **Basis**: this is a *risk-based authentication* model — LinkedIn: combining weighted signals raised AUC 0.913 → 0.955 (Freeman 2016); users find step-up on risk more pleasant than always-on 2FA (Wiefling 2020).
- **The team's own extension (state this in the pitch)**: the `hold` zone and the signals "new recipient / unusual amount" have no academic study to verify them (RBA studies use IP and browser; only vendor material such as BioCatch exists).
- Roadmap: replace with a supervised model once real data from partners is available (Wiefling 2022, 3.3 million users).

### 5.4 Explanation layer

- Take the 2–3 most deviating features (z-score for model 2, TreeSHAP for LightGBM in model 1) → a Vietnamese sentence from a template.
- With the fusion function in 5.3, each term `w·value` **is** its contribution → no SHAP needed.
- The LLM is used only in the dashboard to write case summaries for analysts.

### 5.5 Evaluation (done properly)

Basis: FETA (Georgiev 2022) reviewed 30 touch papers — **all** had at least one evaluation flaw; combining the flaws turns a real EER of 13.8% into 4.9%.

- **Time-based split**: enroll with earlier sessions, test with later sessions. No random split (a random split makes EER look better by ~3.8 points).
- **A single phone** for all participants (mixing device models flatters the numbers by 3.2–5.8 points).
- **Do not put impostor data into the training of model 2** (flatters the numbers by ~2.55 points; 80% of papers make this mistake).
- **Leave-users-out** for the pairwise model.
- Report both single-session level and combined-signal level.
- **Figures for the slides:**
  - FAR at FRR = 5% (**the main number** — ISO/IEC 19795-1 prefers error at a single operating point; EER only for comparison with papers)
  - EER + DET curve, with confidence intervals (25 people is few)
  - Error distribution per person (the mean hides "hard" people — Eberz 2017)
  - Bot catch rate per tactic
  - Accuracy by number of enrollment rounds (1 / 3 / 5)
  - API latency
- **Public datasets for comparison** (check licenses before use, record in the README): MobileTouchDB/BioTouchPass2 (217 people, 4-digit PIN, EER 2.38%), BB-MAS (117 people), BehavePassDB (81 people, 4 sessions), HuMIdb (600 people, with sensors — used for human/machine).

Full paper list: [docs/research/paper-report.md](../research/paper-report.md) · PDFs in [`papers/`](../../papers/).

---

## 6. Final demo script

| Step | Who | Purpose |
|---|---|---|
| 1. Enroll | Judge A does 3–5 trial transfer rounds (~20 seconds each) on the team's phone | Learn the personal rhythm |
| 2. Reveal the PIN | All 3 judges know the PIN (e.g. 159357) | Exactly the "PIN-knowing impostor" scenario |
| 3. Try | Judges B, C → then **A again** | Must see the real owner accepted and others asked for extra authentication |
| 4. Explain | The screen shows the score + reasons ("nhịp PIN chậm hơn 40%, chạm lệch phải, cuộn thẳng hơn", i.e. "PIN rhythm 40% slower, touch offset to the right, straighter scroll") | AI is the core + transparency |
| 5. Machine attack | The "hacker console" taps into the app by itself from another device | Simulates Accessibility malware → reports "not a real person" |
| 6. Dashboard | Open the operations dashboard, view the case summary, mark correct/incorrect | The "Future Workspace" angle |

Preparation: enroll and try in the same posture; set the threshold to lean toward `step_up` rather than blocking; have a backup video in case the venue network is poor.

---

## 7. Roles & plan — build in 1 day

### Roles (each person owns one part, responsible until submission)

| | **Member 1 — Data & ML** | **Member 2 — Backend & attack** (team leader) | **Member 3 — App & pitch** |
|---|---|---|---|
| Owns | Feature extraction, models 1 & 2, fusion function, explanation layer (reasons), evaluation numbers | Scoring API, DB, deploy, latency, template updates, **hacker simulator + hacker console** | Signal-collecting SDK, PIN keypad, demo wallet, enrollment/result screens, dashboard; slides, video, 1-page PDF |
| End-of-day output | `features.py`, `model1.pkl`, `score()` returning score + 2–3 reasons; preliminary results table | Online API with `/enroll`, `/score`, Swagger, demo API key; bot running all 4 tactics + 1 real attack source | Demo wallet running on the demo phone, end-to-end; 10-page slide skeleton |
| Answers judges (section 9) | Questions 1, 2, 3, 4 | Questions 5, 6, 8 | Question 7 + leads the whole demo |

**Done together, not assigned separately:** data collection; contest registration + sending questions to the organizers **before 23:59 27/11** (Member 2 — team leader).

### Build day (D-day)

| Time | Member 1 — Data & ML | Member 2 — Backend & attack | Member 3 — App & pitch |
|---|---|---|---|
| **08:00–09:00** | **Whole team**: fix the 2 data contracts — the session JSON the SDK sends (touch events: `t_down`, `t_up`, `x`, `y`, `w`, `h`, `key`) and the API response schema (section 3). Create the repo, deploy "hello world" for the API and frontend right from the start | | |
| **09:00–12:00** | Function extracting ~40 features from sample JSON; model 2 version 1 (scaled Manhattan) | FastAPI: receive sessions, save to DB, `/enroll`, `/score` (fake numbers first); deploy | Pointer Events SDK + custom-drawn PIN keypad; flow Home → Transfer → Enter account number → PIN |
| **12:00–13:00** | **Integration 1 + sitting 1 data collection**: 3 people × 5 sessions on **one demo phone** | | |
| **13:00–17:00** | Model 1 (Random Forest/LightGBM) on human sessions + bot sessions; fusion function (tanh normalization, weights); Vietnamese reason sentences from z-score | 4-tactic simulator → generate bot sessions for Member 1; **real attack source**: `adb shell input tap` from the laptop into the demo wallet; load the models into the API | Rhythm enrollment screen, result screen with reasons; table-style dashboard (suspicious sessions + reasons + correct/incorrect button) |
| **17:00** | ⚑ **Decision milestone**: if model 2 cannot separate the 3 people on the team → the pitch focuses on **"human or machine"**, with "is it the owner" as a secondary signal | | |
| **17:00–19:00** | **End-to-end integration 2 + sitting 2 data collection**: the team redoes 5 sessions each + 3–5 friends (with consent forms) + a round of "knows the PIN, impersonates the owner" | | |
| **19:00–21:00** | Evaluation: time-based split (sitting 1 enroll → sitting 2 test), FAR@FRR 5%, EER, bot catch rate per tactic | Template update with drift cap; measure latency; demo account; cost cap | Run the full flow on the demo phone, fix interface bugs; rehearse the demo script in section 6 |
| **21:00–23:00** | Put preliminary numbers into the slides | Draft README (libraries, AI tools, data sources, existing assets) | 10-page slide skeleton + 3-minute video script |

**Cut from the build day** (do later if time allows, does not affect the demo): pairwise model (version 2), LLM summary in the dashboard, accelerometer, drift direction check.

### After the build day (until 3/12)

| Milestone | Work |
|---|---|
| By 27/11 | Collect ~25 people × ≥ 2 sittings × 5 sessions in total; **contest registration + questions to the organizers before 23:59 27/11** |
| 28/11–1/12 | Re-evaluate on the full data (DET, confidence intervals, per-person error distribution); the cut items above if time allows |
| 2/12 | Feature freeze; load test, backup, always-on hosting |
| 3/12 | Final slides, video, 1-page PDF, source code zip. **Submit before 23:59** |

## 8. Risks & how to handle them

| Risk | Handling |
|---|---|
| 3–5 enrollment rounds are not enough to tell people apart | Measure early (1/3/5 rounds), split enrollment across ≥ 2 sittings, report the real numbers; 17:00 decision milestone on build day → shift focus to "human or machine" (do not rely on "being coached" — no study exists) |
| The "being coached" signal / a victim scammed over the phone | Only vendor material exists (BioCatch…) → present as an extension direction, not in the main figures |
| Judges nervous on stage → the real owner wrongly rejected | Enroll & try in the same posture; threshold leans toward `step_up` |
| A sophisticated bot (tactic 4) gets through | Acknowledge in the pitch; combine several signals; native SDK has extra device signals |
| Falsely good numbers from flawed evaluation | Time-based split, one device, report single-session level |
| Data law | Personal Data Protection Law (Luật BVDLCN) 2025 + Decree 356/2025 (effective 1/1/2026) classify biometrics as sensitive data → treat touch/swipe data as sensitive: ask for explicit consent, store only timing/coordinate features, do not store content, state it clearly in the README |
| Branding | Do not copy MoMo's interface/logo; use our own brand |
| Product down / out of credit before 11/12 | Always-on hosting, LLM cost cap, caching, monitoring |
| The question "MoMo already has this, doesn't it?" | Stress transparency, step-up, detection of machine-produced actions, open API form |

---

## 9. Questions judges may ask — prepare in advance

1. Where does the data come from, how many people, was there consent?
2. What are the EER / FAR / FRR, and how was it evaluated?
3. How many enrollment rounds are needed? What if the user changes phones?
4. What about a bot that replays a real person's actions?
5. Latency and cost per scoring call?
6. Why not let an LLM decide?
7. How is it different from MoMo's internal systems?
8. How is sensitive data handled under the new law?

---

## 10. Main references

**Contest**
- MoMo TechDay 2026 home page: https://techday.momo.vn/
- Problem statement: https://techday.momo.vn/topic.html
- Contest rules: https://techday.momo.vn/assets/docs/the-le-cuoc-thi.pdf

**MoMo background & malware**
- MoMo and the Ministry of Public Security cooperate against fraud with AI: https://www.momo.vn/tin-tuc/thong-bao/momo-va-bo-cong-an-dong-hop-tac-day-lui-lua-dao-8893
- Is MoMo safe (security layers): https://www.momo.vn/blog/momo-co-an-toan-khong-giai-dap-tu-a-z-thong-tin-c198dt2342
- Hanoi police warn about RedHook malware: https://dantri.com.vn/phap-luat/cong-an-ha-noi-canh-bao-2-ma-doc-co-the-tu-chuyen-tien-dien-ma-otp-20260826130439761.htm
- Malware that takes over Accessibility: https://m.tinnhanhchungkhoan.vn/cuoc-dua-ai-bao-ve-ngan-hang-so-post397114.html

**Behavioral biometrics**
- BioCatch — detecting scams through behavior: https://www.biocatch.com/detect-social-engineering-scam
- Touchalytics: https://arxiv.org/pdf/1207.6231
- FETA — mistakes in evaluating touch biometrics: https://ar5iv.labs.arxiv.org/html/2201.10606
- Authentication through PIN tapping rhythm: https://www.eecis.udel.edu/~hnw/paper/tapping.pdf
- Buschek et al. 2015 (spatial features when entering passwords): http://www.florian-alt.org/unibw/wp-content/publications/buschek2015chi.pdf
- Attack mimicking typing rhythm with AR: https://cs.uwaterloo.ca/~uhengart/publications/mobisys18.pdf
- KVC / Aalto dataset: https://arxiv.org/pdf/2311.06000v3

**Product model reference**
- MouseCat (YC W26): https://www.ycombinator.com/companies/mousecat

**Legal**
- Biometrics are sensitive data under the new law: https://thesaigontimes.vn/dung-dua-voi-du-lieu-sinh-trac-hoc-nguoi-dung/
