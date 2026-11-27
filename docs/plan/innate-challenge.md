# Innate Challenge — type a phrase to prove "a real person, the right owner"

> **Updated 25/11/2026:** the design has moved to a **random lowercase Vietnamese phrase, letters only** (no longer a letters-and-digits string like the example "mua 4 ca phe 27" below), issued by `GET /v1/challenge` with a signed single-use token. The measurements here are on English sentences (Aalto). Current design, the Telex/VNI typing-style channel and risks: [`innate-challenge-vi.md`](innate-challenge-vi.md); how to reduce FAR (E22): `../research/ai-research.md`. This file is kept as the original document.

> Idea finalized 24/11/2026. Complements Innate's passive verification layer ([`positioning.md`](positioning.md)). Figures: [`../research/ai-research.md`](../research/ai-research.md), E13.

## The idea in one paragraph

By default Innate runs **passively**: the user just enters the PIN as usual and Innate scores the touch rhythm. When the system is **unsure** (low owner-match score, new recipient, large amount), instead of demanding an OTP or a face scan, it shows **a short system-generated random phrase of letters and digits** ("mua 4 ca phe 27", a buy-coffees phrase with digits) and the user **retypes exactly that phrase**, taking about 10 seconds. A phrase of 15–20 characters gives far more signal than 6 PIN taps, and because the system creates the phrase, it is **not the user's private data**.

```
Transaction ─► Innate passively scores (PIN)
              ├─ confident it is the owner, a human ─► allow
              ├─ clearly a machine ──────────────────► hold
              └─ NOT SURE ─► Innate Challenge: "retype this phrase"
                               └─ combine extra signal ─► allow / step_up (OTP, face) / hold
```

## Why it can do better

1. **More signal.** Typing rhythm, variability, error-correction habits over 20–30 keys.
2. **Hard to prefill.** A new phrase every time: no text for malware to set in advance; setting the whole phrase directly (`ACTION_SET_TEXT`) or pasting it whole is a sign of a machine, because a real person types key by key.
3. **Less friction than OTP/face** *(not measured)*: a familiar action, no app switching, no waiting for an SMS.
4. **Fits the "Human Centered" spirit:** asks for more **only when needed**, does not bother the user on every transaction, and the user can see clearly why they are being asked.

## Evidence (E13, real people typing sentences on phones, Aalto data)

Each sentence is cut at the first n keys (n = 6 ≈ the length of a 6-digit PIN). Only inter-key timing is used; enroll 3 sentences, and the **test sentence differs in content from the enrollment sentences** (exactly the random-phrase situation).

| Number of keys n | Owner recognition: EER | Owner recognition: FAR at FRR 5% | Catching evenly typing bots (AUC) | Catching population-sampling bots (AUC) |
|---|---|---|---|---|
| 6 | 0.364 | 0.807 | 0.915 | 0.719 |
| 10 | 0.337 | 0.733 | 0.969 | 0.764 |
| 20 | 0.279 | 0.591 | 0.996 | 0.848 |
| 30 | **0.245** | **0.489** | 0.995 | 0.891 |

**Hypothesis supported in direction:** more keys clearly improve owner recognition (EER 0.364 → 0.245; impostors getting through at FRR 5% from 81% down to 49%, confidence intervals not overlapping) and catch evenly typing bots almost perfectly from 20 keys.

## What was NOT proven (stated plainly)

- **The absolute numbers are still weak:** at 30 keys, EER is 24.5% and ~49% of impostors get through at FRR 5% (only 6 rhythm features, 3 enrollment sentences). The challenge phrase is **not magic**; it improves things but does not turn the "owner" score into a gate.
- **Not comparable with PIN:** the Aalto data has no key hold time and no coordinates, unlike the StrokePIN set. Combining PIN + challenge phrase has also **not been measured**.
- **The data is copying English sample sentences** on a phone (a typing-speed test), not typing a random letters-and-digits string when about to lose money: users are stressed, and typing an unfamiliar string is slow and differs from habit.
- **The bots in E13 are fake bots** from only two families; an attacker who knows the system can type fake keys with a human-like rhythm (see below).
- **Friction not measured** (time, abandonment rate, people with disabilities, voice keyboards).

## What the attacker does, and what Innate Challenge blocks

| Attacker | Blocked? | Notes |
|---|---|---|
| Sets the whole phrase directly (`ACTION_SET_TEXT`) | **Yes**, if a **native** SDK sees the text change without key events | The web SDK **cannot** see it: needs native (R1/R9) |
| Pastes the whole phrase | Yes, with the `challenge_pasted` flag | Need to disable selecting/copying the challenge text (draw it as an image/canvas) |
| Automatic key presses with even rhythm | Yes (AUC ~0.99 at ≥ 20 keys, for seen bots) | **Unseen** bots are still weak (E4b, E11) |
| Automatic key presses with a **rhythm sampled from real people** | **Weak** (AUC 0.72–0.89) | An adaptive attacker (ActReal 2026) can still fool it |
| Replaying the victim's recorded rhythm | **Not blocked yet** | A new phrase each time does not by itself block replaying the *timing*: the attacker types the right phrase with the recorded rhythm. The replay check (E5) needs extending to key-pair distance sequences |
| A bystander who knows the PIN | Partly | Improves owner recognition but weak (see above) |

**Checking "typed the right phrase" without storing the content:** the app compares the typed text with the displayed phrase on the device and sends a **salted hash** (or just a match/no-match flag) along with the key timings; the server knows the right phrase, so it can check without storing the text. This **assumes the app is not tampered with** (layer 1 in [`positioning.md`](positioning.md)).

## Challenge phrase design

- **Short, 12–20 characters, letters + digits, no tone marks.** Longer gives more signal (E13) but increases friction: needs measuring.
- **Random each time**, issued by the server with a single-use code (nonce), expiring after a few tens of seconds.
- **Turn off autocorrect, prediction and suggestions** in the input field (`autocorrect=off`, `autocomplete=off`, `spellcheck=false`) so typing rhythm is not disturbed.
- **Always have an alternative path** (OTP/face) for people who cannot type (disability, voice): Innate is never the only way to complete a transaction.

## Privacy

The phrase content is system-generated, so it is **not the user's personal data** (better than reading a free-text note field). Still only timing, event type, character count and character class are stored. Typing rhythm is sensitive biometric data: it needs explicit consent (Luật BVDLCN 2025, NĐ 356/2025).

## Implementation status

| Done (24/11) | Not yet |
|---|---|
| `SessionIn.fields` accepts a `challenge` field with `expected_len`; typing-rhythm features; rule: `set_text` or pasting the whole phrase = machine; 1 test | UI showing the phrase; phrase and nonce generator; hash check; native SDK; replay check on key sequences; **any real data in the challenge field** |

**Work needed to turn it into a product:** (1) collect real people typing random letter-and-digit phrases (team), (2) measure PIN + phrase combined, (3) measure friction, (4) replay check for key sequences, (5) native SDK for `set_text`.
