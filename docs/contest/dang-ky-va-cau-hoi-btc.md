# Contest registration, questions to the organizers, and decisions the team must make

> Drafted 25/11/2026. **Deadline for registration and sending questions: 23:59:59 27/11/2026.** Organizers' email: techday@mservice.com.vn. I (Claude) have not sent anything; registration and sending the email are done by the team leader.

## 1. Registration (team leader, at https://techday.momo.vn)
- [ ] A team of 2–3 people; members are Vietnamese university/college students, Vietnamese nationality, **aged 18–23**; nobody currently works or interns at MoMo.
- [ ] Decide the **team name** and the member list (fill in the submission README, slides, product PDF).
- [ ] Take a screenshot of the registration confirmation and keep it.
- [ ] People outside the team may not take part in building the product: check who has contributed to the repo (see `git log`).

## 2. Clarification questions (draft to send before 27/11)

> **Subject:** [MoMo Tech Contest 2026] Clarification questions on the rules — team <TEAM NAME>
>
> Dear Organizers, team <TEAM NAME> would like to ask a few points so that we submit in line with the rules:
>
> 1. **Public data under a share-alike license.** We train the bot-detection and owner-recognition models on a public dataset licensed CC BY-NC-SA 4.0 (StrokePIN, DOI 10.21227/thft-4721), and have declared the source and license in the README. Derived models must be released under the same license. Is this acceptable in the submission, and do the Organizers require anything further about data sources?
> 2. **Product form.** Our product is a behavioral risk-scoring API service (with Swagger) plus a web demo simulating the money transfer flow, not a mobile app. Does this form meet the requirement of a "product usable online"?
> 3. **Source code.** Our source code is currently stored on GitHub. If we leave it public before the submission deadline, would that be considered sharing code between teams? We plan to make it private until submission.
> 4. **Data collected by the team.** We collect touch/typing rhythm (only timing, coordinates, event type, no content stored) from volunteer friends, with a written consent form. Is that a sufficient "basis for using data" under the rules, and do the Organizers require a specific form template?
> 5. **AI coding tools.** We use an AI coding assistant (Claude Code) to write code, experiments, and documents, and will declare it in the README under "AI tools used". Is there any limit on the degree of use?
> 6. **Figures in the slides.** The slides submitted on 03/12 cannot be edited. If we obtain further measurements after the deadline, may we present them as a supplement at the final?
>
> 7. **Pre-existing assets.** Our web interface reuses a design system (colors, components, animations) from an earlier web demo project of one member; all content, models, API, SDK, and Innate pages are new. We have declared this in the README. Is this approach valid? Also, if the whole package is released under CC BY-NC-SA 4.0 (because the models are derived from data under the same license), does that affect how MoMo evaluates or uses it after the contest?
>
> Thank you, Organizers. Team leader: <NAME>, <PHONE>.

## 3. Decisions the team must make (I do not decide for you)

| Decision | Suggestion | Reason |
|---|---|---|
| **Submission license** | **DECIDED 25/11: the whole package CC BY-NC-SA 4.0** (`LICENSE`); third-party libraries keep their own licenses (`THIRD_PARTY_NOTICES.md`) | A model trained on StrokePIN is a derivative. Note: CC does not recommend use for software code, and "non-commercial" may be a problem if MoMo wants to use it for real: ask the organizers (questions 1, 7). Not legal advice. |
| **The GitHub repo is currently public** | Switch to **private** before submitting, reopen after the final if wanted | The rules disqualify "sharing code between teams". The repo owner (`tuannghia2457`) can change it in Settings; I only have write access. |
| **Team-collected data** | Collect from 10–20 volunteer friends, 2 sessions, with consent forms, no content stored; or state in the README "no team data yet, only public data" | The rules disqualify entries using personal data of unclear source. |
| **DiceBear avatar set (web)** | **Checked 25/11:** the Notionists style (Zoish) is CC0 1.0; the DiceBear library is MIT | Declared in `THIRD_PARTY_NOTICES.md`. |
| **Aalto and Touchalytics do not state a data license** | Use only for research, do not put the data or derived models in the package; consider emailing to ask for confirmation (Antti Oulasvirta, Mario Frank) | Not sent yet; someone on the team must send it if a written answer is wanted. |
| **Reusing the Movago interface framework (a member's earlier web project)** | Declared in `web/README.md` and `THIRD_PARTY_NOTICES.md`; ask the organizers whether it counts as a "pre-existing product" (question 7) | The rules disqualify entries submitting a pre-existing product for this very problem; an interface framework is different from a product. |

## 4. Already done for you
- The submission README (`docs/submission/README.submission.md`) is filled in: API URL and Swagger (`/health` and `/docs` returned 200 on 25/11), web libraries, AI tools, where Touchalytics and Aalto data are used, E19 figures and the negative results. **Still `TODO`:** team name, members, web URL, demo key, Touchalytics/Aalto licenses, DiceBear package license, team data, consent form template.
