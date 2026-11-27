# What Innate is in the cybersecurity picture

> Finalized 24/11/2026. This is the **positioning** document (where Innate sits, what it does and does not do). Mechanism explained in: [`how-it-works.md`](how-it-works.md). Pitch story: [`pitch-story.md`](pitch-story.md).

## In one sentence

> **Innate is a human verification layer that runs silently at the transaction confirmation step: AI matches the current interaction against the enrolled habit and against the pattern of real people, to answer "is this a human or a machine, and is it the owner", before the money leaves.**

It is a **passive behavioral security** layer. It does not replace any existing layer; it adds what the others lack: **evidence that the one operating the device is a human, and the right owner**.

## Why this layer is needed

Every traditional authentication layer checks something that **can be taken away**: the PIN (shoulder surfing), the OTP (can be read), the device (can be seized). Accessibility malware (a technique MITRE ATT&CK for Mobile files under **Input Injection, T1516**) makes everything look right: the right app, the right PIN, the right device, the right open session. The question no layer answers: **who or what is touching the screen?**

## Where Innate sits in the security stack

```
┌─ 1. Device/app integrity         (attestation, anti-root/hook, malware scanning)   "is this device clean?"
├─ 2. Authentication               (PIN, OTP, face, fingerprint)                      "what does this person know/have/are?"
├─ 3. ★ INNATE: human verification (touch/typing behavior, runs silently)             "is this interaction by a HUMAN or a MACHINE?
│        AI matches against enrolled habit + real-human pattern                        Is it the OWNER?"
├─ 4. Transaction risk             (amount, recipient, history, network)               "is this transaction unusual?"
└─ 5. Operations & response        (dashboard, extra authentication, hold, investigation)
```

- **Complements, does not replace.** Layer 1 (attestation) answers "has the device been tampered with"; Innate answers "is the one on the device a real person and the right owner". Sufficiently sophisticated malware may pass layer 1; its interactions still leave behavioral traces. Conversely, someone standing next to the owner who knows the PIN passes every device layer but lacks the owner's habits.
- **API side:** the partner (wallet, bank) embeds the SDK that collects signals and calls a scoring API. The output is a score and a suggested action, not the final decision: the partner keeps the decision.

## Names in the industry (so judges can place it quickly)

Innate belongs to the group that industry literature calls **behavioral biometrics / continuous authentication / risk-based authentication (RBA)**, combined with **human-vs-bot detection** (automation detection). In product language: *human verification at the confirmation step*. Note: "HUMAN Security" is the name of a company; **do not use that phrase as a name or slogan**, only "human verification".

## What the AI underneath does: matching

Two matchings, both **1:1 verification** (against one specific template), not 1:N identification:

| Matching | What is compared to what | Enrollment needed? | Result |
|---|---|---|---|
| **Human or machine** | Current interaction ↔ "real human" pattern learned from many people (and bots) | No | "Is human" score |
| **Is it the owner** | Current interaction ↔ **the owner's own habit template** (3–5 enrollment rounds) | Yes | Owner-match score |
| **Replay** | Current interaction ↔ **the account's own earlier sessions** (unusual duplication) | No | "Replay" flag |

Fusion: human/machine score + owner-match score + context (new recipient, unusual amount) → `allow` / `step_up` / `hold` + a reason in Vietnamese. Technical detail and measurements: [`../research/ai-research.md`](../research/ai-research.md).

## Two scenarios blocked

| | A. Remotely controlled malware | B. Person holding the device who knows the PIN |
|---|---|---|
| Why it slips past other layers | PIN/OTP/device are all correct | Same |
| What Innate sees | An interaction that is **not a human finger**: rhythm too even, dead-center on buttons, text set directly without keys, replay | A human interaction that **does not match the owner's habit** |
| Current confidence | Naive bot: caught 100%. Human-like bot: weak (see limits) | Weaker: EER 16–20% |

## What Innate does NOT do

- **It does not detect malware** (no app scanning, no reading system logs); it only sees malware's **effect** on how touches look.
- **It does not replace PIN, OTP, face**: a low score means **ask for more**, never a hard block, and it never locks an account by itself.
- **It does not read content**: only timing, coordinates, event type, character count; it does not store the PIN, the amount, or the transfer note.
- **It does not detect scams by content** (messages, calls); that is another layer's job.

## Limits that must be stated plainly (public real-human data; not the team's data yet)

- "Owner" score: **EER ~14–16%; at FRR 5%, 32–55% of PIN-knowing impostors still get through** (E9, E10b, E12b: 55% basic distance, 32% learned model). This is a **risk signal, not an authentication gate**.
- Human-like bots (replay tactics, population sampling) are caught weakly; a system-level adaptive attacker can fool both touch and sensors (Wang 2026, ActReal: 71–77%).
- **Whole-system measurement (E24, E27, 10 people never seen by the learned model):** owners pass 81%, naive bots and replay with noise ≤ ±10% are held 100%; but replay with ±15–30% noise and bots that know the victim's template are let through 44–86% of the time. A 4-digit PIN (web demo) stops the learned owner model from running (E28).
- The web SDK cannot see text set directly without keys; a native SDK is needed.
- No real bot (`adb`, `dispatchGesture`) yet and no team data in any measurement.

## How to put it to the judges

| Say | Do not say |
|---|---|
| "A **human verification layer** running silently, complementing PIN/OTP/face" | "Replaces authentication", "stops all malware" |
| "AI **matches** the interaction against the owner's habit and against the real-human pattern" | "AI recognizes who you are" (1:N identification) |
| "Reliably catches naive bots; the owner part is a risk signal, a low score means ask for more" | "As accurate as a fingerprint" |
| State real measurements and limits before being asked | Promise an EER of a few percent as in papers |
