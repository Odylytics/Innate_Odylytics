# What data to collect from participants (page `#/collect`)

> 25/11/2026. Answers the question "what kinds of data should we collect". Basis: experiments E9–E27 in [`../research/ai-research.md`](../research/ai-research.md), browser limitations, and the 2025 Personal Data Protection Law (collect the minimum, with consent). Overall collection plan: [`thu-du-lieu-doi.md`](thu-du-lieu-doi.md).

## 1. Selection principles

1. **Collect only what answers a question that already has an experiment waiting.** Each row below states which experiment it serves.
2. **The biggest open question is "recognizing the owner"**, not "human or machine" (naive bots are already caught ~100%). Owner recognition is weak because: a posture change loses the signal (E9, E14, E23), noise from different devices (E12b, E23), and few enrollment samples (E22). The team's data must fix exactly these three: **same device, record posture, multiple sittings**.
3. **The browser sees only part of the picture.** What only a native app sees (`set_text`, selection without touch, sensors ≥ 100 Hz) is not promised on the web.
4. **Collect as little personal data as possible.** Full name + email + the trial PIN are already stored with the touch data (team decision, 25/11); no other identifier is added.

## 2. Currently collected (current version)

The page asks only for full name + email (with a consent checkbox), then lets the person enter the PIN 5 times on a 10-digit keypad. It does not ask for posture or sitting (team decision 25/11, to keep the real page lean); `sitting` is always sent as 1. The collection time is still in `created_at`.

| Data | Field | Used for |
|---|---|---|
| Full name, email | `meta.full_name`, `meta.email` | Contact, deletion on request, grouping one person's sessions (`participant_id` hashed from the email) |
| Self-chosen trial PIN (6 digits) | `pin_taps[].key` | Research by key and key pair (geometric distance between two keys, E14/E21b); checking "typing a new PIN" versus a familiar PIN |
| Press/release time of each key | `pin_taps[].t_down`, `t_up` | Key hold time, interval between two keys: the core of owner recognition (E9, E12b) and human/machine (E4b) |
| Touch position relative to key center | `x, y, key_cx, key_cy, key_w, key_h` | Center offset (E12b); bots tap exactly at the center |
| Contact area size | `w, h` | Only to check device noise (E12b dropped it from the owner model). Kept because it is cheap, do not rely on it |
| Screen and time of first touch | `screens[]` | Hesitation time before typing |
| Device id | `device_id` | Separates "recognizing the person" from "recognizing the device" |

## 3. Worth adding, by value

| # | Data | On the web? | Why (evidence) | Cost |
|---|---|---|---|---|
| 1 | **Second sitting ≥ 1 day later**, same person, same device, same PIN | Yes (email + `created_at`) | Without a second sitting every owner-recognition figure is only "same sitting", which is optimistic. FETA requires a time-based split | Remind participants to come back. **The page must say clearly: next time, enter the same old PIN again** |
| 2 | **PIN-knowing impostor, on the owner's own device** | Yes (need to re-add a "person who knows the PIN" role and let them enter the owner's PIN) | E24: the PIN-knowing impostor is still `allow`ed 28%. Public data (StrokePIN) has the impostor on a different device, mixed with device noise; only the team's data has "same device" | A second person, 5 entries |
| 3 | **Several postures in one sitting** (sitting + standing or walking) | Yes | E9: enrolling in one posture breaks when posture changes; need to know whether enrolling in several postures rescues it (the "multi-posture enrollment" gap in CLAUDE.md) | 5 extra entries per posture |
| 4 | **Vietnamese challenge phrase** (`GET /v1/challenge`, retype the phrase) | Typing timing yes; Telex/VNI tone-mark typing style **not certain** (need to try `beforeinput`/composition on Gboard and iOS) | E13/E22: 30 keys give EER 0.25 versus 0.36 with only 6 keys; Vietnamese adds `vi_tone_late` (not yet measured on real people) | 5 phrases per sitting, ~2 minutes. Only `t, kind, n, cls` are stored, **not the phrase content** |
| 5 | **Motion sensors** (acceleration, gyroscope, device orientation) while entering the PIN | Limited: needs HTTPS, iOS Safari requires a tap to allow, ~60 Hz | E23: motion alone gives EER 0.04 same posture (suspected to be device recognition), and it disappears when posture changes. Need **same-device, two-person** data to know whether it recognizes the person or the device; and whether it distinguishes "device lying on a table (bot)" from "held in a hand" | Need to add an `imu` field to the API (not there yet) and ask for a separate permission. **More sensitive data**: ask separately, allow declining while still participating |
| 6 | **Confirmation swipe** | Yes (the SDK already has `swipes`) | E19: the uniform-velocity rule catches 100% of evenly swiping bots, 0/20,896 human strokes wrongly blocked, but measured on Touchalytics, not yet on the app's confirmation swipe | Add one swipe step after each PIN entry |
| 7 | **Minimal device info**: brand/model (self-reported or `userAgent`), screen size, `devicePixelRatio`, finger/hand used (thumb/index, left/right) | Yes | Explains variance between people; checks whether coordinates need normalizing by screen | Very low |

## 4. Do not collect

| Data | Reason |
|---|---|
| Pressure (`pressure`) | Browsers usually return a constant; design rule: do not rely on it |
| `isTrusted`, photos, voice, GPS location, contacts | Serve no experiment; raise legal risk |
| Challenge phrase content, real account numbers | Not needed for features; the server already knows the phrase via the token |
| Participants' real password/PIN | Warned twice; if anyone reports entering a real PIN by mistake, delete their sessions immediately |
| Age, gender, occupation | A sample of 10–20 people is too small for group analysis; it only adds identifiers |

## 5. Suggested order for the collection page

1. The page currently asks only for name + email per the team's decision; the items in section 3 (second sitting, posture, impostor) are **not done yet**. If we want a more trustworthy owner-recognition figure, item 3.1 (return for a second sitting, recognized via email + `created_at`) is the cheapest task.
2. **Before 30/11:** re-add the PIN-knowing impostor role, entering on the owner's device (item 3.2); one extra posture round (item 3.3).
3. **If there is time:** the challenge phrase (item 3.4) after trying the input method on a real phone; confirmation swipe (item 3.6).
4. **Leave until after submission:** motion sensors (item 3.5): need an API change, iOS permission, and a separate consent form.

Per participant, minimum: 2 sittings × 5 PIN entries + 5 impostor entries on their device. With 10–20 people this is enough to **run** `team_analysis.py` (T1–T5), but the confidence intervals will be wide; state the sample size when putting figures on slides.

## 6. Legal and operational notes

- Full name, email and the trial PIN sit with the touch data in each session, so the `/v1/export` file is personal data: only the holder of the ML key may export it, and it must not go into the repo or the submission zip.
- The consent form must list exactly what is collected. When adding any item from section 3, edit the form in `web/src/Collect.tsx` at the same time.
- State the deletion deadline (suggested: after the final on 11/12/2026) and how to request deletion (set `VITE_COLLECT_CONTACT`).
- Ask someone with legal knowledge to review the form (Luật BVDLCN 2025, the Personal Data Protection Law), as noted in `thu-du-lieu-doi.md`.
