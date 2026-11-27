# Technology research notes

> Updated 24/11/2026. Each item states its confidence: **verified** (read the primary source or ran an experiment), **partial** (secondary source), **unknown**.

## 1. The threat is real and evolving (verified, secondary sources)

| Malware | Capability | Source |
|---|---|---|
| RemControl | Abuses Accessibility: fake overlays, live screen streaming, keylogging, remote control. The dropper blocks Play Protect through a local VPN and generates a new self-signed certificate on each install, so it evades hash-based detection | [Group-IB](https://www.group-ib.com/blog/remcontrol/), [Infosecurity](https://www.infosecurity-magazine.com/news/banking-trojan-remote-control/) |
| ToxicPanda 2.0 (08/2026) | Banking overlays, remote control, PIN capture, Accessibility abuse, attempts at Wireless Debugging. The goal is fraud on the victim's own device (on-device fraud) | [Malwarebytes](https://www.malwarebytes.com/blog/mobile/2026/08/toxicpanda-2-0-can-take-over-your-android-phone-and-banking-apps) |
| Trojan reported by Cyfirma (11/2025) | Reads the screen, taps buttons, fills in forms "like a user" | [Malwarebytes](https://www.malwarebytes.com/blog/news/2025/11/sneaky-new-android-malware-takes-over-your-phone-hiding-in-fake-news-and-id-apps) |

Implication: Innate's scenario A has a real-world basis. The reports say the attacker operates inside an already open session, so it evades unknown-device and unknown-location controls, which is exactly the gap the behavior layer is meant to close. These sources do **not** discuss detecting machine-generated touch.

## 2. R1: telling real touches from injected touches (unknown)

Public search does not answer this. What we found:
- The Android framework has a flag for events injected from an Accessibility service (AOSP has the constant `INJECTED_FROM_ACCESSIBILITY_TOOL` in the input flags; see the [commit mirror](https://gitlab.e.foundation/e/os/android_frameworks_native/-/commit/8a1be9125beb41e22d59e55ce64627be1a2c2880)). **Not verified** whether this flag reaches the `MotionEvent` that an app/WebView sees, or stays at the system level.
- `dispatchGesture` takes a `GestureDescription` and the framework builds the `MotionEvent` sequence itself, so a malicious service controls the trajectory and timing ([AOSP](https://android.googlesource.com/platform/frameworks/base/+/5f256310187b4ff2f13a7abb9afed9126facd7bc)).
- A web SDK only sees Pointer Events and cannot read system flags. This may be the practical reason a native SDK is needed. An experiment is needed to learn which fields are exposed.

**To do:** experiment R1 in [`research-plan.md`](research-plan.md).

## 3. R2: touch geometry on the web (partial)

- MDN lists Pointer Events as "Baseline widely available" since 07/2020 ([MDN](https://developer.mozilla.org/en-US/docs/Web/API/PointerEvent)).
- `width`/`height` is the contact area in CSS pixels, **defaulting to 1 when the hardware cannot report it** ([MDN width](https://developer.mozilla.org/Web/API/PointerEvent/width)).
- Not yet confirmed whether the team's demo phone returns real values or always 1. If it is 1, then `tap_w_*`/`tap_h_*` are useless and Zheng 2014 (which uses touch size) does not apply.
- The backend currently does not rely on `pressure`: correct, because the standard returns 0.5 when the device does not measure it.

## 4. The adaptive attacker (verified, preprint)

ActReal (Wang 2026): a system-level agent generates touch and IMU together, time-aligned, with an average success rate of 77.5%, still 71.1% when the detector uses both touch and IMU. Consequence: the "human or machine" layer is strongest against the naive bot. The pitch must say this plainly and measure with independent bot sources. Details: [`../plan/mo-ta-du-an-va-kiem-chung.md`](../plan/mo-ta-du-an-va-kiem-chung.md) section 4.

## 5. Models and evaluation (verified against papers)

See the comparison table in [`../plan/mo-ta-du-an-va-kiem-chung.md`](../plan/mo-ta-du-an-va-kiem-chung.md) section 3. Summary: realistic expected EER is 10–15% with ~25 people, one device, 3–5 sessions; imitation attack 10–15% (BioTouchPass2); report FAR@FRR together with confidence intervals.

## Open questions

1. Is the "injected" flag exposed to the app/WebView? (R1)
2. `width`/`height` on the demo phone? (R2)
3. How do the judges get into the trial version: a public key or an embedded one? (R6)
4. Is a native SDK needed for a real product, or is web enough for the contest? (decided after R1)
