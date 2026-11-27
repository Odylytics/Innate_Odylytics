// Editable Innate deck (PPTX). Run: NODE_PATH=<dir with pptxgenjs> node tools/build_pptx.js <out.pptx> <team> <web url>
// Needs: npm --prefix tools i pptxgenjs. Fonts: Sora (headings) + Manrope (body) per the Innate Brand Identity Kit; install them to edit with the intended look.
const path = require('path')
const pptxgen = require('pptxgenjs')
const { applyTheme } = require('./lib/apply_theme.js')
const A = path.join(__dirname, 'assets') + '/'
const S = A + 'shots/'
const OUT = process.argv[2] || 'Innate-slides.pptx'
const URL = (process.argv[4] || 'https://innate.odylytics.com').replace(/^https?:\/\//, '').replace(/\/$/, '')

const INK = '071A1C', TEAL = '0F4F4C', JADE = '11B88F', MINT = '63E6BE', MIST = 'CFF7EE', CLOUD = 'F5FBF9', STONE = 'DDE8E5', CORAL = 'FF7A6B', AMBER = 'F5B941'
const MUTED = '52666A', MUTED_D = 'A9BDBD'
const H = 'Sora', B = 'Manrope'
const THEME = {
  name: 'Innate', headFontFace: H, bodyFontFace: B,
  colors: { dk1: INK, lt1: 'FFFFFF', dk2: TEAL, lt2: CLOUD, accent1: JADE, accent2: MINT, accent3: TEAL, accent4: AMBER, accent5: CORAL, accent6: MIST, hlink: TEAL, folHlink: MUTED },
}

const pres = new pptxgen()
pres.layout = 'LAYOUT_WIDE' // 13.33 x 7.5 in
pres.theme = { headFontFace: H, bodyFontFace: B }
pres.title = 'Innate: silent human verification for wallet transfers'
pres.author = 'Odylytics'
pres.company = 'Odylytics'

const footer = (dark) => [{ image: { path: A + (dark ? 'lockup-dark.png' : 'lockup-ink.png'), x: 0.75, y: 6.82, w: 1.30, h: 0.2275 } }]
for (const [name, dark] of [['LIGHT', false], ['DARK', true]]) {
  pres.defineSlideMaster({
    title: name, background: { color: dark ? INK : CLOUD },
    objects: [
      ...footer(dark),
      { placeholder: { options: { name: 'title', type: 'title', x: 0.75, y: 0.5, w: 11.8, h: 1.15, fontFace: H, fontSize: 30, bold: true, color: dark ? 'FFFFFF' : INK, valign: 'top', align: 'left', margin: 0, fit: 'shrink' }, text: '' } },
    ],
    slideNumber: { x: 11.6, y: 6.78, w: 0.98, h: 0.3, fontFace: B, fontSize: 11, color: dark ? MUTED_D : MUTED, align: 'right' },
  })
}
pres.defineSlideMaster({ title: 'COVER', background: { color: INK }, objects: [] })

const T = (s, text, o) => s.addText(text, Object.assign({ isTextBox: true, fontFace: B, fontSize: 14, color: INK, margin: 0, valign: 'top' }, o))
const arrow = (s, x, y, color = JADE) => s.addShape(pres.shapes.RIGHT_ARROW, { x, y, w: 0.3, h: 0.2, fill: { color }, line: { color, width: 0 } })
const link = (s, x1, x2, y, color = JADE) => s.addShape(pres.shapes.LINE, { x: x1 + 0.14, y, w: x2 - x1 - 0.28, h: 0, line: { color, width: 1.5, endArrowType: 'triangle' } })
const hair = (s, x, y, w, color = STONE) => s.addShape(pres.shapes.LINE, { x, y, w, h: 0, line: { color, width: 0.75 } })
const vhair = (s, x, y, h, color = STONE) => s.addShape(pres.shapes.LINE, { x, y, w: 0, h, line: { color, width: 0.75 } })
const dot = (s, x, y, color, d = 0.14) => s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color }, line: { color, width: 0 } })
const cap = (s, text, x, y, w, dark) => T(s, text.toUpperCase(), { x, y, w, h: 0.25, fontSize: 11, bold: true, charSpacing: 2, color: dark ? MINT : TEAL })

