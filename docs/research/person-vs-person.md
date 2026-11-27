# Person-to-person verification (1:1) and the "Accuracy check" bar at enrollment (27/11/2026)

## 1. Has anyone done "telling one person from another" with behavioral biometrics?

**Yes, a lot.** 1:1 verification (is this session from the account owner, or from someone else even if they know the PIN) is the original problem of keystroke/touch-rhythm biometrics. Works already in `papers/` (detailed summaries: `notes/owner_verification.md`, `paper-report.md`):

| Work | What it does | Figures |
|---|---|---|
| Zheng et al. 2014, *You Are How You Touch* | Rhythm + touch position when typing a PIN on a phone, >80 people | EER 3.65–7% (85 training samples/person, shared PIN) |
| Buschek et al. 2015 (CHI) | Adds touch off-center offset to rhythm | EER down 26–37% versus rhythm only; across different sessions EER doubles |
| Killourhy & Maxion 2009 | Compares 14 detectors, same password, 51 people | Scaled Manhattan is best, EER 9.6% (used in `owner.py`) |
| Acien et al. 2021, TypeNet | A jointly trained network, verifying people not seen | Mobile EER 10.7% (1 sample) → 6.3% (10 samples) |
| Stragapede et al. 2022/2023 (Transformer, KVC) | Benchmark with 5 enrollment rounds | EER 6.99% (1) → 3.84% (5) → 3.15% (10) |
| Khan et al. 2018 | Impostors practicing imitation with AR guidance | Passed 87% of the time after ~4 minutes of practice |

Conclusion: telling people apart is **not a new idea**. What differs in Innate is placing it at the wallet's transfer confirmation step, combining it with the human/machine signal and context, and measuring honestly on real phone PINs (E9, E30).

An **enrollment progress/sample quality bar** is rarer in the academic literature. A search (27/11) found only a patent that shows the number of missing samples as a "thermometer" ([US 7809170](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7809170)), a sample-quality measure correlated with error (Morales et al. 2015, [repositorio.uam.es](https://repositorio.uam.es/bitstream/handle/10486/665359/towards_morales_LNCS_2015_ps.pdf?sequence=1)), and a sample-quality index that predicts FAR ([PLoS ONE 2022](https://doaj.org/article/0df83e8ac87840bfa9022a584586514c)). We have not read the full texts; we **did not find** a work that builds this bar for PIN rhythm.

## 2. What the "Accuracy check" bar in the demo measures

Two numbers, both with sources:

1. **Main bar = % of PIN-knowing impostors blocked** = 1 − FAR@FRR5% by number of enrollment rounds k (`web/src/enrollCurve.ts`).
   - k = 2, 3, 4: **really measured** on StrokePIN, sitting, backend distance (E30): 14%, 50%, 57%.
   - k ≥ 5: **extrapolated** with a power law through k = 3 and 4 (StrokePIN has at most 5 sitting rounds, so no rounds are left to test). The interface states clearly "extrapolated, not measured". k = 5 → ~62%, k = 10 → ~74%.
2. **Rhythm stability of the enrolling person** (`owner.consistency`): each round is scored against a template built from the remaining rounds (leave-one-out), then averaged. High = steady typing. This is **not** the accuracy of recognizing the person.

Do not put the extrapolated numbers on slides as measurements. A safe way to say it: "the more times you enter, the more PIN-knowing impostors are blocked; going from 3 to 4 rounds is measured, beyond 4 is an estimate".

## 3. Demo flow for the judges

1. `#/demo` → enter a name → account `judge_<name without diacritics>` (same name = same account, not case- or diacritic-sensitive).
2. Type PIN `159357` 5 to 10 times; the bar rises after each one. Press **Xong** (Done; unlocks after 5 rounds) or it locks automatically at round 10.
3. Open the wallet, transfer money: Innate scores at the confirmation step.
4. Another judge logs in **with the other person's name** and transfers money: expected `step_up`/`hold`. Or press "Kẻ trộm biết PIN" (the thief who knows the PIN).

## 4. Backend changes and limits

- `POST /v1/users/{id}/enroll` accepts `keep_open` (default false: the old behavior, locks at round 3). With `keep_open=true`, each round rebuilds the template; it locks when `POST /v1/users/{id}/enroll/finish` is called or at 10 rounds. An old template without the `open` flag is still treated as locked.
- **Security limit:** while enrollment is still open, anyone with the SDK key who knows the user_id can add rounds (up to 10). Login by name has **no password**: demo use only.
- Enrolling 5–10 rounds in **one sitting** is still weak when posture changes (E9: sitting → walking nearly loses the signal).
