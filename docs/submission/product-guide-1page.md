> **SUPERSEDED (27/11):** the official version is `submission/Product/Innate-product-guide.pdf`, generated from `tools/product-guide.html` by `tools/build_submission.sh`. This file is kept only as a draft.

# Innate — Trial guide (≤ 1 A4 page, DRAFT)

> **Not usable for submission yet:** the web demo URL and key (if needed) must be filled in. When done, export a 1-page A4 PDF (contest rules: it contains the **product link** and a **trial account**). Do not put secret keys in this file: the SDK key is already in the web build, and judges do not need to enter it.

**Innate** — a human verification layer for e-wallets. *A PIN can be stolen, innate touch habits are very hard to steal.*

| | |
|---|---|
| **Demo page** | `[TODO: web URL, opens immediately, no login]` (landing `#/`, demo wallet `#/demo`, story `#/demo?story=1`) |
| **API + Swagger** | https://nhip-api-taupe.vercel.app/docs (viewable immediately; trying calls needs the SDK key `[TODO]`) |
| **Demo PIN** | `159357` (6 digits) |

## 3 ways to see it (about 3 minutes)
1. **Watch the story:** open `#/demo?story=1`. Eight steps run automatically: the wallet owner enrolls the rhythm, a transfer passes (`allow`); a PIN-knowing person is asked for extra verification (`step_up`) with reasons; malware that taps by itself is held (`hold`).
2. **Try the wallet yourself:** open `#/demo`, enter PIN `159357` three times to enroll the rhythm, then transfer money (pick a saved recipient or enter an account number and choose a bank). Hand the phone to someone else to enter the same PIN and see a different result.
3. **Simulated malware:** in the attacker control panel, click "mã độc" (malware; fills in the account number directly, then taps the PIN) or "người khác" (someone else) to see Innate score right away on the real API.

## Reading the result
`allow` lets it through · `step_up` needs extra verification (face, OTP) · `hold` holds the order and notifies the user, with a reason in Vietnamese. Innate only **recommends**; it never locks an account.

## Notes
The wallet UI and the characters are fictional and are not any wallet's app. The malware and character sessions are generated in the browser and sent to the API to be scored like real sessions. Innate is a **risk signal**, not a replacement for PIN/OTP/face. Only timing, coordinates and event type are stored; no PIN or content. Source code and figures: see the `.zip` package. License: CC BY-NC-SA 4.0.