// ---- 1 Cover
{
  const s = pres.addSlide({ masterName: 'COVER' })
  s.addImage({ path: A + 'gesture-dark.png', x: 7.4, y: -0.9, w: 7.6, h: 7.6, altText: 'Innate gesture mark, cropped' })
  s.addImage({ path: A + 'lockup-dark.png', x: 0.75, y: 0.6, w: 2.1, h: 2.1 * 43.73 / 228.17, altText: 'innate' })
  s.addShape(pres.shapes.RECTANGLE, { x: 3.12, y: 0.62, w: 0.012, h: 0.4, fill: { color: '3A5557' }, line: { color: '3A5557', width: 0 } })
  T(s, 'Powered by', { x: 3.3, y: 0.62, w: 1.2, h: 0.4, fontSize: 13, color: MUTED_D, valign: 'middle' })
  s.addImage({ path: A + 'odylytics-on-dark.png', x: 4.45, y: 0.67, w: 1.4, h: 1.4 * 549 / 1813, altText: 'Odylytics' })
  cap(s, 'MoMo Tech Contest 2026  ·  Cybersecurity + Anti-fraud', 0.75, 2.2, 8, true)
  T(s, 'Silent human verification for every transfer', { x: 0.75, y: 2.6, w: 9.0, h: 2.0, fontFace: H, fontSize: 44, bold: true, color: 'FFFFFF', lineSpacingMultiple: 0.98 })
  T(s, 'Innate reads the rhythm behind every tap and quietly checks that the right person, not a bot or a PIN thief, is confirming the payment. The owner does nothing extra.', { x: 0.75, y: 4.45, w: 6.6, h: 1.1, fontSize: 16, color: MUTED_D, lineSpacingMultiple: 1.15 })
  T(s, 'Your behavior is your signature', { x: 0.75, y: 5.75, w: 7, h: 0.4, fontFace: H, fontSize: 20, bold: true, color: MINT })
  T(s, 'Team Odylytics', { x: 10.2, y: 6.95, w: 2.38, h: 0.3, fontSize: 11, color: MUTED_D, align: 'right' })
  s.addNotes('Open with the one-line promise: a layer that verifies the human at the moment of transfer, with no extra step for the owner.')
}

