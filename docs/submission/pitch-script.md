# Final pitch script and judge Q&A

> Use with `submission/Slide/Innate-slides.pdf` (10 pages, synced 27/11/2026 with the final deck). The slides **cannot be edited after submission**: adjust the spoken words, not the slides. Pitch length `[TODO: confirm with the organizers]`; the script below is ~5 minutes (~30 seconds per slide, slides 8 and 10 take longer). Page numbers below are the PDF page numbers; the section numbers on the slides (01 to 09) are one lower.

## Spoken lines by slide

| # | Slide | Key points to say | Time |
|---|---|---|---|
| 1 | Cover | "Innate: silent human verification for every transfer. A PIN can be stolen; innate touch habits are very hard to steal. Your behavior is your signature." | 0:20 |
| 2 | 01 Problem | Two scenarios: Accessibility malware that taps by itself (a fake APK reads the screen and the OTP), and someone who knows the PIN. "Even face, fingerprint and retina scans fall back to the PIN. Every check passes. None asks who is touching the screen." | 0:35 |
| 3 | 02 Solution | Read the chart: the same PIN typed by two real people has a different rhythm. Four kinds of evidence (PIN rhythm, transfer form, touch and swipe, context). "One risk score, not four gates in a row: four gates at 95% each would block nearly 1 in 5 genuine owners." | 0:40 |
| 4 | 03 How it works | Enter amount, tap the PIN, confirm, Innate scores (about 4 ms in tests, network excluded). Three outcomes: allow (the owner sees nothing), step_up (the wallet's existing face or OTP, or a typed phrase), hold (transfer paused, user alerted). Enrollment is the PIN taps users already make; bot detection needs no enrollment. | 0:40 |
| 5 | 04 What changes for the wallet | Walk the table row by row: malware is held, a PIN-knowing person is stepped up, the owner is allowed. Then the **proposed** rollout: shadow mode (score only), step-up, hold. Say it is our proposal and has not been piloted. | 0:40 |
| 6 | 05 Product | Two live paths: the phone app (scan the QR, sign up, set your rhythm, send money: live scoring) and the demo wallet plus story on a computer (**static**, illustrative decisions). Scoring API with Swagger and the ops dashboard. 81 automated tests. Invite the judges to try it. | 0:35 |
| 7 | 06 AI basis | Three checks: human or bot, the owner, a replay. Each has a published basis (BeCAPTCHA, Killourhy and Maxion, Lovisotto). Weighted risk score, `allow / step_up / hold`, a plain reason per signal. "Classical machine learning, verified. No LLM on the decision path." | 0:45 |
| 8 | 07 Evidence | "97 real people, split by person, models retrained per fold." Owner: 77% pass silently (caption on the slide: with a new recipient, 15% pass silently). PIN-knowing impostor: 83% held or asked (rules only: 89% allowed). Naive bots: 100% held. Bot sampling the population: 97% held or asked. State clearly: the bots come from our generator, and the impostor used a different phone. | 0:50 |
| 9 | 08 Limits and roadmap | **Say it before being asked:** bots that copy a rhythm pass 27 to 89%; owners get asked too (23% of known-recipient transfers; fix: tune threshold A on the wallet's own data, starting in shadow mode); the web SDK has blind spots; public data only. Each has a safety net today and a fix. "That is why `step_up` is in the design." Two bets on top: fine-tuned Transformer (one run) and the Innate Challenge. | 0:45 |
| 10 | 09 Impact | The formula: expected loss = transfers × fraud rate × loss per case × share that gets through. The prize (VND 8 trillion+ lost to online scams in Vietnam in 2025). What Innate changes: a PIN check alone lets 100% of PIN-knowing people through, Innate lets 17% through (upper bound). What it costs: 23% of normal owner transfers (known recipient) are asked for more. Strategy: shadow mode, tune on the wallet's own data, spend friction where loss per case is highest. Close: "PIN is what you know. Innate is how you are." | 0:50 |

## Likely judge questions and honest answers

**1. Where does the data come from, how many people, was there consent?**
The current figures come from two public datasets: StrokePIN (97 people, 6-digit PIN on a phone, CC BY-NC-SA 4.0) and Aalto (2,260 people typing phrases). Our own consented collection through the phone app is ongoing; no figure in the slides or the README uses it yet. We store only timing, coordinates and event type, not content. The research phone app also keeps name, email and a throwaway practice PIN, with consent.

**2. What are the EER/FAR, and how is it evaluated?**
Two levels. Owner recognition alone (E12b, 3 enrollment entries, PIN-knowing impostor): 32% of impostors get through at the point where 5% of owners are mistaken, measured on unseen people. The whole system (E29, 97 people, 5-fold cross-validation by person, models retrained per fold, confidence intervals): a PIN-knowing impostor is allowed 17% [15, 19] of the time, the owner 77%. This is a risk signal, not a gate.

**3. Why not deep learning?**
The data is small. Statistical shrinkage toward the population alone cut impostors getting through by 16 points; deep models such as TypeNet need >100,000 people. We chose what runs, can be verified and can be explained. A fine-tuned TypeFormer improved EER from 0.29 to 0.20 on 30 unseen people, but that is one run and it is not in the API.

**4. What if a bot replays a real person's interaction?**
There is a dedicated replay check: it catches 100% when the added noise is ≤ 10%, but only 28% at ±15% and 0% from ±20%. Measured on the whole system (E29): replay with ±15–30% noise is let through 27–56% of the time. The replay threshold can be raised (0.085 catches 85% at ±15%) but false holds on the owner grow with history length (extrapolated about 15% at 50 sessions, against about 3% at the current 0.07; measured only up to 4 past sessions, about 0.2% at 0.07); we will settle it when the team has long histories. An adaptive attacker who adds enough noise will get through; then the session looks like a different person and only the owner score holds it back. This is a race, and we say so plainly.

**5. What about a bot that samples from the real-human distribution?**
On the whole system (E29) it is held or asked 97% of the time. A bot that **knows the victim's template** gets through 77–89%. We have no real bots to measure yet; that work is in progress.

**6. Does today's malware behave that way? (realism)**
Remote-control Accessibility malware has been widely reported. Whether its tap rhythm is even or not has **no published study measuring it directly**; that is our hypothesis, to be verified with the simulator and `adb`. We do not claim to have caught real malware.

**7. Why not let an LLM decide?**
Latency, consistency, auditability. An LLM (if any) only summarizes the case for the operations team and never sits on the decision path.

**8. How is this different from the wallet's internal system, or commercial solutions (BioCatch...)?**
We do not know the details of anyone's internal system. The differences we aim for: explainable reasons, `step_up` instead of hard blocking, separating human/machine from owner, and an open API format for any wallet. The direction has precedent in the industry (behavioral biometrics, risk-based authentication); we do not claim to have invented it.

**9. Latency and cost per scoring call?**
Measured locally (E26, network excluded): `/score` p50 3.7 ms, p99 14 ms; the model is a small decision tree (~180 KB). Not yet measured on Vercel/Neon: `[TODO: re-measure on the submitted build]`. There is no LLM call on the scoring path.

**10. What if the user changes phone?**
A phone change needs a controlled re-enrollment (designed in `docs/plan/dang-ky-lai.md`, not built). Only an owner authenticated through the wallet's own channel (OTP or biometrics) may open a re-enrollment window, with a daily limit, and the old template stays until the new one has enough rounds. We never re-enroll just because a score is low: a low score may be an impostor.

**11. How is sensitive data handled under the new law?**
We treat touch/typing rhythm as sensitive data (Luật BVDLCN 2025, NĐ 356/2025 (the personal data protection law and its implementing decree)): collected only with consent, no real PIN, amount or note content stored by the product, stated in the README. Templates sit on the server, so they must be protected like biometric data.

**12. Does the Innate Challenge annoy users?**
It appears only when the system is unsure, takes ~10 seconds, and there is always an alternative path (OTP/face). **We have not measured real friction**, and the measured data is copying English phrases, not typing a random Vietnamese phrase under stress. On the slides it is a bet for later, not a claim.

**13. Does the product run on a real phone yet?**
Yes, in a phone browser: the phone app (`#/collect`, can be added to the home screen) scores transfers live. A native SDK does not exist yet. The web demo wallet and the guided story on a computer are static walkthroughs with illustrative decisions, and the slides say so.

**14. Why Vietnamese typing? Is there prior work?**
We searched and **did not find any published work** using Telex/VNI typing style as a biometric (that does not mean nobody has done it). The idea: the keys that transform tone marks and where tone marks are typed are personal habits that do not depend on the specific phrase, and a bot would have to imitate the input method too. So far there is only the design, a simulation and feature extraction code; **not yet measured on real Vietnamese people**.

**15. Why not use motion sensors (gyroscope, accelerometer)?**
Tried on StrokePIN (E23): motion gives EER 0.04, but that is device noise (one phone per person); the data is only 5 Hz, so the jolt at touch cannot be checked. We treat it as a candidate for anti-bot ("is being held"), not a claim.

**16. Does the online version run the learned models yet?**
Yes: `/health` reports both models loaded, and the models run in pure Python so they do not depend on system libraries. The models fall back to rules on error. On real people (E29, 97 people), with learned models the PIN-knowing impostor is let through 17%, with models off 89%. This was measured in `research/`, not on the online version. `[TODO: run backend/scripts/check_online.py at submission and before 11/12]`

**17. Why does the demo use a 6-digit PIN?**
The owner model learned on 6-digit PINs (StrokePIN), and with a 4-digit PIN the PIN-knowing impostor gets through clearly more often (E28: 68% vs 28% `allow`), so the demo uses the 6-digit PIN `159357`. If the learned models are off (error or switch), the system falls back to rules and is weaker, and we say so plainly.

**18. What is it worth to the wallet? How much fraud would you stop?**
We do not have the wallet's fraud rate or loss per case, so we state no revenue figure. We show the arithmetic instead: expected loss = transfers × fraud rate × loss per case × share that gets through. Innate attacks the last factor: against someone who knows the PIN it goes from 100% (a PIN check alone) to 17% in our test, which is an upper bound because the impostor used a different phone and a step-up is a challenge, not a guaranteed stop. The wallet can plug its own numbers into the formula. The VND 8 trillion+ figure is national losses from all online scams in 2025 (Ministry of Public Security, as reported), not only PIN theft.

**19. Does 23% extra friction not hurt conversion?**
That is the cost side and we show it on the last slide: about 23% of normal owner transfers (known recipient) are asked for more (22% step-up, 1% hold). The step-up reuses the face or OTP the wallet already has, and tuning the threshold trades friction against stopping impostors with no free optimum (E24, E31). So our proposal is staged: shadow mode first (score only, change nothing), tune on the wallet's own data, then spend step-ups where loss per case is highest, for example new recipients and large amounts.

**20. Why not rely on face, fingerprint or retina scans?**
They are strong, but they fail sometimes (wet fingers, glasses, a mask, a damaged sensor) and the phone then falls back to the PIN. So the PIN is the last gate, and anyone who knows it gets in. Innate adds the touch as a second signature at that gate, and the owner does nothing new. We do not replace biometrics; we cover the fallback.

## Principles when answering
State the limits **before** being asked; use "risk signal" and "very hard", not "impossible" or "catches all malware"; say clearly which figures are not the team's own data, which are upper bounds, and which parts of the demo are static.
