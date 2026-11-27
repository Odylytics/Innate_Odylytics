# Outputs to submit to the organizers

> Source: the official rules ([summary](the-le-cuoc-thi.md)). Submission deadline **23:59:59 03/12/2026**. No edits after the deadline, including the product at the submitted link. Send clarification questions before **23:59:59 27/11**: techday@mservice.com.vn.

> The web/demo part and the online product link are being done by the team later; there is no final URL for the PDF yet (needs to be fixed before writing).

## 4 components

| # | Component | Format and limits | Content for Innate | Owner | Status |
|---|---|---|---|---|---|
| 1 | **Product** | PDF ≤ 1 A4 page. A link to try it online immediately, with a trial account if login is needed | Link to the demo wallet (`/`) + Swagger (`/docs`). State the demo user, demo API key, demo PIN `159357`, 4 steps of use | Member 3 | Not started |
| 2 | **Source code** | `.zip` of all code + `README` | README declares: how to run, technologies, **pre-existing assets, open-source libraries, AI tools used**, data sources | Member 2 | Not started |
| 3 | **Description document** | Slide PDF ≤ 10 pages. Used as-is for the final, **may not be edited** | Problem, solution, architecture, evaluation figures, demo, limitations | Member 3 + Member 1 (figures) | Not started |
| 4 | **Video** | MP4 ≤ 3 minutes (anything past 3 minutes is not watched) | Film the product actually running: rhythm enrollment → real owner transfer → a stranger → bot blocked | Member 3 | Not started |

## Product conditions

- Can be tried **online**, not dependent on the team's local machine.
- **AI is the core** that creates the value, not a side feature.
- Runs stably at submission and stays **online continuously through 11/12/2026**.
- Belongs to at least 1 theme: AI assistant · Cybersecurity · Anti-fraud (Innate: Cybersecurity + Anti-fraud).

## Notes when building the `.zip`

- **Exclude**: `backend/.env.deploy-key` and all `.env*`, `*.db`, `.venv`, `__pycache__`, `.vercel`.
- `papers/` are other people's copyrighted PDFs: do not put them in the zip, only list them in the README (DOIs are in [`../research/paper-report.md`](../research/paper-report.md)).
- Branding: do not use the MoMo logo or name in the product, slides, or video.
- Personal data must state the source and basis for use (the consent forms of the data collection participants).

## Disqualified if

Submitting a pre-existing product · people outside the team take part · sharing code between teams · editing after the deadline · hiding pre-existing assets · personal data without a source.

## Milestones

| Date | Task |
|---|---|
| 27/11 | Register for the contest (team leader, techday.momo.vn) + send questions to the organizers |
| 03/12 | Submit all 4 components |
| 08/12 | Top 5 announced |
| 11/12 | Final in Ho Chi Minh City; the product must still be online |

## Submission progress (27/11)

| Component | Status |
|---|---|
| Slides ≤ 10 pages | **Full version done** (English, team Odylytics): `submission/Slide/` (editable PPTX + PDF exported from PowerPoint + fonts). Source `tools/build_pptx.js`, built with `tools/build_submission.sh`. **Cannot be edited after submission** |
| Video ≤ 3 minutes | Script exists ([`video-script.md`](../submission/video-script.md)); **not filmed yet** (demo URL exists: https://innate.odylytics.com) |
| 1-page guide PDF | **Done**: `submission/Product/Innate-product-guide.pdf` (QR, link, demo PIN, images of the steps) |
| Submission README | **English version done**: `submission/Document/README.md`; the `TODO` for the team's self-collected data figures remains |
| Source code zip | Built with `tools/build_submission.sh` → `submission/Document/Innate-source-code.zip` (not put into git) |
| Proposal, presentation script + Q&A | [`proposal.md`](../submission/proposal.md), [`pitch-script.md`](../submission/pitch-script.md) (English, synced with the final deck on 27/11/2026) |
