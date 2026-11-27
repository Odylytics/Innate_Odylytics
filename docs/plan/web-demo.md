# Website demo for the judges

> Note of 25/11/2026. The team uses Mac + iPhone; there is no native app yet. Goal: one link the judges can open right away (the rules' "try it online" requirement), valid through 11/12.
> The web code is in the `web/` folder of this repo (landing `#/` + demo `#/demo` + story `#/demo?story=1` + operations `#/ops`). The API is in `backend/`. (The old `Innate_website` repo was merged in here on 26/11.)

## 1. What the judges will experience

1. Open the link → landing (`#/`): the problem, how Innate answers it, and the buttons **Xem demo 2 phút** (Watch the 2-minute demo) and **Tự thử ví demo** (Try the demo wallet yourself).
2. **Xem demo 2 phút** (`#/demo?story=1`): an 8-step story that plays by itself, with sound. Hà enrolls her rhythm → Hà pays her mum (`allow`) → malware taps the PIN at 2 a.m. (`hold`) → Bảo knows the PIN (`step_up`) → Khoa views the dashboard → policy. The sessions are pre-built but **scored for real on the API**.
3. **Tự thử ví** (`#/demo`): the judge types PIN `159357` three times to enroll, transfers money with their own rhythm, then clicks "malware" or "another person" in the attacker console to see a different result.

What runs for real: touch capture (Pointer Events on the self-drawn PIN pad and the swipe-to-confirm bar), scoring, enrollment locking, reasons in Vietnamese. What is simulated: the malware and Bảo sessions and the other characters (generated in the browser and sent to the API for scoring like real sessions).

## 2. Local check (25/11)

The API ran locally and scored exactly the sessions the web demo creates (`synth.ts`, same seed as the story). "25 people" = 25 random fake characters, each enrolling 3 times and then transferring money; Bảo and the malware are tried on each person's account. **Everything is fake sessions: this only checks the data path, not accuracy.**

| Demo PIN | AI (LightGBM) | Story: Hà / Bảo / malware | 25 owners | 25 Bảo runs | 25 malware runs |
|---|---|---|---|---|---|
| 4 digits `1593` (old) | off | allow / step_up / hold | 24 allow | 23 step_up, 2 hold | 25 hold |
| 4 digits `1593` (old) | on | allow / **hold** / hold | 24 allow | 21 step_up, 4 hold | 25 hold |
| 6 digits `159357` (current) | off | allow / step_up / hold | 25 allow | 22 step_up, 3 hold | 25 hold |
| 6 digits `159357` (current) | on | allow / **hold** / hold | **16 allow, 9 step_up** | 11 step_up, 14 hold | 25 hold |

Findings:
- **The "is this the owner" model does not run with a 4-digit PIN.** It was trained on 6-digit PINs (StrokePIN), so with `1593` the API silently falls back to the distance comparison. The "human or machine" model does run.
- **With a 6-digit PIN the owner model runs, but it bothers the real owner 9 times out of 25.** A judge trying it is quite likely to be asked for extra authentication on their own rhythm. This is on fake sessions; we do not know how it behaves for real people.
- **With AI on, the story no longer matches its lines.** The Bảo step says "Innate yêu cầu xác thực khuôn mặt" (Innate asks for face verification, i.e. `step_up`), but with AI on Bảo gets `hold`. The story was calibrated for when the online API runs rules only.
- **Mouse versus finger does not change the result** on fake sessions (touch size is not among the human/machine features). The rhythm of a judge's real mouse clicks has not been measured.
- **The online API currently runs rules only**: Vercel does not install `lightgbm`. The online version currently gives exactly the "AI off" rows above.

> **Addendum 25/11 (E28, real people):** cutting the first 4 touches of the 6-digit StrokePIN PIN (approximating a 4-digit PIN), on 10 people the trained model had never seen: with a 4-digit PIN the PIN-knowing impostor gets `allow` **68%** of the time (6 digits: 28%), so the "PIN-knowing person is asked for more" story at 4 digits holds only about 30% of the time with real people. See `docs/research/ai-research.md` (E28).

## 3. What needs to be done for the web demo to run

| # | Task | Who / where | Notes |
|---|---|---|---|
| 1 | Deploy `web/` (Root Directory = `web`) with `VITE_SDK_KEY` | whoever deploys | Without the key the API returns 401 and the demo shows an error |
| 2 | Decide whether to turn on AI on the online API | team | **Update 26/11:** from now on the online version has the learned model (fixed with `lgbm_text.py`; `/health` reports true; check with `backend/scripts/check_online.py`). The Bảo step of the story was written for pure rules, so it must be re-run and the lines fixed (Bảo may get `hold` instead of `step_up`; the owner sometimes gets `step_up`) |
| 3 | ~~Keep the 4-digit PIN~~ **6-digit PIN `159357` decided** (26/11): the demo wallet, story and docs all use 6 digits | web | A 4-digit PIN loses the learned owner model and lets more PIN-knowing impostors through (E28) |
| 4 | Test on a real iPhone and a real laptop | team | Safari iOS supports Pointer Events; touch `width/height` on iOS not yet checked. Quick test over the LAN: run Vite with `--host` and the API with `--host 0.0.0.0`, open `http://<Mac IP>:5173` on the iPhone |
| 5 | Write a "How to try it" guide on the landing + a 1-page PDF | `web/` + `docs/submission/` | Link, PIN `159357`, 3 steps |

## 4. Bringing the new transfer flow into the web (account number → bank → PIN)

The web can do most of it, except two malware signals that only a native app sees:

| Step | On the web | How to demo |
|---|---|---|
| Typing the account number on the self-drawn number pad | **Captured**: rhythm and off-center offset (Pointer Events, like the PIN) | The owner types for real; per E14, only extra evidence |
| Choosing a bank from the list | **Captured**: touch and scroll | The owner chooses for real |
| Malware sets the account number directly (`set_text`) | **Not capturable** from a browser | The attacker console sends a fake session with `set_text`; the API catches it with rules. Label it clearly as "simulated" |
| Malware picks a bank with no touch | **Not capturable** | As above |

The API must be changed first (see [`../research/transfer-flow.md`](../research/transfer-flow.md) section 3): the account number field has touch coordinates but **does not send the key label**, a bank-selection event, and extending the `set_text` rule to these two steps. Only then add the screens to the web wallet and the story.

## 5. Proposed order (submission deadline 03/12)

1. Deploy the web as it is now (6-digit PIN, API rules only) to get a stable link early. **This is the safe version.**
2. Test on the team's real iPhone and laptop; fix the interface if needed.
3. Decide whether to turn on AI on the API; if yes, fix the Bảo step's lines to match and re-check.
4. Add account number + bank to the API, then to the web wallet and the story.
5. Update the 1-page PDF and the video to match the final web version.