// ---- 2 Problem
{
  const s = pres.addSlide({ masterName: 'LIGHT' })
  s.addText("Fraud now arrives with the right PIN, on the owner's own phone", { placeholder: 'title' })
  const path2 = (y, tag, name, steps, note) => {
    T(s, [{ text: tag + '  ', options: { color: JADE, bold: true } }, { text: name, options: { bold: true } }], { x: 0.75, y, w: 6, h: 0.3, fontFace: H, fontSize: 17 })
    steps.forEach((t, i) => {
      const x = 0.75 + i * 2.0
      if (i) vhair(s, x - 0.1, y + 0.5, 0.95)
      T(s, String(i + 1), { x, y: y + 0.45, w: 1.8, h: 0.3, fontFace: H, fontSize: 12, bold: true, color: TEAL, align: 'center' })
      T(s, t, { x, y: y + 0.8, w: 1.8, h: 0.6, fontSize: 13, align: 'center' })
    })
    T(s, note, { x: 0.75, y: y + 1.55, w: 5.9, h: 0.3, fontSize: 11, color: MUTED })
  }
  path2(1.9, 'A', 'Remote-control malware', ['A fake APK gets\nAccessibility access', 'It reads the screen\nand the OTP', 'It then taps the\ntransfer itself'], 'Families such as RemControl and ToxicPanda 2.0, reported 2025 to 2026.')
  hair(s, 0.75, 4.0, 5.9)
  path2(4.15, 'B', 'Someone who knows the PIN', ['Sees or guesses\nthe PIN', 'Holds the\nunlocked phone', 'Confirms the\ntransfer'], 'A relative, a colleague, a thief: same PIN, same device, open session.')
  vhair(s, 7.2, 1.95, 3.85)
  cap(s, "What today's checks see", 7.7, 1.95, 4.8)
  ;['Device is trusted', 'PIN is correct', 'OTP was entered', 'Session is valid'].forEach((t, i) => {
    dot(s, 7.7, 2.5 + i * 0.52 + 0.06, JADE); T(s, t, { x: 8.05, y: 2.5 + i * 0.52, w: 4, h: 0.3, fontSize: 16 })
  })
  hair(s, 7.7, 4.62, 4.8)
  dot(s, 7.7, 4.82 + 0.05, CORAL, 0.16); T(s, 'Money leaves', { x: 8.05, y: 4.8, w: 4, h: 0.3, fontFace: H, fontSize: 17, bold: true })
  s.addShape(pres.shapes.RECTANGLE, { x: 0.75, y: 6.0, w: 11.83, h: 0.62, fill: { color: INK }, line: { color: INK, width: 0 } })
  T(s, 'Every check passes. None of them asks who is touching the screen.', { x: 0.75, y: 6.0, w: 11.83, h: 0.62, fontFace: H, fontSize: 17, bold: true, color: 'FFFFFF', valign: 'middle', align: 'center' })
  s.addNotes('Two ways in: malware that taps by itself, and a person who knows the PIN. Both pass PIN, OTP and device checks.')
}

// ---- 3 Idea
{
  const s = pres.addSlide({ masterName: 'LIGHT' })
  s.addText('Make how you tap the credential: nothing to remember, steal or phish', { placeholder: 'title' })
  const rows = [['Silent', 'Runs inside the existing PIN and confirm screens. The owner adds zero steps.'], ['Hard to steal', 'A habit is not a secret. Seeing the PIN does not reveal the rhythm behind it.'], ['Explained', 'Every decision ships with a plain reason that the ops team can read and act on.']]
  rows.forEach(([h, d], i) => {
    const y = 2.0 + i * 1.45
    if (i) hair(s, 0.75, y - 0.2, 5.5)
    T(s, h, { x: 0.75, y, w: 5.5, h: 0.4, fontFace: H, fontSize: 22, bold: true })
    T(s, d, { x: 0.75, y: y + 0.5, w: 5.4, h: 0.7, fontSize: 15, color: MUTED, lineSpacingMultiple: 1.1 })
  })
  cap(s, "Where it sits in the wallet's stack", 7.2, 1.95, 5.4)
  const stack = [['1', 'Device and app integrity', 'is the phone clean?'], ['2', 'Authentication', 'PIN, OTP, face'], ['3', 'Innate', 'human or bot? the owner?'], ['4', 'Transaction risk engine', 'is the transfer unusual?'], ['5', 'Operations and response', 'review, step-up']]
  stack.forEach(([n, a, b], i) => {
    const y = 2.4 + i * 0.7, me = n === '3'
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 7.2, y, w: 5.38, h: 0.58, rectRadius: 0.08, fill: { color: me ? INK : 'FFFFFF' }, line: { color: me ? INK : STONE, width: 0.75 } })
    T(s, n, { x: 7.4, y, w: 0.3, h: 0.58, fontFace: H, fontSize: 14, bold: true, color: me ? MINT : TEAL, valign: 'middle' })
    T(s, a, { x: 7.8, y, w: 2.7, h: 0.58, fontSize: 14, bold: me, color: me ? 'FFFFFF' : INK, valign: 'middle' })
    T(s, b, { x: 10.5, y, w: 1.95, h: 0.58, fontSize: 11, color: me ? MUTED_D : MUTED, valign: 'middle' })
  })
  T(s, 'One added layer. It replaces nothing and blocks nothing on its own.', { x: 7.2, y: 6.0, w: 5.4, h: 0.5, fontSize: 13, color: MUTED })
  s.addNotes('The credential is behavior. It sits between authentication and the transaction risk engine.')
}

