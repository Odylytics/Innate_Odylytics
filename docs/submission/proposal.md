# Innate — Idea Proposal

> MoMo Tech Contest 2026 · Theme: **Cybersecurity + Anti-fraud** · Brief: *Imagine the Future Workspace — Human Centered. AI Powered.*
> Synced 27/11/2026 with the final deck (`submission/Slide/Innate-slides.pdf`). Items marked `[TODO]` need the team to fill in. Every figure comes from [`../research/ai-research.md`](../research/ai-research.md) and `research/EXPERIMENTS.md` and can be rerun with the code in `research/`.

## 1. Summary

When a phone is taken over, or someone knows the PIN, the money leaves through the victim's own app, PIN and device, so every authentication layer reports "right owner". Even face, fingerprint and retina scans fall back to the PIN when they fail, so the PIN is the last gate. **Innate** is a **human verification layer** that runs silently at the transaction confirmation step: AI compares how the user touches and types against their enrolled habits and against a real-human pattern, to answer two questions before the money leaves: **is this interaction by a human or a machine? If a human, is it the account owner?** The result is `allow`, `step_up` (extra verification with the wallet's existing face or OTP) or `hold`, with a reason in plain words (Vietnamese or English). Innate does not replace the PIN, OTP or face check, and never locks an account by itself: it is a risk signal that makes the existing layers smarter.

## 2. Fit with the brief

| Contest requirement | Innate |
|---|---|
| **Human Centered** | Runs silently, adds no step for the owner; asks for more only when unsure; always has an alternative path; explains why the user is being asked; stores no private content |
| **AI Powered** | AI is the core: learned models (LightGBM) for human/machine and owner recognition, statistical shrinkage toward the population, replay detection. Not a side feature |
| **Future Workspace** | The operations team gets a list of suspicious sessions with easy-to-read reasons and marks right/wrong as labels for further learning: AI explains, humans decide |
| **Theme** | Cybersecurity (detecting automated interaction, tracing remote control) + Anti-fraud (challenging transactions made by someone else before money is lost) |
| **Usable online** | Phone app with live scoring (scan the QR), static demo wallet and guided story on a computer, scoring API (Swagger) and ops dashboard at https://innate.odylytics.com, online until 11/12/2026 |

## 3. Problem

- **Scenario A, remote-control malware:** the victim installs a fake APK and grants Accessibility permission; the malware reads the screen and OTP and taps through the transfer itself (families such as RemControl and ToxicPanda 2.0 were reported in 2025–2026).
- **Scenario B, a person holding the phone who knows the PIN:** an acquaintance, or a thief who watched the PIN.
- Traditional authentication checks things that **can be taken** (PIN, OTP, device); even a failed face or fingerprint scan falls back to the PIN. The question no layer answers: **who or what is touching the screen?**
- Scale of the prize: online scams caused over VND 8 trillion of losses in Vietnam in 2025 (Ministry of Public Security, as reported by the press; all scam types, not only PIN theft).

**Users:** e-wallet users (protected) and the anti-fraud operations team (supported with explained evidence).

## 4. Solution and what is novel

1. **A human verification layer at the transaction confirmation step**, complementing the existing layers (device, authentication, transaction risk). Position in the security stack: [`../plan/positioning.md`](../plan/positioning.md).
2. **Four kinds of evidence, one risk score:** PIN rhythm, transfer form (typed, pasted or set by a script), touch and swipe, and context (new recipient, unusual amount). Fused into one weighted score, not four gates in a row (four gates at 95% each would block nearly 1 in 5 genuine owners).
3. **Three 1:1 matches from the same interaction session:** human or machine (no enrollment needed), is it the owner (enrollment from the PIN taps users already make), replay of an old session. Fused into a decision `allow / step_up / hold` + reasons.
4. **A staged rollout for a wallet (our proposal, not yet piloted):** shadow mode (score every transfer, change nothing), then step-up when unsure, then hold for bot-like transfers; the threshold is tuned on the wallet's own data and friction is spent where loss per case is highest.
5. **Innate Challenge (a bet on top, not a claim):** when unsure, instead of an OTP or face scan, the system shows a random Vietnamese phrase (chosen by the server, signed single-use token) and the user retypes it (~10 seconds). More keys give more signal (measured on English phrases: owner-recognition EER 0.364 → 0.245 going from 6 to 30 keys; see [`../plan/innate-challenge.md`](../plan/innate-challenge.md)). Typing Vietnamese via Telex/VNI leaves additional traces that a replayed typing rhythm does not carry: **this is a hypothesis not yet measured on Vietnamese people** ([`../plan/innate-challenge-vi.md`](../plan/innate-challenge-vi.md)).
6. **Honest about capability:** the "owner" score is a risk signal, not a gate. The design is built around that (step_up instead of blocking, alternative path).

## 5. The AI underneath

| Component | Method |
|---|---|
| Features | Key hold/release time, tap offset from key center (normalized by key size), swipes, typing rhythm in input fields |
| Human or machine | "Naturalness" rules + **LightGBM** trained on real people + generated bots |
| Is it the owner | Enrollment template (mean, variability; timing variability is **shrunk toward the population** to compensate for few samples) + **LightGBM** learning weights on standardized deviations |
| Replay | Distance to the account's own 50 most recent sessions |
| Template safety | Slow update with a drift cap (against "gradual teaching") |
| Fusion, explanation | Weighted sum; sentence templates; **no LLM on the decision path** (latency, consistency, auditing) |

