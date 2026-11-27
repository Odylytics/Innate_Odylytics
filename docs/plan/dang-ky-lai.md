# Controlled re-enrollment (after a 409 from `/enroll`)

> Design of 26/11/2026, **not implemented**. It addresses the gap noted in `CLAUDE.md`: `/enroll` returns 409 when a template already exists (to stop an impostor from inserting their rhythm), but E9 shows that a posture change (sitting → walking) loses the signal, so a valid extra enrollment round is needed.

## Principles
- Only an **owner authenticated through a channel outside Innate** (the wallet app's OTP/biometrics) may open a re-enrollment window. Innate does not authenticate on its own.
- Never re-enroll just because the score is low: a low score means either an impostor or an owner who changed posture, and Innate cannot tell the two apart (E9).
- The old template stays in place until the new template has enough rounds; new rounds are **added** (multiple postures), they do not replace.

## Flow
1. The wallet app authenticates the owner through a strong channel, then calls `POST /v1/users/{id}/enroll/window` (SDK key + a one-time token signed by the wallet backend, expires in 10 minutes). The backend sets `user.enroll_until`.
2. Inside the window, `/enroll` accepts additional rounds (instead of 409), tagged with a posture declared by the app (sitting/walking/lying), at most 5 rounds per window, 1 window per day.
3. When there are enough rounds: rebuild the template from **all** enrollment rounds (old + new); clear the `frozen` flag (see E7: a frozen template can only be reopened through this path); `mu0` is reset.
4. Write a log (who opened it, when, how many rounds) for the dashboard to show.

## Remaining risks
- An attacker who takes over an authenticated session can still inject their own rhythm: limited by 5 rounds per window, 1 window per day, and an alert when the new template deviates by more than 1 sd from the old one.
- There is no real data on how much the same person's posture shifts across several days; the 1 sd threshold is an assumption.