// ---- 4 User flow
{
  const s = pres.addSlide({ masterName: 'LIGHT' })
  s.addText('One transfer, and the owner notices nothing', { placeholder: 'title' })
  s.addImage({ path: S + 'wallet-pad.png', x: 0.75, y: 1.5, w: 3.05, h: 3.05 * 610 / 400, altText: 'Demo wallet with the Innate SDK on the PIN pad' })
  T(s, 'Demo wallet with the SDK on the PIN pad', { x: 0.75, y: 6.2, w: 3.05, h: 0.3, fontSize: 11, color: MUTED, align: 'center' })
  const X0 = 4.35, CW = 2.08
  const steps = [['1', 'Enter amount', 'The normal\ntransfer form.'], ['2', 'Tap the PIN', 'Timing and touch only.\nNever the digits.'], ['3', 'Confirm', 'The wallet calls\nInnate once.'], ['4', 'Innate scores', 'About 4 ms in tests,\nwith reasons.']]
  steps.forEach(([n, h, d], i) => {
    const x = X0 + i * CW, cx = x + CW / 2
    s.addShape(pres.shapes.OVAL, { x: cx - 0.21, y: 1.55, w: 0.42, h: 0.42, fill: { color: i === 3 ? JADE : INK }, line: { color: i === 3 ? JADE : INK, width: 0 } })
    T(s, n, { x: cx - 0.21, y: 1.55, w: 0.42, h: 0.42, fontFace: H, fontSize: 13, bold: true, color: i === 3 ? INK : 'FFFFFF', align: 'center', valign: 'middle' })
    if (i < 3) link(s, cx + 0.21, cx + CW - 0.21, 1.76, STONE)
    T(s, h, { x, y: 2.15, w: CW, h: 0.35, fontFace: H, fontSize: 15, bold: true, align: 'center' })
    T(s, d, { x, y: 2.58, w: CW, h: 0.6, fontSize: 12, color: MUTED, align: 'center' })
  })
  hair(s, X0, 3.5, 8.23)
  cap(s, 'Then one of three things happens', X0, 3.68, 8.23)
  const OW = 2.74
  const out = [[JADE, 'allow', 'The owner sees nothing.\nThe transfer completes\nas usual.'], [AMBER, 'step_up', "Doubtful: the wallet's\nexisting face or OTP,\nor a typed phrase."], [CORAL, 'hold', 'Bot-like: transfer paused,\nuser alerted, ops reviews\nthe reasons.']]
  out.forEach(([c, h, d], i) => {
    const x = X0 + i * OW, cx = x + OW / 2
    dot(s, cx - 0.07, 4.2, c)
    T(s, h, { x, y: 4.45, w: OW, h: 0.35, fontFace: H, fontSize: 17, bold: true, align: 'center' })
    T(s, d, { x, y: 4.9, w: OW, h: 0.8, fontSize: 13, color: MUTED, align: 'center' })
  })
  T(s, [{ text: 'Enrollment is the PIN taps users already make. ', options: { bold: true } }, { text: 'The first 3 to 5 normal uses build the habit template, with no setup screen. Bot detection needs no enrollment.' }], { x: X0, y: 5.95, w: 8.23, h: 0.6, fontSize: 13, align: 'center' })
  s.addNotes('Walk the four steps; the owner only ever types the PIN. Branches map to flows the wallet already runs.')
}

