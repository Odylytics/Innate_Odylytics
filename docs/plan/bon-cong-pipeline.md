# Innate with 4 evidence channels: motion, PIN, typed phrase, touch area/swipe

> 25/11/2026. Answers the question "if we combine 4 gates, will the AI catch bots?". Numbers: [`../research/ai-research.md`](../research/ai-research.md) (E19, E22, E23).
> **26/11/2026: added section 7 "New flow" at the end of the file** (two layers: human/machine, then person/person; 4 scenarios iPhone/Android × remote takeover/stolen phone; phone tilt while tapping; PIN entered first, scoring at the transfer step). Section 7 is a **design, not implemented and not measured**; sections 1–6 are the 25/11 version.

## Short answer
**Yes, worth doing, but as fusion of 4 evidence channels, not 4 sequential gates that must all be passed.** If each gate wrongly blocks the owner 5% of the time and all 4 must be passed, the owner is wrongly blocked ~18.5% of the time (1 − 0.95⁴). The right way: all 4 channels feed scores into `fusion.py`; only when unsure is a typed phrase requested (channel 3); the result is still `allow | step_up | hold`.

```
Runs in background:   (1) motion  +  (2) PIN entry  +  (4) touch/swipe   ->  risk fusion
                                          sure it is the owner/a human ──► allow
                                          clearly a machine ───────────► hold
                                          unsure ─► (3) type phrase ─► fuse again ─► allow | step_up | hold
```
The strength of the idea: an attacker must fake touch, shaking, PIN rhythm, typing rhythm and tone mark typing style **at the same time**, and these signals must **line up in time with each other**. Each channel alone can be faked (the ActReal paper fakes even the motion sensors); cross-matching between channels is harder. None of the team's experiments has measured that difficulty.

## Each channel: what exists, evidence, limits
| Channel | Used for | Team's evidence | Limits, stated plainly |
|---|---|---|---|
| **1. Motion** (accelerometer, gyroscope, gravity) | Bot: phone lying still on a table, no hand holding it; owner recognition: how it is held | **E23 (StrokePIN):** motion alone gives EER 0.04–0.07 and FAR 3–10% in the same posture (PIN timing + offsets: EER 0.17–0.20, FAR 69–75%). **Changing posture (sitting → walking): EER 0.44–0.48, equal to guessing.** | **The E23 numbers are optimistic because of the device:** each person has one phone with a different sensor bias, so part of it is recognizing the device, not the person. Someone holding the victim's own phone would not be caught this way. StrokePIN only has accelerometer/gyroscope at ~5 Hz, so it **cannot measure the jolt of a tap**. Literature: HMOG 25.7–34.2% (touch only) → 7–10% (with motion added); BeCAPTCHA ~60% → 80–90%; **ActReal: a system-level agent can fake even the sensors, with 71.1% success against a touch + motion detector.** Web: `DeviceMotion` needs HTTPS and asks for permission on iOS Safari, at most ~60 Hz. |
| **2. PIN entry** | Owner recognition, human/machine, replay | Already built: EER 0.16, FAR 37.5% (machine learning), naive bot 100%, replay ≤ ±10% 100% | Loses signal when posture changes; a PIN-knowing impostor gets through often. |
| **3. Typed phrase** | Extra signal when unsure; Vietnamese tone mark typing style | **E22:** FAR 43–52% at 30 keys (learned model 43%); even-typing bot AUC 0.996 | Vietnamese typing style not yet measured on real people (waiting for tests on phones). |
| **4. Touch area / swipe** | Bot (constant-velocity swipe) | **E19:** the constant-velocity rule catches 100% of constant-swipe bots, 0/20,896 real human strokes wrongly blocked | Swipe **cannot** recognize the owner (AUC ~0.5); touch area size is device noise (E12b). Channel 4 is an anti-bot gate, not an owner-recognition gate. |

## The phrase "tôi tên là nguyễn minh quân" ("my name is Nguyen Minh Quan") or a random phrase?
| | User's fixed phrase | Random phrase issued by the server (being built) |
|---|---|---|
| Pros | Enrollment and trial use the same phrase: same content compared, better signal; many diacritics (ô, ê, ễ, â) for the Vietnamese typing style channel | Prevents **content** replay; the server knows the phrase without storing content; not personal data |
| Cons | **It is the user's name: personal data**; a shoulder surfer knows the phrase; someone who records the typing rhythm replays it verbatim; the server does not know the phrase so it cannot check "typed correctly" (only a salted hash comparison) | The phrase changes each time, so per-key-pair rhythm is hard to compare (E21b) |
Suggestion: keep the random phrase as the anti-bot/anti-replay gate; a fixed phrase is only a later add-on option (user chooses it, with separate consent), not built.

## Is the bot caught?
- **Naive bot** (script, `adb`, basic malware): yes, the touch/swipe and PIN channels already catch ~100%; the motion channel adds "no hand holding it".
- **Smart bot** (samples from the population, fakes sensors): **not guaranteed**. This is a known limit (E4b: 20–73%; ActReal). The only advantage of fusion is that it forces the attacker to fake several channels consistently.
- **Independent multiplies, correlated does not:** if the 4 channels were independent, FAR could multiply (e.g. 37.5% × 43% ≈ 16%), but with the same posture, the same device and the same session they are **correlated**; do not multiply before measuring.

