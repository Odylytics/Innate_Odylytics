# False alarms (a real owner blocked/asked for more), their danger, and sitting/walking posture (27/11/2026)

"False alarm" here = **the real account owner does not get `allow`** (gets `step_up` or `hold`). Conversely "got through" = a PIN-knowing impostor gets `allow`.
Figures: E33 (`research/experiments/e33_posture_false_alarm.py`, full table in `research/results/e33_posture_false_alarm.md`), run through the exact `/score` chain of the backend on StrokePIN (real 6-digit PIN, each person with 5 sitting rounds + 5 walking rounds). The test set is fixed across all enrollment methods.

## 1. Main result (full learned model, 10 people never seen, known recipient; 95% CI by person)

| Enrollment | Owner **sitting**: false alarm | Owner **walking**: false alarm | Owner **held** | PIN-knowing impostor gets through (sitting / walking) |
|---|---|---|---|---|
| 3 sitting rounds (like a user who enrolls sitting down in the app) | 17% [11, 23] | **41% [31, 50]** | 0–1% | 24% / 31% |
| 3 walking rounds | 36% [28, 44] | 16% [11, 21] | 0–1% | 30% / 37% |
| 2 sitting + 2 walking | 20% [13, 27] | **18% [12, 24]** | 0–1% | 34% / 39% |
| 3 sitting + 3 walking | 18% [12, 25] | 19% [12, 25] | 0–1% | 33% / 40% |

Reading the table:
1. **A posture change more than doubles false alarms.** Enrolling while sitting and then transferring while walking: 41% of the time the real owner is asked for more (sitting: 17%). The reverse also holds (enroll walking, use sitting: 36%).
2. **Mixed-posture enrollment nearly evens out both sides** (~18–20% both sitting and walking): false alarms while walking drop from 41% to 18%.
3. **The price:** the template is "wider", so PIN-knowing impostors get through about 10 points more (sitting 24% → 34%, CIs do not overlap). This is a real trade-off, not free.
4. **The owner is almost never held** (0–1%; most of those rare cases come from the "bot-like" rule while walking). The main risk is **annoyance**, not lost money or a locked account.
5. **New recipient:** almost every owner transaction is asked for more (84–98%) and the impostor almost never gets through (0–1%). The "new recipient" weight is overwhelming the rhythm; the demo should pick a known recipient to show the difference.

Secondary table (learned model off, 96 people, rules + distance only): low false alarms (sitting 4%, walking 11%; mixed posture: 3% / 5%) but **PIN-knowing impostors get through 85–94%**. That means the distance formula alone blocks almost no one; the learned model (even though TEMPORARY) is carrying the owner-recognition part.

## 2. Why false alarms are dangerous

| Risk | Mechanism | Level in current Innate |
|---|---|---|
| **Annoyance, abandoned transactions** | The real owner is asked for more ~1 in 5 times when sitting, ~2 in 5 times when walking | High if users often transfer money on the move. The RBA paper (Wiefling 2020) shows users accept step-up because it is *rare*; Freeman 2016 chooses the threshold from a small false-alarm budget |
| **"Alert fatigue"** | If asked for more too often, users treat it as a formality and type just to get through; an impostor sitting next to them gets used to it too | Lowers the value of the step-up step itself |
| **Wrongly holding the owner's money** | `hold` from the "bot-like" rule or risk > 0.55 | 0–1% with a known recipient; higher with a new recipient (E24: 3–4%). Urgent money (hospital fees, tuition) is delayed |
| **A loop that cannot learn** | The template updates only after a confident `allow` (anti-poisoning). Transfers made while walking are often asked for more → the template never learns the walking posture | People who often travel are penalized for good; false alarms do not drop by themselves over time |
| **Unfairness** | Older people, hand tremor, motor disabilities, one-handed users on a bus: larger rhythm variation → systematically more false alarms | Not yet measured by group; Eberz 2017 advises reporting the error distribution per person (Gini), not just the mean |
| **Lowering the threshold to reduce annoyance lets impostors through** | E25 table: relaxing A, B means the owner is asked less but PIN-knowing impostors get through more | The operating point must be chosen deliberately, per service (Wiefling 2021) |
| **The Accuracy check bar is optimistic** | The E30 curve is measured while *sitting*, same posture | In real life (walking, standing) the real impostor-blocking rate and the false alarm rate both differ from the numbers on the bar |

## 3. Do sitting and walking need to be included? Yes.

1. **Enrollment should include both postures.** Proposal for the app: within 5–10 entries, prompt "entries 1–3: sitting; entries 4–5: type while walking" (≈ "2–3 sitting + 2 walking" in the table above). This cuts false alarms while walking from ~41% to ~18%, in exchange for ~10 more points of PIN-knowing impostors getting through.
2. **Let the template learn a new posture in a controlled way:** after the owner passes `step_up` (types the right sentence), allow that session to be added to the template ("supervised update", like Windows Hello asking for the PIN before updating; Lovisotto 2020). This needs a real step-up step in the app first (currently it only flags).
3. **Collect team data with posture labels and holder labels** to re-measure on Vietnamese people, self-chosen PINs, the same phone (an impostor holding the victim's actual phone has not been simulated: the real "got through" number may be higher).
4. **Report per person** (who gets many false alarms), not just the mean.

## 4. Limits of E33

- Only 10 people for the full-model table (wide CI); the 96-person table has the learned model off.
- StrokePIN: PINs assigned by the researchers (20 shared PINs), sitting and walking collected in the same batch (no multi-day gap), the impostor uses a different phone.
- No motion sensor in the pipeline; it does not know which posture a session is in at run time.
- The learned model is a temporary version, trained on StrokePIN (other people) + self-generated bots.