// ---- 5 Integration
{
  const s = pres.addSlide({ masterName: 'LIGHT' })
  s.addText('One SDK, one API call, three outcomes mapped to flows the wallet already has', { placeholder: 'title' })
  const BW = 3.1, GAP = (11.83 - 3 * BW) / 2, XS = [0.75, 0.75 + BW + GAP, 0.75 + 2 * (BW + GAP)]
  const box = (x, h1, h2, dark, mono) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.95, w: BW, h: 0.95, rectRadius: 0.1, fill: { color: dark ? INK : 'FFFFFF' }, line: { color: dark ? INK : STONE, width: 0.75 } })
    T(s, h1, { x, y: 2.06, w: BW, h: 0.35, fontFace: H, fontSize: 15, bold: true, color: dark ? 'FFFFFF' : INK, align: 'center' })
    T(s, h2, { x, y: 2.5, w: BW, h: 0.3, fontSize: 11, color: dark ? MUTED_D : MUTED, fontFace: mono ? 'Courier New' : B, align: 'center' })
  }
  box(XS[0], 'Wallet app', 'PIN pad + Innate SDK')
  box(XS[1], 'Innate API', 'POST /v1/sessions/{id}/score', true, true)
  box(XS[2], 'Wallet risk and auth', 'Face, OTP, review queue')
  ;[['timing events', XS[0] + BW, XS[1]], ['action + reasons', XS[1] + BW, XS[2]]].forEach(([t, x1, x2]) => {
    T(s, t, { x: x1, y: 2.1, w: x2 - x1, h: 0.25, fontSize: 10, bold: true, color: TEAL, align: 'center' })
    link(s, x1, x2, 2.55)
  })
  const st = [['1', 'Embed the SDK', ' on the PIN pad and transfer form. It sends timing and coordinates only.'], ['2', 'Call score', ' at the confirm step. One request returns the action, risk and reasons.'], ['3', 'Map the action', ' to flows you already run: face or OTP for step_up, review for hold.']]
  st.forEach(([n, h, d], i) => {
    const y = 3.4 + i * 0.95
    T(s, n, { x: 0.75, y, w: 0.4, h: 0.4, fontFace: H, fontSize: 24, bold: true, color: JADE })
    T(s, [{ text: h, options: { bold: true } }, { text: d }], { x: 1.25, y: y + 0.03, w: 4.7, h: 0.85, fontSize: 13, lineSpacingMultiple: 1.05 })
  })
  T(s, 'Thresholds are set per partner. Nothing typed leaves the device.', { x: 0.75, y: 6.25, w: 5.4, h: 0.3, fontSize: 11, color: MUTED })
  s.addImage({ path: S + 'decision-hold.png', x: 6.6, y: 3.4, w: 5.98, h: 5.98 * 336 / 736, altText: 'Live Innate decision: hold, risk 96 percent, with five plain-language reasons' })
  T(s, 'Live output for the malware case: human 0%, owner match 11%, risk 96%.', { x: 6.6, y: 6.2, w: 5.98, h: 0.3, fontSize: 11, color: MUTED, align: 'center' })
  s.addNotes('Integration is three steps. The screenshot is the real API output from the live demo.')
}

