# How Innate works (explanation for the judges and for the team)

> Finalized 24/11/2026. Used as the basis for the slides, the video, and answers to the judges. Figures come from E9/E4b (public real-human data, not the team's data yet); see [`../research/ai-research.md`](../research/ai-research.md).

> Where Innate sits in the security stack and what it does not do: [`positioning.md`](positioning.md).

## The closing line

> **Like Face ID in how it enrolls and matches, but it is a risk signal, not a key.**
> A PIN can be stolen, inborn touch habits are very hard to steal. *(Say "very hard", not "impossible": see [`pitch-story.md`](pitch-story.md).)*

## Flow

```
First time (setup)   enter the PIN / a trial transfer 3–5 times  →  store your "habit template"
Each later use       enter as usual  →  compare with the template  →  match score
                                              + "human or machine" check
                     →  allow / require extra authentication (face, OTP) / hold the order
```

## Two different kinds of "training" (often confused)

| | General training | Enrollment of each user |
|---|---|---|
| When | Once, before the product ships | Each person, on first use |
| Data | Many people (StrokePIN, then the team's data) | 3–5 entries by that person |
| What is learned | "How people usually type", "what bots look like", the population distribution (prior) | **No separate model is trained**: only the mean and the spread of each feature are stored |

Because the end user has only 3–5 samples, this is a **few-shot** problem. Population knowledge (the prior) makes up for the few samples: E2 reduces the share of impostors who get through at the FRR 5% operating point by about 7–16 percentage points.

## Two questions, not one

| Question | Enrollment needed? | Who it catches | Confidence (current measurements) |
|---|---|---|---|
| **Human or machine?** | **No**: works from the first use | Malware, scripts, `adb` (scenario A) | Naive bot: caught 100% (E4b). Human-like bot: 5–73% |
| **Is it the owner?** | **Yes**: needs a template | Acquaintances, a thief who knows the PIN (scenario B) | EER 16–20% (E9) |

## Not like a fingerprint or a face

| | Fingerprint, face | PIN-entry habit |
|---|---|---|
| Nature | A body characteristic, nearly fixed | Behavior: changes with posture, mood, time |
| Accuracy | Very high | **EER ~16%**; at FRR 5%, **38–57%** of PIN-knowing impostors still get through (E9, E12b: 57% with basic distance, 38% with the learned model) |
| Changed conditions | Stable | **Sitting → walking: the signal is nearly lost** (EER 32–40%) |
| Where the template is stored | In the device's secure chip | **On the server** → must be protected like sensitive biometric data |

Consequence: Innate **does not replace** passwords or Face ID. A low match score **does not hard-block**; it requires stronger authentication. That is why `step_up` exists.

## How enrollment should be done (a little different from Face ID)

- **Several postures** (sitting, standing, walking) and **several different sittings**. E9 shows that enrolling only while sitting is not enough; Buschek 2015 shows that enrolling within a single session gives numbers twice as optimistic.
- The template **updates itself slowly** over time, with a **drift cap** so that an impostor cannot "teach" it gradually (E7: without the cap the impostor is accepted 100% and the owner is locked out).
- Store only **timing, coordinates, event type**; do not store the PIN content, the amount, or the transfer note.
- Also enroll the **input fields other than the PIN** (amount, recipient, note) if their typing rhythm is to be used as an owner signal.

## How to put it to the judges (safely)

| Say | Do not say |
|---|---|
| "Like Face ID in how it enrolls and matches, but **a risk signal**" | "Replaces Face ID / PIN", "as accurate as a fingerprint" |
| "Reliably catches naive bots from the very first use; the owner part needs a few enrollment rounds" | "Catches all malware" |
| "A low score means ask for more, not a hard block" | "Locks the account by itself" |
| Real measurements: EER 16–20%, stated before being asked | Promise an EER of a few percent as in papers |
