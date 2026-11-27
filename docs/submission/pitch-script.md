# Final pitch script and judge Q&A

> Use with `submission/Slide/Innate-slides.pdf` (10 pages). The slides **cannot be edited after submission**: adjust the spoken words, not the slides. Pitch length `[TODO: confirm with the organizers]`; the script below is ~5 minutes (~30 seconds per slide, slides 5–7 take longer).

## Spoken lines by slide

| # | Slide | Key points to say | Time |
|---|---|---|---|
| 1 | Title | "Innate: a human verification layer for e-wallets. In one sentence: a PIN can be stolen, but innate touch habits are very hard to steal." | 0:20 |
| 2 | Problem | Two scenarios: Accessibility malware that taps by itself, and someone who knows the PIN. "Every security layer says right owner. The missing question: who or what is touching the screen?" | 0:35 |
| 3 | Gap | A 5-layer security stack, Innate at layer 3. "Complementary, not a replacement; runs silently; a low score asks for more, it does not hard-block." | 0:30 |
| 4 | Solution | Enroll 3–5 times → three matches (human/machine, owner, replay) → allow/step_up/hold + reasons. "Like Face ID in workflow, but it is a risk signal." | 0:40 |
| 5 | Innate Challenge | When unsure, type a random Vietnamese phrase. Read the figure: 81% → 49% (measured on English phrases). **Stress:** "a clear improvement but not a gate; the Vietnamese tone-mark typing style is a hypothesis, not yet measured." | 0:45 |
| 6 | AI | Component table. "Classical machine learning, verified; with ~100 people, statistics and decision trees win. No LLM on the decision path." | 0:45 |
| 7 | Evidence | "Measured on real people, split by person. Naive bots are all caught; owner recognition is better but still a signal." State clearly: the bots come from the generator, not the team's own data. | 0:50 |
| 8 | Product | API + SDK + demo + dashboard. Invite the judges to try it themselves (link in the guide PDF). 4-step script. | 0:30 |
| 9 | Limits | **Say it before being asked:** human-like bots, weak owner recognition, posture change, web SDK, no real bots yet. "That is why `step_up` is in the design." | 0:40 |
| 10 | Impact | Users, partners, operations; roadmap; closing line "PIN is what you know. Innate is how you are." | 0:30 |

## Likely judge questions and honest answers

**1. Where does the data come from, how many people, was there consent?**
The current figures come from two public datasets: StrokePIN (97 people, 6-digit PIN on a phone, CC BY-NC-SA 4.0) and Aalto (2,260 people typing phrases). `[TODO: team data: number of people, number of sessions, consent forms]`. We store only timing, coordinates and event type, not content.

**2. What are the EER/FAR, and how is it evaluated?**
Owner recognition with 3 enrollment entries, PIN-knowing impostor: 38% of impostors get through at the point where 5% of owners are mistaken (contact size not used, measured on unseen people). Split by person, time-split, with confidence intervals and paired comparison. This is a risk signal, not a gate.

**3. Why not deep learning?**
The data is small. Statistical shrinkage toward the population alone cut impostors getting through by 17 points; deep models such as TypeNet need >100,000 people. We chose what runs, can be verified and can be explained.

**4. What if a bot replays a real person's interaction?**
There is a dedicated replay check: it catches 100% when the added noise is ≤ 10%, but only 29% at ±15% and 0% from ±20%. Measured on the whole system (E24, E27): replay with ±15–30% noise is let through 48–72%. The replay threshold can be raised (0.085 catches 86% at ±15%) but false blocks on the owner increase; we will settle it when the team has long histories. An adaptive attacker who adds enough noise will get through; then the session looks like a different person and only the (weak) "owner" score holds it back. This is a race, and we say so plainly.

**5. What about a bot that samples from the real-human distribution?**
Catches 20–73% depending on whether that bot type was seen in training. A bot that **knows the victim's template** gets through 75–82% (E27). We have no real bots to measure yet; that work is in progress.

**6. Does today's malware behave that way? (realism)**
Remote-control Accessibility malware has been widely reported. Whether its tap rhythm is even or not has **no published study measuring it directly**; that is our hypothesis, to be verified with the simulator and `adb`. We do not claim to have caught real malware.

**7. Why not let an LLM decide?**
Latency, consistency, auditability. An LLM (if any) only summarizes the case for the operations team and never sits on the decision path.

**8. How is this different from the wallet's internal system, or commercial solutions (BioCatch...)?**
We do not know the details of anyone's internal system. The differences we aim for: explainable reasons, `step_up` instead of hard blocking, separating human/machine from owner, and an open API format for any wallet. The direction has precedent in the industry (behavioral biometrics, risk-based authentication); we do not claim to have invented it.

**9. Latency and cost per scoring call?**
Measured locally (E26, network excluded): `/score` p50 3.7 ms, p99 14 ms; the model is a small decision tree (~180 KB). Not yet measured on Vercel/Neon: `[TODO: re-measure on the submitted build]`. There is no LLM call on the scoring path.

**10. What if the user changes phone or posture?**
A posture change nearly loses the signal (measured: EER 0.31, 71% of impostors get through). Hence: enroll in several postures, and a low score only leads to `step_up`. A phone change needs a controlled re-enrollment (design not finished).

**11. How is sensitive data handled under the new law?**
We treat touch/typing rhythm as sensitive data (Luật BVDLCN 2025, NĐ 356/2025 (the personal data protection law and its implementing decree)): collected only with consent, no PIN/amount/note content stored, stated in the README. Templates sit on the server, so they must be protected like biometric data.

**12. Does the Innate Challenge annoy users?**
It appears only when the system is unsure, takes ~10 seconds, and there is always an alternative path (OTP/face). **We have not measured real friction**, and the measured data is copying English phrases, not typing a random Vietnamese phrase under stress.

**13. Does the product run on a real phone yet?**
The demo wallet and web SDK run in a phone browser; a native SDK does not exist yet. `[TODO: update to reality at submission time]`.

**14. Why Vietnamese typing? Is there prior work?**
We searched and **did not find any published work** using Telex/VNI typing style as a biometric (that does not mean nobody has done it). The idea: the keys that transform tone marks and where tone marks are typed are personal habits that do not depend on the specific phrase, and a bot would have to imitate the input method too. So far there is only the design, a simulation and feature extraction code; **not yet measured on real Vietnamese people**.

**15. Why not use motion sensors (gyroscope, accelerometer)?**
Tried on StrokePIN (E23): motion gives EER 0.04, but that is device noise (one phone per person) and disappears entirely when posture changes; the data is only 5 Hz, so the jolt at touch cannot be checked. We treat it as a candidate for anti-bot ("is being held"), not a claim.

**16. Does the online version run the learned models yet?**
Yes: `/health` reports both models loaded, and the models run in pure Python so they do not depend on system libraries. The models fall back to rules on error. On real people (E29, 97 people), with learned models the PIN-knowing impostor is let through 22%, with models off 89%. This was measured in `research/`, not on the online version; the sessions in the demo are simulated. `[TODO: run backend/scripts/check_online.py at submission and before 11/12]`

**17. Why does the demo use a 6-digit PIN?**
The owner model learned on 6-digit PINs (StrokePIN), and with a 4-digit PIN the PIN-knowing impostor gets through clearly more often (E28: 68% vs 28% `allow`), so the demo uses the 6-digit PIN `159357`. The learned models are on in the online version; if they are off (error or switch), the system falls back to rules and is weaker, and we say so plainly.

## Principles when answering
State the limits **before** being asked; use "risk signal" and "very hard", not "impossible" or "catches all malware"; say clearly which figures are not the team's own data.