// ---- 6 AI
{
  const s = pres.addSlide({ masterName: 'LIGHT' })
  s.addText('Three checks, one explainable decision', { placeholder: 'title' })
  const cols = [['1', 'Human or bot?', 'Even rhythm, exact key centers,\ntext set directly, no touch.', 'Rules + LightGBM trained on\nreal people and simulated bots.'], ['2', 'The owner?', 'PIN hold times, gaps and tap offsets\nagainst 3 to 5 enrollment sessions.', 'Normalized distance, population\nshrinkage, LightGBM on deviations.'], ['3', 'A replay?', "A session nearly identical to\nthe account's own recent ones.", 'Distance to the 50 latest\nsessions of the account.']]
  const CW = 11.83 / 3
  cols.forEach(([n, h, d, m], i) => {
    const x = 0.75 + i * CW
    if (i) vhair(s, x, 1.9, 2.7)
    T(s, n, { x, y: 1.85, w: CW, h: 0.7, fontFace: H, fontSize: 40, bold: true, color: JADE, align: 'center' })
    T(s, h, { x, y: 2.6, w: CW, h: 0.4, fontFace: H, fontSize: 20, bold: true, align: 'center' })
    T(s, d, { x, y: 3.15, w: CW, h: 0.6, fontSize: 14, align: 'center' })
    T(s, [{ text: 'Method\n', options: { bold: true, color: TEAL } }, { text: m }], { x, y: 3.95, w: CW, h: 0.8, fontSize: 12, color: MUTED, align: 'center' })
  })
  const PW = 3.3, PG = (11.83 - 3 * PW) / 2
  const pipe = [['Weighted risk score', false], ['allow  ·  step_up  ·  hold', true], ['A plain reason per signal', false]]
  pipe.forEach(([t, ink], i) => {
    const x = 0.75 + i * (PW + PG)
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 5.05, w: PW, h: 0.62, rectRadius: 0.08, fill: { color: ink ? INK : MIST }, line: { color: ink ? INK : MIST, width: 0 } })
    T(s, t, { x, y: 5.05, w: PW, h: 0.62, fontFace: H, fontSize: 14, bold: true, color: ink ? 'FFFFFF' : INK, align: 'center', valign: 'middle' })
    if (i < 2) link(s, x + PW, x + PW + PG, 5.36)
  })
  T(s, 'No LLM sits on the decision path. Templates keep means and spreads only, never the PIN, amount or text.', { x: 0.75, y: 6.0, w: 11.83, h: 0.3, fontSize: 13, color: MUTED, align: 'center' })
  s.addNotes('Explainability is a design rule: every decision carries reasons per signal.')
}

// ---- 7 Evidence (native charts)
{
  const s = pres.addSlide({ masterName: 'LIGHT' })
  s.addText('Measured on real people: bots are stopped, PIN thieves mostly stopped', { placeholder: 'title' })
  const common = { barDir: 'bar', showTitle: true, titleFontFace: H, titleFontSize: 14, titleColor: INK, showValue: true, dataLabelPosition: 'outEnd', dataLabelFontFace: B, dataLabelFontSize: 12, dataLabelColor: INK, catAxisLabelFontFace: B, catAxisLabelFontSize: 11, catAxisLabelColor: INK, catAxisLineShow: false, valAxisHidden: true, valAxisLineShow: false, valAxisMinVal: 0, valAxisMaxVal: 112, valGridLine: { style: 'none' }, catGridLine: { style: 'none' }, showLegend: false, catAxisOrientation: 'maxMin', barGapWidthPct: 55 }
  const ch = (title, labels, vals, colors, x, w) => s.addChart(pres.charts.BAR, [{ name: title, labels, values: vals }], Object.assign({}, common, { x, y: 1.75, w, h: 3.1, title, chartColors: colors }))
  ch('Bots caught, % (while 5% of unseen humans are flagged)', ['Even rhythm, exact center', 'Added timing noise', 'Replay, noise up to 10%', 'Samples the population'], [100, 100, 100, 61], [JADE, JADE, JADE, AMBER], 0.55, 4.6)
  ch('PIN-knowing impostors allowed, per 100', ['Rules only', 'Rules + learned models'], [89, 22], [CORAL, JADE], 5.25, 3.75)
  ch('Genuine owner passes silently, per 100', ['Same posture (sitting)', 'Posture changed (walking)'], [76, 49], [JADE, AMBER], 9.1, 3.75)
  const k = [['~4 ms', 'median scoring time in local\ntests, network excluded'], ['0', 'extra steps for the owner\nwhen the decision is allow'], ['Step-up', 'not block: the owner score\nis a risk signal']]
  k.forEach(([big, d], i) => {
    const x = 0.75 + i * 4.115
    T(s, big, { x, y: 5.0, w: 3.6, h: 0.65, fontFace: H, fontSize: 32, bold: true, color: i === 2 ? TEAL : INK, align: 'center' })
    T(s, d, { x, y: 5.7, w: 3.6, h: 0.5, fontSize: 12, color: MUTED, align: 'center' })
  })
  T(s, 'Public datasets: StrokePIN (97 people, 6-digit PIN) and Aalto typing. Bots come from our simulator. Full system: 5-fold by person, models retrained per fold. Not team-collected data.', { x: 0.75, y: 6.3, w: 11.8, h: 0.4, fontSize: 10, color: MUTED })
  s.addNotes('Bots: naive classes caught fully. Impostors: rules alone let 89 of 100 through, with learned models 22. Owner friction: 76 of 100 pass silently when posture matches.')
}