**Why classical machine learning, not deep learning:** with ~100 people, statistics and decision trees win (shrinkage toward the population alone cut impostors getting through by 17 points); deep models such as TypeNet are trained on >100,000 people. A TypeFormer fine-tuned on StrokePIN improved EER from 0.29 to 0.20 on 30 unseen people (one run, not in the API yet).

## 6. Evidence (public real-human data, not the team's own data yet)

| Task | Result |
|---|---|
| **Whole system** (E29, StrokePIN, 97 people, 5-fold cross-validation by person, models retrained per fold, known recipient) | Owner: 77% allow / 22% step_up / 1% hold. PIN-knowing impostor (a different phone, so an upper bound): 17% [15, 19] allow / 82% step_up / 1% hold; with the learned models off (rules only) the impostor is allowed 89%. Naive bots and replay ≤ ±10%: **100% hold**. Bot sampling the population: 2% allow / 63% step_up / 34% hold |
| **Adaptive bots** (E29) | Replay with ±15–30% noise: 27–56% allowed; a bot that knows the victim's template: 77–89% allowed. A stated limit |
| Owner recognition alone (E12b, StrokePIN, PIN-knowing impostor, 3 enrollment entries) | Machine learning cuts impostors getting through at FRR 5% from **55% to 32%**; EER 0.160 → 0.140 |
| Human/machine (unseen real people; generated bots) | Naive bot (even rhythm, timing noise): **100% caught**; a classifier alone catches only 12–26% of replays |
| Replay check (calibrated on real people, E5b) | Catches **100%** of replays with noise ≤ 10%, 28% at ±15%, 0% from ±20%; false alarm on the owner ~0.2% at 4 past sessions (extrapolated about 3% at 50 sessions; raising the threshold to 0.085 would catch 85% at ±15% but extrapolates to about 15%) |
| Innate Challenge (E13, 2,260 people typing English phrases) | Impostors getting through at FRR 5% from 81% to 49% going from 6 to 30 keys; Vietnamese not measured |
| Swipe rules (E19, 41 people, 20,896 strokes) | Uniform-velocity rule: 0 real-human strokes wrongly blocked; the old "straight" rule wrongly blocked 13% of sessions (replaced) |

## 7. Impact and business view

- **Expected loss = transfers × fraud rate × loss per case × share that gets through.** Innate attacks the last factor: against someone who knows the PIN it goes from 100% (a PIN check alone) to 17% in our test. That is an upper bound (different phone; a step-up is a challenge, not a guaranteed stop).
- **Cost side, friction:** about 23% of normal owner transfers (known recipient) are asked for more. The threshold trades friction against stopping impostors with no free optimum (E24, E31).
- **We have no wallet fraud rate or loss per case, so we state no revenue figure**; the wallet can plug its own numbers into the formula. Strategy: shadow mode first, tune on the wallet's own data, spend friction where loss per case is highest (new recipients, large amounts).
- **Users:** protected without extra steps; asked for more only when there are signs, with a reason.
- **Partners (wallets, banks):** SDK + one API call; configurable thresholds; complements the existing authentication layers.
- **Operations team:** fewer vague alerts, more evidence; right/wrong labels feed the model.

## 8. Risks and limits

- Human-like bots (replay with noise ≥ 15%, template-aware bots 77–89% allowed) and system-level adaptive attackers (ActReal 2026) can get through: Innate is **one layer** among many.
- Owners get asked too: 23% of known-recipient transfers get a step-up (face or OTP), and only 1% are held. Owner recognition alone is weak (~32% of PIN-knowing impostors get through at FRR 5%). Fix: tune threshold A on the wallet's own data, starting in shadow mode.
- The web SDK cannot see text set directly without key events and has no motion signal → a native SDK is needed.
- **Public data only and no real bots yet**; the current models are temporary. Our own consented collection through the phone app is ongoing and not used in any figure. Plan in section 9.
- The web demo wallet and the guided story are static (illustrative decisions); live scoring runs in the phone app.
- Privacy: the product stores only timing, coordinates, event type and character count; the research phone app also keeps name, email and a throwaway practice PIN with consent. Touch and typing data is sensitive under the Personal Data Protection Law (Luật BVDLCN 2025).

## 9. Plan to the final

| Milestone | Task |
|---|---|
| 27/11 | Register for the contest, send questions to the organizers |
| 28–30/11 | Collect real-human data with consent through the phone app (≥ 2 sittings, one phone) and real bots (`adb`, `dispatchGesture`) |
| 30/11–01/12 | Retrain (`train_human_model.py --export …`), calibrate thresholds, final figures if the data allows |
| 02/12 | Feature freeze, load test, README declaring assets |
| 03/12 | Submission (slides, guide and README cannot be edited afterwards) |
| 11/12 | Final (product continuously online) |

## 10. Contest-rules compliance

Existing assets, open-source libraries, AI tools and data sources are declared in the README: [`README.submission.md`](README.submission.md). StrokePIN data (CC BY-NC-SA 4.0) and derived products (models, priors) are released under the same license. No third-party logos or brand names are used in the product.