## Next work (by value)
1. **Test an `adb` bot on a phone lying still on a table vs a person holding the phone:** measure motion vibration. Cheap, and decides whether channel 1 is really an anti-bot gate. Needs ≥ 100 Hz (native Android) or ≥ 50 Hz (web, if the device allows).
2. **Collect team data with motion**, each person entering the PIN + typing a phrase, the same device for both the owner and the "impostor" (a second person holding the owner's phone) to separate out device noise.
3. **Check alignment between touch time and IMU jolt** (needs a high sampling rate).
4. `imu_*` features in `features.py`: **not written**; write them once there is same-device data.

## 7. New flow (26/11/2026, design, not implemented, not measured)

### 7.1 Two scoring layers
1. **Layer 1, human or machine** (no enrollment needed): rules + optional LightGBM + replay check (`human.py`, `human_model.py`, `replay.py`). Already built. The online version has had the learned models on since 26/11 (`/health`: `human:true, owner:true`; before that it fell back to rules because lightgbm could not load on Vercel).
2. **Layer 2, person vs person** (needs enrollment): compare the action with the owner's template (`owner.py`, optional `owner_model.py`). Already built; it is only a **risk signal, not a gate** (a PIN-knowing impostor gets through 38–57% at FRR 5%).
3. Fusion in `fusion.py`, then `allow | step_up | hold`. Layer 2 only leads to `step_up`, never blocks on its own.

### 7.2 Four scenarios
| | Remote takeover | Stolen phone |
|---|---|---|
| **Android** | Accessibility malware injects taps. **Layer 1 is the main layer**; add the phone tilt channel (7.3). | The thief is a person who may know the PIN. **Layer 2 is the main layer**; the impostor uses the owner's own device (no device noise as in the StrokePIN data). |
| **iPhone** | **Out of scope.** The team's assessment: iOS has no Accessibility equivalent for injecting taps; in the "victim types by following the scammer's instructions" case the person typing is the real owner, Innate cannot catch it, and only context remains (new recipient, amount). Not verified against documentation. | Same as Android; the web SDK has not checked touch size on iOS. |

The owner template is tied to each device: changing device or posture requires a controlled re-enrollment (`dang-ky-lai.md`, not implemented). There are no measurements split by iPhone/Android yet.

### 7.3 Phone tilt while tapping (protects remotely taken over Android)
- **Idea:** malware injects taps through software, and the phone is usually lying still (e.g. 2 a.m. on a table); a person holding the phone has a tilt angle within a familiar range and a slight shake coinciding with each tap.
- **Proposed features:** mean tilt angle during PIN entry (gravity vector), deviation of the angle during entry, acceleration amplitude around each `t_down`/`t_up`, correlation between acceleration peaks and tap times.
- **Put in layer 1 (anti-bot), not used for owner recognition.** E23 gives EER 0.04 but that is device noise and disappears entirely when posture changes; repo convention: do not claim IMU owner recognition.
- **Limits stated up front:** if the victim is holding the phone when the malware taps, the signal weakens; malware with Accessibility can read and replay sensors (ActReal 71–77%), so it is only additional evidence; web `DeviceMotion` limits frequency and permissions, so the official version needs a native Android SDK; sensor data needs additional consent (Personal Data Protection Law (Luật BVDLCN) 2025); StrokePIN is only ~5 Hz so there is **no data yet to measure this idea**.
- **Work:** (1) add sensor reading at ≥ 50 Hz to `#/collect` on Android, with two conditions (held in hand and lying on a table), and update the consent form; (2) run an `adb`/`dispatchGesture` bot on a real Android phone to get "still phone with injected taps" samples; (3) measure whether the two groups separate, and only then write `imu_*` into `features.py`.

### 7.4 PIN entered first, scoring at the transfer step
**The team's idea:** the PIN is entered when opening the wallet/logging in, **with no blocking there**; a thief can just enter the PIN, and only at the transfer step does Innate start to tell bots, thieves and real people apart. Fits the rule "never lock accounts on its own".

Proposed design:
- **Still record the PIN at login, but in passive mode** (only time, coordinates, key label as now), attached to the later transaction session. No scoring to block at this step.
- **Score once at transfer confirmation**, combining: the recorded PIN rhythm + actions at the transfer step (typing the account number, choosing the bank, entering the amount, swiping to confirm) + motion (7.3) + context (new recipient, unusual amount). Only when unsure is a typed phrase requested (channel 3).

Things to account for in advance, because moving the PIN entry changes the evidence:
1. **The strongest evidence is lost at the decision point.** Owner recognition now relies almost entirely on PIN rhythm (the same 6 digits repeated every time). The account number changes with each recipient so it is weak (E14: only additional evidence), and swipe cannot recognize the owner (AUC ~0.5). So person/person evidence at the transfer step is mostly still the PIN recorded earlier.
2. **The gap "owner unlocks then hands over the phone" (or the phone is snatched after unlocking):** the PIN has the owner's rhythm, but the person transferring is someone else. This needs a check for the **same person throughout the session**, comparing tap rhythm at the transfer step with the PIN rhythm in the same session. This is a hypothesis, with no experiment yet.
3. **Malware may not need to enter the PIN** if it hijacks an already open session; then the PIN evidence is empty and only the transfer step + motion remain, so the `missing_pin_evidence` rule needs to be reconsidered (currently only a reason, see `api.ts`).
4. **Old numbers (E24–E28) were measured with the PIN right at confirmation.** When the PIN is separated from the confirmation step, these numbers no longer apply as is and must be re-measured.
5. **Impact on code and demo:** the `SessionIn` schema currently groups `pin_taps`, `fields`, `swipes` into one session; two sessions (login and transfer) need to be linked, or a field added. **Update 26/11: the demo wallet (`Wallet.tsx`) has switched to PIN-first** (opening the wallet with a PIN that is only recorded, scoring at transfer confirmation, one session carrying both); the video script and the PDF guide need to match this order. Not yet done: re-measuring E24–E29 under the new order and linking the two sessions in the API.

### 7.5 Next work (by value)
1. Settle with the team: does PIN-first replace the demo and video flow, or is it only a design description (impact in 7.4 item 5).
2. Collect Android data with motion (7.3), with a second person holding the owner's phone as the "impostor".
3. An experiment checking the same person throughout the session (7.4 item 2) on team data when available.

### 7.6 Decision after scoring (proposal for the wallet; thresholds are the wallet's decision)
Innate only **recommends**, and never locks accounts on its own.

| Level | When | Suggested action |
|---|---|---|
| **allow** | Sure it is a human, matches the owner, normal context | Let it through, no extra step. Update the owner template only when sure (keep the drift cap). |
| **step_up** | A human but does not match the owner, or unusual context (new recipient, large amount) | **Type one phrase** (Innate Challenge, ~10 seconds); if still unsure, face or OTP. A short delay with a notification to the owner can be added. |
| **hold** | Clearly a machine, or very high risk | **Suspend the order**, notify the owner through another channel, the owner can release the order, with a **hold deadline** so the order does not hang forever, and pass it to the operations team to review the reasons. The account is not locked. |

Accompanying actions (not visible to the user): freeze the owner template when suspicious (`owner.update`, not yet exposed in the API); the operations team labels fraud/legit as training data.

By scenario: remotely taken over Android leans toward `hold` (the human/machine layer catches it); a stolen phone leans toward `step_up` (the person/person layer is only a risk signal, do not `hold` just because the owner score is low). The thresholds `NHIP_THRESHOLD_A/B` are not yet calibrated on real data; the trade-off between bothering the owner and blocking the impostor has no free optimum (E24).

**The phrase at the `step_up` step:**

| | Fixed phrase (e.g. "tôi là Nghĩa", "I am Nghia") | Random phrase issued by the server |
|---|---|---|
| Person vs person comparison | Better: enrollment and trial use the same phrase | Harder to compare: the phrase changes each time (E21b) |
| Replay resistance | Weak: someone who records the typing rhythm replays it verbatim | Good |
| Personal data | Yes if the real name is used | No |
| Thief can guess the phrase | Possibly (knows the owner's name) | No |

Decision: **random phrase by default** (anti-bot and anti-replay gate). **A fixed phrase is only a later add-on**, where the user chooses any phrase (not a name) with separate consent; not built. Typing a phrase is **not a gate**: at 30 keys an impostor still gets through 43–52% (E22); the result goes back to `fusion` as additional evidence, and only when the typing is wrong or there is no tone mark typing action does it escalate to face/OTP. A fixed phrase has not been measured.

### 7.7 For the pitch: what is collected to analyze person vs person
**Collected** (behavioral metadata only): press/release time of each key (hold time, gap); touch position and offset from the key center; rhythm of entering the account number and the challenge phrase (only time, key type, length); context (new recipient, amount). Planned, not done: tilt angle and phone shake while tapping (needs separate consent).

**Not collected:** the content of the real PIN, amount, account number, content of the typed phrase, contacts, photos, voice, location. Exception: the research data collection page `#/collect` stores the trial PIN that the volunteer sets themselves (with a warning not to use a real PIN), and it is not put into the product SDK.

**Deliberately not used:** touch area size (device noise, E12b) and swipe for owner recognition (AUC ~0.5, E19). Worth saying proactively as a point of honesty.

**How to tell it:** each person has their own tapping rhythm and touch habits; enroll 3 times, compare the current action with that template; the result is a risk signal, not a key.

**Limits stated up front** (numbers on StrokePIN, 97 people, not the team's own data): a PIN-knowing impostor gets through 38–57% at FRR 5%; changing posture nearly loses the signal; touch data is sensitive data (Personal Data Protection Law (Luật BVDLCN) 2025), collected only with consent. No separate iPhone/Android measurements, no real bots yet; PIN-first, phone tilt and the fixed phrase have not been measured.