// ---- 8 Product (dark)
{
  const s = pres.addSlide({ masterName: 'DARK' })
  s.addText('Working today: SDK, scoring API, demo wallet and ops dashboard', { placeholder: 'title' })
  // laptop built from shapes + the real site screenshot
  const lx = 0.75, ly = 1.95, lw = 6.7, ih = (lw - 0.24) * 1103 / 2000
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: lx, y: ly, w: lw, h: ih + 0.24, rectRadius: 0.12, fill: { color: '0A1112' }, line: { color: '2C4547', width: 0.75 } })
  s.addImage({ path: A + 'innate-home.png', x: lx + 0.12, y: ly + 0.12, w: lw - 0.24, h: ih, altText: 'Innate website on a laptop' })
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: lx - 0.35, y: ly + ih + 0.24, w: lw + 0.7, h: 0.15, rectRadius: 0.06, fill: { color: 'C9D3D1' }, line: { color: 'C9D3D1', width: 0 } })
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.2, y: 1.95, w: 1.55, h: 1.55, rectRadius: 0.1, fill: { color: 'FFFFFF' }, line: { color: 'FFFFFF', width: 0 } })
  s.addImage({ path: A + 'qr-innate.png', x: 8.25, y: 2.0, w: 1.45, h: 1.45, altText: 'QR code for innate.odylytics.com' })
  T(s, URL, { x: 10.0, y: 2.1, w: 2.6, h: 0.45, fontFace: H, fontSize: 17, bold: true, color: 'FFFFFF' })
  T(s, 'Scan to open the demo wallet. No login needed.', { x: 10.0, y: 2.6, w: 2.55, h: 0.7, fontSize: 12, color: MUTED_D })
  const L = [['Guided story, 90 seconds', 'Owner allowed, malware held, PIN thief stepped up.'], ['Demo wallet', 'Enroll with PIN 159357, then play thief or malware.'], ['Scoring API and ops dashboard', 'Swagger for developers, labeled reasons for analysts.']]
  L.forEach(([h, d], i) => {
    const y = 3.85 + i * 0.85
    dot(s, 8.2, y + 0.07, MINT, 0.12)
    T(s, [{ text: h + '\n', options: { bold: true, color: 'FFFFFF', fontSize: 14, breakLine: false } }, { text: d, options: { color: MUTED_D, fontSize: 12 } }], { x: 8.45, y, w: 4.1, h: 0.75 })
  })
  T(s, '55 automated tests  ·  4-tactic bot simulator + adb  ·  every figure reruns from research/', { x: 0.75, y: 6.3, w: 11, h: 0.3, fontSize: 11, color: MUTED_D })
  s.addNotes('Everything shown is live at the URL. Scan the QR to try it.')
}

