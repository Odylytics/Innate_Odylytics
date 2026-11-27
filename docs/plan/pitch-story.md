# Innate — pitch story

> **A PIN can be stolen. Inborn touch habits are very hard to steal.**
> Updated 24/11/2026. For the slides (≤ 10 pages), the video (≤ 3 minutes), and the final presentation.

> Product positioning (what kind of layer Innate is, where it sits in the security stack): [`positioning.md`](positioning.md).

## Main idea

Every traditional authentication factor is something that can be **taken away**: a PIN can be shoulder-surfed, an OTP can be read, a device can be seized. Malware such as RemControl and ToxicPanda 2.0 (2026) abuses the Accessibility permission to tap a transfer by itself, using the victim's own app, PIN, and device. But **how a person touches**: how long a key is held, which way the touch is off-center on the button, whether a swipe is fast or slow, is a motor habit formed from childhood, and there is no file to copy.

Innate measures exactly that, and answers only two questions at the transaction confirmation step:

| Question | Who it catches |
|---|---|
| Is this interaction by a **human** or a **machine**? | Malware, scripts, `adb` (scenario A) |
| If human, is it the account **owner**? | Acquaintances, a thief who knows the PIN (scenario B) |

The result is `allow`, `step_up` (extra authentication) or `hold` (hold the order), with a reason in Vietnamese. The system recommends; it does not lock accounts by itself.

## Story flow (7 beats)

1. **Open with a story.** The victim installs a fake APK and grants the Accessibility permission. A few minutes later money leaves using their own PIN. Every security layer says "correct owner".
2. **Point out the gap.** Everything we check is something an attacker can obtain.
3. **Change the angle.** There is one thing they cannot obtain easily: how you touch.
4. **Show the academic evidence.** Rhythm and touch position when entering a PIN can tell one person from another (Zheng 2014: EER 3.65–7%; Buschek 2015: adding touch position cuts errors by 26–37%).
5. **Live demo (section 6 of the plan).** Judge A enrolls. Judge B knows the PIN but is asked for extra authentication. The hacker console taps automatically and is labeled "not a real person".
6. **Transparency.** The screen shows the reason: "nhịp PIN chậm hơn 40%, chạm lệch phải" (PIN rhythm 40% slower, touch off to the right). This is what sets it apart from a black box.
7. **Be honest about limits, then close.** Innate is one signal among many layers, measured with a strict evaluation protocol, open through an API to any wallet.

## Slogan

- EN: *PIN is what you know. Innate is how you are.*
- VI: *Mật khẩu có thể bị lộ. Cách bạn chạm thì không dễ bị đánh cắp.* (A password can be exposed. How you touch is not easy to steal.)

## Keeping the story standing (important)

The judges are a CTO and a Head of AI. "Inborn" is a good way to tell it, but the evidence shows touch habits are **hard** to steal, not **impossible**. Overclaiming will be challenged at once.

| Say | Do not say |
|---|---|
| "**Very hard** to steal", "there is no file to copy" | "Impossible to forge", "absolutely accurate" |
| "One **signal** among many layers, used to trigger extra authentication" | "Replaces OTP / PIN" |
| "Catches naive bots well; adaptive bots are a research direction" | "Catches all malware" |

**Evidence to have ready when asked:**
- Imitation attacks (a person deliberately mimicking) raise EER to 10–15% (BioTouchPass2, 2020). So partial imitation is possible.
- Practice makes attackers better: FAR from 0.24 to 0.63 after practice (Tey 2013, a secondary source in the paper report; the original could not be downloaded).
- System-level adaptive malware fools touch + IMU detectors 71–77% of the time (ActReal 2026, preprint).
- The Touchalytics authors themselves conclude that touch alone is not enough as standalone authentication.
- The team's numbers will differ from papers because of 3 stricter evaluation choices (split by time, one device, no impostor data in training), following FETA 2022. Say this **before** being asked.

**How to turn the weakness into a strength:** "We do not promise an impostor can never imitate it. We make that **much more expensive**, and when in doubt we ask for more instead of hard-blocking."

## Mapping to the judging criteria

| Criterion | Innate's answer |
|---|---|
| Creativity | Moves the authentication axis from "what you have/know" to "how you act"; separates bot from owner |
| Quality, completeness | Online, demo wallet + API + Swagger; measured with the FETA protocol, FAR@FRR reported with confidence intervals |
| Impact potential | Open API for wallets/banks, addressing the growing Accessibility threat |

## Suggested 10-slide outline

1. Victim story + slogan
2. The problem: two scenarios A (malware) and B (knows the PIN)
3. Why current authentication falls short (everything can be taken)
4. The idea: how you touch
5. What Innate does: two questions, three actions
6. Architecture and AI (human/machine, owner, fusion, explanation)
7. Demo (screenshots + product QR)
8. Real measurements and how they were taken
9. Honest limits and ways to extend
10. Impact and roadmap (API for partners)
