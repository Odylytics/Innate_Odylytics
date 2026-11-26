# Innate — Landing page + web demo

One site: the landing page guides visitors into the demo wallet, the guided story and the ops dashboard. Vite + React + TypeScript, static build, hash routing. Every score shown comes from the live Innate API (`../backend/`, same repository).

## Run

```powershell
cd web
npm install
npm run dev        # http://localhost:5173
npm test           # synthetic sessions + reason texts
npm run build      # static site in dist/
```

Environment (`.env.local`, not committed):

| Variable | Default | Note |
|---|---|---|
| `VITE_API_URL` | `https://nhip-api-taupe.vercel.app` | Innate API |
| `VITE_SDK_KEY` | *(empty)* | The **SDK** key (`NHIP_API_KEYS`). It ships in the browser by design: it can only create sessions, enroll and score. The ops and ML keys are never bundled. |

## Deploy

Deploy this repository as one static site; nothing else is needed (the API is already hosted). Any static host works (Vercel, Netlify, GitHub Pages): hash routes, so no rewrites.

| Setting | Value |
|---|---|
| Root directory | `web` (this repository also holds the API in `backend/`, which has its own Vercel project) |
| Build command | `npm run build` |
| Output directory | `dist` |
| Env | `VITE_SDK_KEY` = the API's **SDK** key (ask the API owner), required for live scoring; `VITE_API_URL` only if the API moves. `VITE_*` values are baked in at build time: rebuild after changing them. |

After deploy, open `/#/demo` and enroll once to check that scoring works (without the SDK key the API answers 401).

## Pages

| Route | What it shows |
|---|---|
| `#/` | Landing (`src/landing/`, Tailwind, scoped to this page): hero with an animated PIN phone, live signal box (tap six keys, then let a bot try; runs in the browser), links into the full demo, owner vs PIN-thief vs malware, the three decisions, how it works, privacy, API and dashboard. Pale-blue hero atmosphere that fades into a white page; approved app-icon logo and fonts from the Figma brand kit. English only (the Vietnamese strings stay in the code; the language switch is removed). |
| `#/demo` | Demo wallet with the SDK inside. Enroll your rhythm (3 × PIN `159357`). After that the wallet unlocks with the PIN (recorded, never blocks) and Innate scores at the transfer confirmation (docs/plan/bon-cong-pipeline.md §7.4); two cases to try: Android hijacked remotely (malware) and phone stolen (thief who knows the PIN). Transfer to a saved contact or to a **bank account** (pick a bank, type the account number on the wallet's own pad: only key times are sent, never the digits). The attacker console replays malware (fills the account straight into the field, then taps the PIN) or another person (types an account, then the PIN) on the same screens. |
| `#/demo?story=1` | Guided story, 8 steps (~90 s): SDK, Hà enrolls, Hà pays her mum (allow), fake officer + Accessibility app, malware at 2 a.m. (hold), Bảo with the PIN (step-up), ops review, policy. Seeded sessions, scored live. Autoplay, sound, keyboard ← → K M, behind-the-scenes picture-in-picture. |
| `#/ops` | Fraud-ops dashboard: flagged sessions with reasons, label fraud / legit. Needs the **ops** key, typed by the analyst and kept in `sessionStorage` only. |
| `#/collect` | Touch data collection, phone only (Tom's page: name + email + consent, a throwaway 6-digit PIN typed 5 times, a Vietnamese sentence after each). **Phone-first:** a phone that opens the bare site address lands here (`src/device.ts`); any explicit route such as `#/` still opens that page. Works as an installed app: manifest + home-screen icons (`public/manifest.webmanifest`, `public/brand/icon-*.png`), full screen around the notch, an install tip (Android install button, iPhone Share steps). On a laptop it shows a QR code of this page instead. |

## What is live and what is simulated

| Part | In this demo |
|---|---|
| Touch capture (SDK) | Live: Pointer Events on the wallet keys and the swipe-to-confirm bar (`src/capture.ts`). Keyboard input is not counted, because it carries no touch position. |
| Scoring, enrollment lock, reasons | Live, from the API. |
| Attacker console, story sessions | Synthetic sessions (`src/synth.ts`) on the real key layout, scored live. Real attacks: `../attacker/` (adb). |
| Wallet, people, fake app dialog | Fictional. |
| KPIs on the landing page | Latency measured on the live API; catch rates simulated on synthetic sessions, labelled as such. |

## Pre-existing assets, libraries and tools (declared per contest rules)

| Asset | Source | Use |
|---|---|---|
| **Design system and frontend shell** | Movago web demo by team Odylytics (one of this team's members), reused: `styles.css`, `ui.tsx`, `smooth.ts`, `sound.ts`, `Intro.tsx`, `StoryBar.tsx`, `BehindScenes.tsx` engine, `DemoChoice.tsx`, nav/footer structure, colour tokens and type scale | Layout, components, motion, story player. All Innate content, wallet, SDK, API client, pages and line art are new. |
| Layout reference | Movora template (Framer Marketplace), via Movago's `DESIGN.md` | Grid, spacing, shapes only; no Movora images, logos or text |
| Avatars | Notionists by Zoish (CC0), pre-rendered with DiceBear | Fictional cast |
| Fonts | Sora, Manrope, JetBrains Mono (OFL, Google Fonts), chosen in the team's Figma brand kit | Typography (Sora has no Vietnamese glyphs, so Vietnamese headings use Manrope) |
| Libraries | React, React DOM, Lenis (MIT), Vite, TypeScript, Vitest, Tailwind CSS (MIT, landing page only, no preflight), qrcode-generator (MIT, QR on the collect page) | Build and runtime |
| AI tools | Claude (Anthropic) via Claude Code, used for code, copy and review | Development |