// ---- 9 Limits and next
{
  const s = pres.addSlide({ masterName: 'LIGHT' })
  s.addText('Where it stands, and what comes next', { placeholder: 'title' })
  cap(s, 'Known edges', 0.75, 1.75, 5)
  const E = [['Weak', CORAL, 'Human-like bots: replay with 15 to 30% noise\nand template-aware bots pass 48 to 82%.'], ['Limit', AMBER, 'Changing posture removes much of\nthe owner signal.'], ['Limit', AMBER, 'The web SDK cannot see text set\ndirectly; a native SDK can.'], ['Missing', MUTED, 'Team-collected data and real\nmalware sessions.']]
  E.forEach(([t, c, d], i) => {
    const y = 2.15 + i * 0.9
    if (i) hair(s, 0.75, y - 0.12, 5.6)
    T(s, t, { x: 0.75, y, w: 0.95, h: 0.3, fontFace: H, fontSize: 13, bold: true, color: c === AMBER ? '8A5F00' : c === CORAL ? 'B04436' : MUTED })
    T(s, d, { x: 1.8, y, w: 4.55, h: 0.6, fontSize: 13 })
  })
  T(s, 'So Innate steps up instead of blocking, and is one layer among several.', { x: 0.75, y: 5.85, w: 5.6, h: 0.4, fontSize: 12, color: MUTED })
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.85, y: 1.7, w: 5.73, h: 4.85, rectRadius: 0.12, fill: { color: MIST }, line: { color: MIST, width: 0 } })
  cap(s, 'Next', 7.2, 1.95, 4)
  const N = [['Real data', 'Consented volunteers and real bots, then\nretrain and recalibrate thresholds.'], ['Innate Challenge', 'Typing 30 keys instead of 6 cuts the impostor\npass rate from 81% to 49% (2,260 typists).'], ['Fine-tuned Transformer', 'TypeFormer on StrokePIN: EER 0.29 to 0.20, impostors\npassing 71% to 42% (30 unseen people). Planned for the API.'], ['Native SDK', 'Sees text set directly, plus a controlled\nre-enrollment flow.']]
  N.forEach(([h, d], i) => {
    const y = 2.4 + i * 1.0
    T(s, [{ text: h + '\n', options: { bold: true, fontSize: 14 } }, { text: d, options: { fontSize: 12, color: '2F4A4C' } }], { x: 7.2, y, w: 5.1, h: 0.95 })
  })
  s.addNotes('Be direct about the weak spots; they explain why the design steps up instead of blocking.')
}

// ---- 10 Close (dark)
{
  const s = pres.addSlide({ masterName: 'DARK' })
  s.addImage({ path: A + 'gesture-dark.png', x: 10.5, y: 3.7, w: 5.2, h: 5.2, altText: 'Innate gesture mark, cropped' })
  s.addText('Security the user never has to think about', { placeholder: 'title' })
  const C = [['Users', 'Protected on every transfer\nwith no extra steps. Asked\nfor more only when it looks off.'], ['The wallet', 'Catches what PIN, OTP and\ndevice checks cannot: right\ncredentials, wrong hands.'], ['Operations', 'Fewer vague alerts, more\nexplained evidence. Analyst\nlabels train the model.']]
  const CW = 11.83 / 3
  C.forEach(([h, d], i) => {
    const x = 0.75 + i * CW
    T(s, h, { x, y: 1.95, w: CW, h: 0.4, fontFace: H, fontSize: 18, bold: true, color: MINT, align: 'center' })
    T(s, d, { x, y: 2.5, w: CW, h: 1.0, fontSize: 14, color: 'DCE7E6', align: 'center' })
  })
  T(s, 'PIN is what you know.', { x: 0.75, y: 4.2, w: 11.83, h: 0.75, fontFace: H, fontSize: 38, bold: true, color: 'FFFFFF', align: 'center' })
  T(s, 'Innate is how you are.', { x: 0.75, y: 4.95, w: 11.83, h: 0.75, fontFace: H, fontSize: 38, bold: true, color: MINT, align: 'center' })
  T(s, URL + '  ·  Team Odylytics', { x: 0.75, y: 5.95, w: 11.83, h: 0.3, fontSize: 13, color: MUTED_D, align: 'center' })
  s.addNotes('Close on the line, then point to the QR on slide 8.')
}

;(async () => { await pres.writeFile({ fileName: OUT }); await applyTheme(OUT, THEME); console.log('wrote', OUT) })()
