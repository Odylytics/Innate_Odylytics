# Technology research plan

> Drawn up 24/11/2026. Goal: answer the technical questions that could break the product or be used against us by the judges, in order of risk. Results go into [`tech-notes.md`](tech-notes.md).

## Scope (updated 24/11)

The team builds the web/demo separately later. The demo wallet (`backend/app/static/wallet.html`) and the API deploy (`nhip-api`) are **no longer being developed**; code is not deleted. R6 (infrastructure) and R8 (dashboard) are postponed. The focus is the AI core: see [`ai-research.md`](ai-research.md) (task A human/machine, task B account owner, task C fusion and explanation; experiments E1–E7).

## Principles

- A question whose **answer changes the design** goes first.
- Prefer experiments on the demo phone over more reading. External sources are for orientation only.
- Every question has a verifiable output and a deadline.

## Research questions

| # | Question | Why it matters | Method | Output | Deadline |
|---|---|---|---|---|---|
| R1 | Can the SDK **see a difference** between a real touch and a touch injected by `adb input` / `dispatchGesture`? (w/h, pointerType, time resolution, `getCoalescedEvents`, number of points between down and up) | If the difference is clear, "human or machine" has a hard signal beyond statistics. If not, only statistics remain | Record events on the demo wallet from 3 sources: a finger, `adb input tap/swipe`, a self-written `dispatchGesture` app. Compare field by field | Table of which fields differ, with numbers | 28/11 |
| R2 | Is the touch geometry field (`width`/`height`) usable on the demo phone? Does it return 1, 0, or a real value? | Touch size is one of the strong "owner" signals (Zheng 2014). A device that does not measure it returns 1 | Measure on real Android Chrome and iOS Safari | Decision to keep or drop `tap_w/h_*` | 26/11 |
| R3 | With ~25 people, does a learned model (LightGBM/RF) beat rules + Manhattan? How many enrollment sessions are needed? | "AI is the core" must hold in the submission, but data is scarce | Collect data, evaluate per FETA: time split, one device, leave-users-out | Table of FAR@FRR 5%, EER, DET, per-person distribution | 01/12 |
| R4 | A cheap and reliable way to detect replay (tactic 3)? | The current baseline catches 0% of tactic 3 | Distance to the same user's old sessions in feature space; threshold from real human data | Check in `/score` + test | 29/11 |
| R5 | What does the adaptive attacker (ActReal 2026) do, and what is left for Innate? Is adding `devicemotion`/IMU worth it? | The paper reports 71–77% success against a touch + IMU detector | Read ActReal closely; try `devicemotion` on the web demo; build tactic 5 if time allows | "Limitations" section in the slides + IMU decision | 30/11 |
| R6 | Infrastructure: is Vercel Python + Neon stable enough, latency < 200 ms, no "sleep" causing errors during judging? Free-tier limits? | The product must be online until 11/12 | Measure cold start, 100 consecutive requests, check plan limits, enable `/health` monitoring | Latency numbers + fallback plan | 02/12 |
| R7 | Legal side of data collection: the 2025 Personal Data Protection Law + Decree 356/2025 classify biometrics as sensitive | Disqualifying condition: personal data without a source and a legal basis | Draft a consent form, store only timing + coordinates, document in the README | Consent form + README paragraph | 27/11 |
| R8 | (Optional) Dashboard + LLM summary | The "Future Workspace" angle | Only after R1–R4 are done | Dashboard | after 01/12 |
| R9 | **Signals beyond the PIN**: typing the amount, account number/recipient name, transfer note. Is typing in these fields enough signal? How does a remote-control machine fill in a field (typing keys or setting text directly)? | A session gets dozens more keystrokes instead of 6 PIN taps, and this is where a bot is most exposed | Measure on a phone: real typing, paste, and filling with `ACTION_SET_TEXT` (Accessibility). Record `beforeinput`/`input`/`keydown` events on web, `TextWatcher` on native | Table of signals per field type + keep/drop decision for each field | 30/11 |

## Order of work

1. R2 and R7 (cheap, block data collection) → R1 (changes the design) → R4 (cheap fix, wins points back) → R3 (needs data) → R5 → R6.
2. Decision point: 17:00 on the first data-collection day. If the "account owner" model cannot separate the 3 team members, the pitch focuses on "human or machine".

## Done (24/11)

- Cross-checked the plan's numbers against the 7 original papers and read the abstracts of the remaining papers: [`../plan/mo-ta-du-an-va-kiem-chung.md`](../plan/mo-ta-du-an-va-kiem-chung.md).
- Initial search for R1, R2: see [`tech-notes.md`](tech-notes.md). **No conclusion yet** because public documents do not cover the defense side; experiments are needed.

## R6 infrastructure measurement (26/11)

100 sequential `GET /health` requests to `nhip-api-taupe.vercel.app` from the dev machine: min 0.16 s, p50 0.22 s, p95 0.48 s, max 1.27 s. Only `/health` was measured (no DB access, no `/score`); real cold start after idle time has not been measured, nor the free-tier limits. The R6 threshold of 200 ms is not met at p50, due to network latency from the dev machine.
