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

const footer = (dark) => [{ image: { path: A + (dark ? 'lockup-dark.png' : 'lockup-ink.png'), x: 0.75, y: 6.8, w: 1.34, h: 1.34 / 5.0420 } }]
for (const [name, dark] of [['LIGHT', false], ['DARK', true]]) {
  pres.defineSlideMaster({
    title: name, background: { color: dark ? INK : CLOUD },
    objects: [
      ...footer(dark),
      { placeholder: { options: { name: 'title', type: 'title', x: 0.75, y: 0.78, w: 11.8, h: 1.0, fontFace: H, fontSize: 28, bold: true, color: dark ? 'FFFFFF' : INK, valign: 'top', align: 'left', margin: 0, fit: 'shrink' }, text: '' } },
    ],
    slideNumber: { x: 11.6, y: 6.78, w: 0.98, h: 0.3, fontFace: B, fontSize: 11, color: dark ? MUTED_D : MUTED, align: 'right' },
  })
}
pres.defineSlideMaster({ title: 'COVER', background: { path: A + 'bg-dark-gesture.png' }, objects: [] })
pres.defineSlideMaster({ title: 'DARKBG', background: { path: A + 'bg-dark-gesture.png' }, objects: [...footer(true), { placeholder: { options: { name: 'title', type: 'title', x: 0.75, y: 0.78, w: 11.8, h: 1.0, fontFace: H, fontSize: 28, bold: true, color: 'FFFFFF', valign: 'top', align: 'left', margin: 0, fit: 'shrink' }, text: '' } }], slideNumber: { x: 11.6, y: 6.78, w: 0.98, h: 0.3, fontFace: B, fontSize: 11, color: MUTED_D, align: 'right' } })

const T = (s, text, o) => s.addText(text, Object.assign({ isTextBox: true, fontFace: B, fontSize: 14, color: INK, margin: 0, valign: 'top' }, o))
const arrow = (s, x, y, color = JADE) => s.addShape(pres.shapes.RIGHT_ARROW, { x, y, w: 0.3, h: 0.2, fill: { color }, line: { color, width: 0 } })
const link = (s, x1, x2, y, color = JADE, pad = 0.14) => s.addShape(pres.shapes.LINE, { x: x1 + pad, y, w: x2 - x1 - 2 * pad, h: 0, line: { color, width: 1.5, endArrowType: 'triangle' } })
const hair = (s, x, y, w, color = STONE) => s.addShape(pres.shapes.LINE, { x, y, w, h: 0, line: { color, width: 0.75 } })
const vhair = (s, x, y, h, color = STONE) => s.addShape(pres.shapes.LINE, { x, y, w: 0, h, line: { color, width: 0.75 } })
const dot = (s, x, y, color, d = 0.14) => s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color }, line: { color, width: 0 } })
const head = (s, i, label, dark) => {
  T(s, [{ text: String(i).padStart(2, '0') + '   ', options: { bold: true, color: dark ? MINT : JADE } }, { text: label.toUpperCase(), options: { bold: true, color: dark ? MINT : TEAL } }], { x: 0.75, y: 0.42, w: 6, h: 0.26, fontFace: H, fontSize: 11, charSpacing: 2 })
  for (let k = 1; k <= 9; k++) { const c = k === i ? (dark ? MINT : JADE) : (dark ? '2C4547' : STONE); s.addShape(pres.shapes.OVAL, { x: 12.58 - (9 - k) * 0.2 - 0.1, y: 0.47, w: 0.1, h: 0.1, fill: { color: c }, line: { color: c, width: 0 } }) }
}
const src = (s, text, dark) => T(s, 'Sources: ' + text, { x: 2.45, y: 6.7, w: 8.95, h: 0.5, fontSize: 9, italic: true, color: dark ? MUTED_D : MUTED, valign: 'middle' })
const cap = (s, text, x, y, w, dark) => T(s, text.toUpperCase(), { x, y, w, h: 0.25, fontSize: 11, bold: true, charSpacing: 2, color: dark ? MINT : TEAL })

// ---- 1 Cover
{
  const s = pres.addSlide({ masterName: 'COVER' })
  s.addImage({ path: A + 'lockup-dark.png', x: 0.75, y: 0.6, w: 2.1, h: 2.1 / 5.0420, altText: 'innate' })
  s.addShape(pres.shapes.RECTANGLE, { x: 3.12, y: 0.62, w: 0.012, h: 0.4, fill: { color: '3A5557' }, line: { color: '3A5557', width: 0 } })
  T(s, 'Powered by', { x: 3.3, y: 0.62, w: 1.2, h: 0.4, fontSize: 13, color: MUTED_D, valign: 'middle' })
  s.addImage({ path: A + 'odylytics-on-dark.png', x: 4.45, y: 0.6, w: 1.4, h: 1.4 * 549 / 1813, altText: 'Odylytics' })
  cap(s, 'MoMo Tech Contest 2026  ·  Cybersecurity + Anti-fraud', 0.75, 2.2, 8, true)
  T(s, 'Silent human verification for every transfer', { x: 0.75, y: 2.6, w: 8.6, h: 2.0, fontFace: H, fontSize: 44, bold: true, color: 'FFFFFF', lineSpacingMultiple: 0.98 })
  T(s, 'Everyone taps a PIN in their own rhythm: how long the finger stays down, the gap between taps, where it lands. Innate learns that pattern and checks it silently on every transfer. The owner does nothing extra.', { x: 0.75, y: 4.4, w: 6.9, h: 1.2, fontSize: 16, color: MUTED_D, lineSpacingMultiple: 1.15 })
  T(s, 'Your behavior is your signature', { x: 0.75, y: 5.95, w: 7, h: 0.4, fontFace: H, fontSize: 20, bold: true, color: MINT })
  T(s, 'MoMo Tech Day: Imagine the Future Workspace', { x: 7.2, y: 6.95, w: 5.38, h: 0.3, fontSize: 11, color: MUTED_D, align: 'right' })
  s.addNotes('Open with the one-line promise: a layer that verifies the human at the moment of transfer, with no extra step for the owner.')
}

// ---- 2 Problem
{
  const s = pres.addSlide({ masterName: 'LIGHT' }); head(s, 1, 'Problem')
  s.addText("Fraud now arrives with the right PIN, on the owner's phone", { placeholder: 'title' })
  const lane = (y, tag, name, note, steps) => {
    T(s, tag, { x: 0.75, y, w: 0.5, h: 0.55, fontFace: H, fontSize: 30, bold: true, color: JADE })
    T(s, [{ text: name + '\n', options: { bold: true, fontFace: H, fontSize: 14 } }, { text: note, options: { fontSize: 11, color: MUTED } }], { x: 1.3, y: y + 0.05, w: 1.7, h: 1.1 })
    steps.forEach((t, i) => {
      const x = 3.2 + i * 2.05
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 1.75, h: 1.2, rectRadius: 0.1, fill: { color: 'FFFFFF' }, line: { color: STONE, width: 0.75 } })
      T(s, String(i + 1), { x: x + 0.15, y: y + 0.1, w: 0.3, h: 0.25, fontFace: H, fontSize: 11, bold: true, color: TEAL })
      T(s, t, { x: x + 0.15, y: y + 0.38, w: 1.5, h: 0.75, fontSize: 12.5 })
      link(s, x + 1.75, x + 2.05, y + 0.6, JADE, 0.04)
    })
  }
  lane(1.95, 'A', 'Remote-control malware', 'Families such as RemControl, ToxicPanda 2.0', ['A fake APK gets Accessibility access', 'It reads the screen and the OTP', 'It then taps the transfer itself'])
  lane(3.55, 'B', 'Someone who knows the PIN', 'A relative, a colleague, a thief', ['Sees or guesses the PIN', 'Holds the unlocked phone', 'Confirms the transfer'])
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 9.55, y: 1.95, w: 3.03, h: 2.8, rectRadius: 0.12, fill: { color: INK }, line: { color: INK, width: 0 } })
  T(s, "WHAT TODAY'S CHECKS SEE", { x: 9.8, y: 2.1, w: 2.6, h: 0.25, fontSize: 10, bold: true, charSpacing: 2, color: MINT })
  ;['Device is trusted', 'PIN is correct', 'OTP was entered', 'Session is valid'].forEach((t, i) => { dot(s, 9.8, 2.5 + i * 0.4 + 0.07, JADE, 0.12); T(s, t, { x: 10.05, y: 2.5 + i * 0.4, w: 2.4, h: 0.3, fontSize: 13, color: 'FFFFFF' }) })
  hair(s, 9.8, 4.15, 2.55, '2C4547')
  dot(s, 9.8, 4.3 + 0.05, CORAL, 0.14); T(s, 'Money leaves', { x: 10.05, y: 4.27, w: 2.4, h: 0.3, fontFace: H, fontSize: 14, bold: true, color: 'FFFFFF' })
  link(s, 8.95, 9.55, 2.55, JADE, 0.06); link(s, 8.95, 9.55, 4.15, JADE, 0.06)
  s.addShape(pres.shapes.RECTANGLE, { x: 0.75, y: 5.4, w: 11.83, h: 0.8, fill: { color: MIST }, line: { color: MIST, width: 0 } })
  T(s, 'Every check passes. None of them asks who is touching the screen.', { x: 0.75, y: 5.4, w: 11.83, h: 0.8, fontFace: H, fontSize: 19, bold: true, color: INK, valign: 'middle', align: 'center' })
  src(s, 'Fratantonio et al., Cloak and Dagger, IEEE S&P 2017; Naseri et al., AccessiLeaks, PoPETs 2019 (72% of top finance apps leak); Diao et al., RAID 2019; Malwarebytes, ToxicPanda 2.0 (Aug 2026).')
  s.addNotes('Two ways in, one blind spot. A: malware with Accessibility permission taps the transfer by itself. B: a person who knows the PIN. In both cases every credential check passes, so the wallet cannot tell who is touching the screen.')
}

// ---- 3 Solution
{
  const s = pres.addSlide({ masterName: 'LIGHT' }); head(s, 2, 'Solution')
  s.addText('Everyone taps the same PIN differently. Innate learns yours', { placeholder: 'title' })
  const hold = { A: [48.0, 57.0, 59.0, 57.0, 53.0, 49.0], B: [83.0, 88.0, 81.0, 74.0, 51.0, 69.0] }, gap = { A: [202.0, 209.0, 174.0, 166.0, 208.0], B: [232.0, 273.0, 205.0, 253.0, 194.0] }
  const common = { barDir: 'col', chartColors: [TEAL, JADE], showLegend: false, showTitle: false, showValue: false, catAxisLabelFontFace: B, catAxisLabelFontSize: 11, catAxisLabelColor: INK, catAxisLineShow: false, valAxisLabelFontFace: B, valAxisLabelFontSize: 10, valAxisLabelColor: MUTED, valAxisLineShow: false, valGridLine: { color: STONE, size: 0.5 }, catGridLine: { style: 'none' }, barGapWidthPct: 40, valAxisMinVal: 0 }
  T(s, 'Same PIN 147258, two people, real recordings', { x: 0.75, y: 1.9, w: 7.0, h: 0.3, fontFace: H, fontSize: 14, bold: true })
  ;[[TEAL, 'Person A', 0.75], [JADE, 'Person B', 2.0]].forEach(([c, t, x]) => { dot(s, x, 2.3 + 0.04, c, 0.13); T(s, t, { x: x + 0.2, y: 2.28, w: 1.0, h: 0.25, fontSize: 11, color: MUTED }) })
  T(s, 'Time the finger stays on the key (ms)', { x: 0.75, y: 2.65, w: 3.4, h: 0.25, fontSize: 11, bold: true, color: TEAL })
  s.addChart(pres.charts.BAR, [{ name: 'Person A', labels: ['1', '4', '7', '2', '5', '8'], values: hold.A }, { name: 'Person B', labels: ['1', '4', '7', '2', '5', '8'], values: hold.B }], Object.assign({}, common, { x: 0.65, y: 2.9, w: 3.65, h: 2.5, valAxisMaxVal: 100, valAxisMajorUnit: 25 }))
  T(s, 'Time between taps (ms)', { x: 4.5, y: 2.65, w: 3.4, h: 0.25, fontSize: 11, bold: true, color: TEAL })
  s.addChart(pres.charts.BAR, [{ name: 'Person A', labels: ['1-4', '4-7', '7-2', '2-5', '5-8'], values: gap.A }, { name: 'Person B', labels: ['1-4', '4-7', '7-2', '2-5', '5-8'], values: gap.B }], Object.assign({}, common, { x: 4.4, y: 2.9, w: 3.5, h: 2.5, valAxisMaxVal: 300, valAxisMajorUnit: 100 }))
  vhair(s, 8.3, 1.95, 3.5)
  cap(s, 'Evidence Innate reads', 8.7, 1.95, 3.9)
  const R_ = [['PIN rhythm', 'hold time, gap, landing spot on each key'], ['Transfer form', 'typed, pasted or set by a script'], ['Touch and swipe', 'a finger, or machine-uniform strokes'], ['Context', 'new recipient, unusual amount']]
  R_.forEach(([h, d_], i) => {
    const y = 2.4 + i * 0.7
    T(s, String(i + 1), { x: 8.7, y, w: 0.35, h: 0.4, fontFace: H, fontSize: 18, bold: true, color: JADE })
    T(s, [{ text: h + '\n', options: { bold: true, fontSize: 14 } }, { text: d_, options: { fontSize: 12, color: MUTED } }], { x: 9.15, y, w: 3.4, h: 0.62 })
  })
  T(s, 'Unsure? A short typed phrase adds signal.', { x: 8.7, y: 5.2, w: 3.9, h: 0.3, fontSize: 11.5, italic: true, color: MUTED })
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.75, y: 5.75, w: 11.83, h: 0.62, rectRadius: 0.08, fill: { color: MIST }, line: { color: MIST, width: 0 } })
  T(s, [{ text: 'One risk score, not four gates in a row. ', options: { bold: true } }, { text: 'Four gates at 95% each would block nearly 1 in 5 genuine owners (1 - 0.95^4).' }], { x: 0.75, y: 5.75, w: 11.83, h: 0.62, fontSize: 13, align: 'center', valign: 'middle' })
  src(s, 'Chart: two StrokePIN participants (Yao & Wang, IEEE TDSC 2026), 5 sitting entries each, pair at the 75th percentile of separation; different phones, illustrative. Zheng et al., ICNP 2014. Channels: Innate backend features.')
  s.addNotes('Same PIN, two people: the pattern of hold times and gaps is different and stable. Innate learns the owner pattern and checks it silently.')
}

// ---- 4 How it works
{
  const s = pres.addSlide({ masterName: 'LIGHT' }); head(s, 3, 'How it works')
  s.addText('One transfer, and the owner notices nothing', { placeholder: 'title' })
  s.addImage({ path: S + 'wallet-pad.png', x: 0.75, y: 1.7, w: 2.95, h: 2.95 * 610 / 400, altText: 'Demo wallet with the Innate SDK on the PIN pad' })
  T(s, 'Demo wallet with the SDK on the PIN pad', { x: 0.75, y: 6.3, w: 2.95, h: 0.25, fontSize: 10, color: MUTED, align: 'center' })
  const X0 = 4.35, CW = 2.08
  const steps = [['1', 'Enter amount', 'The normal\ntransfer form.'], ['2', 'Tap the PIN', 'Timing and touch only.\nNever the digits.'], ['3', 'Confirm', 'The wallet calls\nInnate once.'], ['4', 'Innate scores', 'About 4 ms in tests,\nwith reasons.']]
  steps.forEach(([n, h, d], i) => {
    const x = X0 + i * CW, cx = x + CW / 2
    s.addShape(pres.shapes.OVAL, { x: cx - 0.21, y: 1.75, w: 0.42, h: 0.42, fill: { color: i === 3 ? JADE : INK }, line: { color: i === 3 ? JADE : INK, width: 0 } })
    T(s, n, { x: cx - 0.21, y: 1.75, w: 0.42, h: 0.42, fontFace: H, fontSize: 13, bold: true, color: i === 3 ? INK : 'FFFFFF', align: 'center', valign: 'middle' })
    if (i < 3) link(s, cx + 0.21, cx + CW - 0.21, 1.96, STONE)
    T(s, h, { x, y: 2.3, w: CW, h: 0.35, fontFace: H, fontSize: 15, bold: true, align: 'center' })
    T(s, d, { x, y: 2.72, w: CW, h: 0.55, fontSize: 12, color: MUTED, align: 'center' })
  })
  hair(s, X0, 3.55, 8.23)
  cap(s, 'Then one of three things happens', X0, 3.72, 8.23)
  const OW = 2.74
  const out = [[JADE, 'allow', 'The owner sees nothing.\nThe transfer completes\nas usual.'], [AMBER, 'step_up', "Doubtful: the wallet's\nexisting face or OTP,\nor a typed phrase."], [CORAL, 'hold', 'Bot-like: transfer paused,\nuser alerted, ops reviews\nthe reasons.']]
  out.forEach(([c, h, d], i) => {
    const x = X0 + i * OW, cx = x + OW / 2
    dot(s, cx - 0.07, 4.22, c)
    T(s, h, { x, y: 4.47, w: OW, h: 0.35, fontFace: H, fontSize: 17, bold: true, align: 'center' })
    T(s, d, { x, y: 4.9, w: OW, h: 0.8, fontSize: 13, color: MUTED, align: 'center' })
  })
  T(s, [{ text: 'Enrollment is the PIN taps users already make. ', options: { bold: true } }, { text: 'The first 3 to 5 normal uses build the habit template, with no setup screen. Bot detection needs no enrollment.' }], { x: X0, y: 5.85, w: 8.23, h: 0.55, fontSize: 12, align: 'center' })
  src(s, 'Step-up is standard risk-based authentication: Wiefling et al., IFIP SEC 2019 and ACSAC 2020 (RBA is easier to use than 2FA). Latency: team benchmark E26, 300 requests, local, network excluded.')
  s.addNotes('Walk the four steps; the owner only ever types the PIN. Branches map to flows the wallet already runs.')
}

// ---- 5 What changes for the wallet
{
  const s = pres.addSlide({ masterName: 'LIGHT' }); head(s, 4, 'What changes for the wallet')
  s.addText('Stolen credentials stop being enough, and the owner still sees nothing', { placeholder: 'title' })
  const X = [0.75, 4.0, 7.9], W = [3.0, 3.6, 4.68]
  ;[['Case', 0], ['Today: PIN + OTP + device checks', 1], ['With Innate underneath', 2]].forEach(([t, i]) => cap(s, t, X[i], 1.95, W[i]))
  hair(s, 0.75, 2.3, 11.83, INK)
  const rows = [
    ['Remote-control malware', 'taps the transfer by itself', 'Passes. The app, PIN and device are all the victim\'s.', CORAL, 'hold', 'Machine rhythm, exact key centers. Transfer paused, user alerted.'],
    ['Someone who knows the PIN', 'a relative, a thief', 'Passes. The PIN is correct.', AMBER, 'step_up', 'Rhythm does not match the owner. Face or OTP before money moves.'],
    ['The real owner', 'every normal transfer', 'Passes, no friction.', JADE, 'allow', 'Matches the habit. Nothing changes. If unsure: the usual step-up, never a block.'],
  ]
  rows.forEach(([c, cs, today, col, act, what], i) => {
    const y = 2.5 + i * 1.05
    if (i) hair(s, 0.75, y - 0.12, 11.83)
    T(s, [{ text: c + '\n', options: { bold: true, fontFace: H, fontSize: 15 } }, { text: cs, options: { fontSize: 12, color: MUTED } }], { x: X[0], y, w: W[0], h: 0.85 })
    T(s, today, { x: X[1], y, w: W[1], h: 0.85, fontSize: 13, color: MUTED })
    dot(s, X[2], y + 0.07, col, 0.14)
    T(s, [{ text: act + '\n', options: { bold: true, fontFace: H, fontSize: 15 } }, { text: what, options: { fontSize: 12.5 } }], { x: X[2] + 0.28, y, w: W[2] - 0.28, h: 0.95 })
  })
  cap(s, 'How it plugs in', 0.75, 5.75, 3)
  const st = [['1', 'SDK on the PIN pad and transfer form'], ['2', 'One API call at the confirm step'], ['3', 'Map actions to your existing flows']]
  const SW = 3.45, SG = (11.83 - 3 * SW) / 2
  st.forEach(([n, t], i) => {
    const x = 0.75 + i * (SW + SG)
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 6.05, w: SW, h: 0.4, rectRadius: 0.08, fill: { color: MIST }, line: { color: MIST, width: 0 } })
    T(s, [{ text: n + '   ', options: { bold: true, color: TEAL, fontFace: H } }, { text: t }], { x, y: 6.05, w: SW, h: 0.4, fontSize: 11.5, align: 'center', valign: 'middle' })
    if (i < 2) link(s, x + SW, x + SW + SG, 6.25)
  })
  src(s, 'Decision mix per group: team experiment E29 (slide 8). Step-up as standard practice: Wiefling et al., IFIP SEC 2019. Integration: Innate scoring API, Swagger at nhip-api-taupe.vercel.app/docs.')
  s.addNotes('Use this as the talk track for the wallet. Before: three very different people all look identical to the wallet because every credential passes. After: Innate separates them silently underneath. Malware is held, a PIN thief is asked for face or OTP, the owner sees nothing. Integration is three small steps and maps onto flows the wallet already runs. Numbers for each group are on slide 8.')
}

// ---- 6 Product (dark)
{
  const s = pres.addSlide({ masterName: 'DARK' }); head(s, 5, 'Product', true)
  s.addText('Working today: SDK, scoring API, demo wallet and ops dashboard', { placeholder: 'title' })
  const lx = 0.75, ly = 2.0, lw = 6.7, ih = (lw - 0.24) * 1103 / 2000
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: lx, y: ly, w: lw, h: ih + 0.24, rectRadius: 0.12, fill: { color: '0A1112' }, line: { color: '2C4547', width: 0.75 } })
  s.addImage({ path: A + 'innate-home.png', x: lx + 0.12, y: ly + 0.12, w: lw - 0.24, h: ih, altText: 'Innate website on a laptop' })
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: lx - 0.35, y: ly + ih + 0.24, w: lw + 0.7, h: 0.15, rectRadius: 0.06, fill: { color: 'C9D3D1' }, line: { color: 'C9D3D1', width: 0 } })
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.2, y: 2.0, w: 1.55, h: 1.55, rectRadius: 0.1, fill: { color: 'FFFFFF' }, line: { color: 'FFFFFF', width: 0 } })
  s.addImage({ path: A + 'qr-innate.png', x: 8.25, y: 2.05, w: 1.45, h: 1.45, altText: 'QR code for innate.odylytics.com' })
  T(s, URL, { x: 10.0, y: 2.15, w: 2.6, h: 0.45, fontFace: H, fontSize: 17, bold: true, color: 'FFFFFF' })
  T(s, 'Scan to open the demo wallet. No login needed.', { x: 10.0, y: 2.65, w: 2.55, h: 0.7, fontSize: 12, color: MUTED_D })
  const L = [['Guided story, 90 seconds', 'Owner allowed, malware held, PIN thief stepped up.'], ['Demo wallet', 'Enroll with PIN 159357, then play thief or malware.'], ['Scoring API and ops dashboard', 'Swagger for developers, labeled reasons for analysts.']]
  L.forEach(([h, d], i) => {
    const y = 3.9 + i * 0.85
    dot(s, 8.2, y + 0.07, MINT, 0.12)
    T(s, [{ text: h + '\n', options: { bold: true, color: 'FFFFFF', fontSize: 14 } }, { text: d, options: { color: MUTED_D, fontSize: 12 } }], { x: 8.45, y, w: 4.1, h: 0.75 })
  })
  T(s, '55 automated tests  ·  4-tactic bot simulator + adb  ·  every figure reruns from research/', { x: 0.75, y: 6.3, w: 11, h: 0.3, fontSize: 11, color: MUTED_D })
  src(s, 'Live product at innate.odylytics.com; tests: backend 43, bot simulator 8, phone input SDK 4; experiments E1 to E31 in research/EXPERIMENTS.md.', true)
  s.addNotes('Everything shown is live at the URL. Scan the QR to try it.')
}

// ---- 7 AI and research basis
{
  const s = pres.addSlide({ masterName: 'LIGHT' }); head(s, 6, 'AI and research basis')
  s.addText('Three checks, one explainable decision, each grounded in published work', { placeholder: 'title' })
  const cols = [['1', 'Human or bot?', 'Even rhythm, exact key centers,\ntext set directly, no touch.', 'Rules + LightGBM trained on\nreal people and simulated bots.', 'Touch-only bot detection reaches\nabout 60%, with motion 80 to 90%\n(BeCAPTCHA, EAAI 2021).'], ['2', 'The owner?', 'PIN hold times, gaps and tap offsets\nagainst 3 to 5 enrollment sessions.', 'Normalized distance, population\nshrinkage, LightGBM on deviations.', 'Scaled Manhattan: EER 9.6%, best\nof 14 detectors (Killourhy &\nMaxion, DSN 2009).'], ['3', 'A replay?', "A session nearly identical to\nthe account's own recent ones.", 'Distance to the 50 latest\nsessions of the account.', 'Template poisoning succeeds over\n70% with under 10 injections\n(Lovisotto, EuroS&P 2020).']]
  const CW = 11.83 / 3
  cols.forEach(([n, h, d, m, r], i) => {
    const x = 0.75 + i * CW
    if (i) vhair(s, x, 1.95, 3.15)
    T(s, n, { x, y: 1.9, w: CW, h: 0.55, fontFace: H, fontSize: 32, bold: true, color: JADE, align: 'center' })
    T(s, h, { x, y: 2.45, w: CW, h: 0.35, fontFace: H, fontSize: 19, bold: true, align: 'center' })
    T(s, d, { x, y: 2.9, w: CW, h: 0.55, fontSize: 13, align: 'center' })
    T(s, [{ text: 'Method\n', options: { bold: true, color: TEAL } }, { text: m }], { x, y: 3.6, w: CW, h: 0.65, fontSize: 11.5, color: MUTED, align: 'center' })
    T(s, [{ text: 'Backed by\n', options: { bold: true, color: TEAL } }, { text: r }], { x, y: 4.3, w: CW, h: 0.8, fontSize: 11, color: MUTED, align: 'center' })
  })
  const PW = 3.3, PG = (11.83 - 3 * PW) / 2
  ;[['Weighted risk score', false], ['allow  ·  step_up  ·  hold', true], ['A plain reason per signal', false]].forEach(([t, ink], i) => {
    const x = 0.75 + i * (PW + PG)
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 5.4, w: PW, h: 0.58, rectRadius: 0.08, fill: { color: ink ? INK : MIST }, line: { color: ink ? INK : MIST, width: 0 } })
    T(s, t, { x, y: 5.4, w: PW, h: 0.58, fontFace: H, fontSize: 14, bold: true, color: ink ? 'FFFFFF' : INK, align: 'center', valign: 'middle' })
    if (i < 2) link(s, x + PW, x + PW + PG, 5.69)
  })
  T(s, 'No LLM sits on the decision path. Templates keep means and spreads only, never the PIN, amount or text.', { x: 0.75, y: 6.2, w: 11.83, h: 0.3, fontSize: 12, color: MUTED, align: 'center' })
  src(s, 'Acien et al., BeCAPTCHA, EAAI 2021; Killourhy & Maxion, DSN 2009; Lovisotto et al., EuroS&P 2020; Ke et al., LightGBM, NeurIPS 2017; Freeman et al., Who Are You?, NDSS 2016 (weighted risk score, AUC 0.955).')
  s.addNotes('Each check maps to a published result; the numbers shown are from those papers, not ours.')
}

// ---- 8 Evidence (doughnuts)
{
  const s = pres.addSlide({ masterName: 'LIGHT' }); head(s, 7, 'Evidence')
  s.addText('On 97 real people, the right outcome wins in every group', { placeholder: 'title' })
  const D = [
    ['Genuine owner\nsitting, n = 1,164', [76, 23, 1], '76%', 'passes silently', 'Walking instead of sitting: 49% allowed'],
    ['PIN-knowing impostor\nn = 2,328', [22, 77, 1], '78%', 'stopped or asked', 'Rules only, no learned model: 89% allowed'],
    ['Naive bots: even, noisy,\nreplay within 5%', [0, 0, 100], '100%', 'held', 'Replay within 10% also 100% held'],
    ['Bot sampling the\nhuman population', [3, 65, 32], '97%', 'stopped or asked', 'The hardest naive bot'],
  ]
  const W = 11.83 / 4
  D.forEach(([t, v, big, sub, note], i) => {
    const x = 0.75 + i * W
    T(s, t, { x, y: 1.9, w: W, h: 0.5, fontFace: H, fontSize: 13, bold: true, align: 'center' })
    s.addChart(pres.charts.DOUGHNUT, [{ name: t, labels: ['allow', 'step_up', 'hold'], values: v }], { x: x + 0.2, y: 2.45, w: W - 0.4, h: 2.35, holeSize: 66, chartColors: [JADE, AMBER, CORAL], showLegend: false, showLabel: false, showPercent: false, showValue: false, showTitle: false, dataBorder: { pt: 1, color: 'F5FBF9' } })
    T(s, big, { x, y: 3.3, w: W, h: 0.5, fontFace: H, fontSize: 24, bold: true, align: 'center' })
    T(s, sub, { x, y: 3.78, w: W, h: 0.25, fontSize: 11, color: MUTED, align: 'center' })
    T(s, `allow ${v[0]}  ·  step_up ${v[1]}  ·  hold ${v[2]}`, { x, y: 4.9, w: W, h: 0.25, fontSize: 11, bold: true, align: 'center' })
    T(s, note, { x: x + 0.1, y: 5.2, w: W - 0.2, h: 0.4, fontSize: 11, color: MUTED, align: 'center' })
  })
  ;[[JADE, 'allow'], [AMBER, 'step_up'], [CORAL, 'hold']].forEach(([c, t], i) => { const x = 5.35 + i * 1.2; dot(s, x, 5.93 + 0.05, c, 0.12); T(s, t, { x: x + 0.2, y: 5.93, w: 0.9, h: 0.25, fontSize: 11, color: MUTED }) })
  T(s, 'Share of sessions, %. Owner sessions that are asked for more get the wallet\'s usual face or OTP, never a block.', { x: 0.75, y: 6.25, w: 11.83, h: 0.3, fontSize: 12, color: MUTED, align: 'center' })
  src(s, 'Team experiment E29 on StrokePIN (Yao & Wang, IEEE TDSC 2026, DOI 10.21227/thft-4721), 97 people, 5-fold CV by person, models retrained per fold; bots from the team simulator. Protocol after Georgiev et al., FETA, 2022.')
  s.addNotes('Doughnuts show the decision mix per group. Impostor: 22% pass with learned models, 89% with rules alone. Owner friction is a step-up, not a block.')
}

// ---- 9 Roadmap and limits
{
  const s = pres.addSlide({ masterName: 'LIGHT' }); head(s, 8, 'Limits and roadmap')
  s.addText('Where it stands, and what comes next', { placeholder: 'title' })
  cap(s, 'Known edges', 0.75, 1.9, 5)
  const E = [['Weak', CORAL, 'Human-like bots: replay with 15 to 30% noise\nand template-aware bots pass 48 to 82%.'], ['Limit', AMBER, 'Changing posture removes much of\nthe owner signal.'], ['Limit', AMBER, 'The web SDK cannot see text set\ndirectly; a native SDK can.'], ['Missing', MUTED, 'Team-collected data and real\nmalware sessions.']]
  E.forEach(([t, c, d], i) => {
    const y = 2.3 + i * 0.9
    if (i) hair(s, 0.75, y - 0.12, 5.6)
    T(s, t, { x: 0.75, y, w: 0.95, h: 0.3, fontFace: H, fontSize: 13, bold: true, color: c === AMBER ? '8A5F00' : c === CORAL ? 'B04436' : MUTED })
    T(s, d, { x: 1.8, y, w: 4.55, h: 0.6, fontSize: 13 })
  })
  T(s, 'So Innate steps up instead of blocking, and is one layer among several.', { x: 0.75, y: 5.95, w: 5.6, h: 0.4, fontSize: 12, color: MUTED })
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.85, y: 1.8, w: 5.73, h: 4.75, rectRadius: 0.12, fill: { color: MIST }, line: { color: MIST, width: 0 } })
  cap(s, 'Next', 7.2, 2.0, 4)
  const N = [['Real data', 'Consented volunteers and real bots, then retrain.'], ['Fine-tuned Transformer', 'TypeFormer on StrokePIN: EER 0.29 to 0.20 on 30 unseen\npeople. Planned for the API.'], ['Native SDK', 'Sees text set directly and device motion (a phone lying still while taps arrive).']]
  N.forEach(([h, d], i) => {
    const y = 2.4 + i * 0.78
    T(s, [{ text: h + '\n', options: { bold: true, fontSize: 13 } }, { text: d, options: { fontSize: 11.5, color: '2F4A4C' } }], { x: 7.2, y, w: 5.1, h: 0.75 })
  })
  T(s, [{ text: 'Innate Challenge: ', options: { bold: true, fontSize: 13 } }, { text: 'impostor pass rate by keys typed, %', options: { fontSize: 11.5, color: '2F4A4C' } }], { x: 7.2, y: 4.78, w: 5.1, h: 0.3 })
  s.addChart(pres.charts.BAR, [{ name: 'Impostor pass rate', labels: ['6 keys (PIN)', '10 keys', '20 keys', '30 keys'], values: [81, 73, 59, 49] }], { x: 7.1, y: 5.0, w: 5.35, h: 1.5, barDir: 'bar', chartColors: [CORAL, CORAL, AMBER, JADE], showLegend: false, showTitle: false, showValue: true, dataLabelPosition: 'outEnd', dataLabelFontFace: B, dataLabelFontSize: 11, dataLabelColor: INK, catAxisLabelFontFace: B, catAxisLabelFontSize: 10, catAxisLabelColor: INK, catAxisLineShow: false, valAxisHidden: true, valAxisLineShow: false, valAxisMinVal: 0, valAxisMaxVal: 100, valGridLine: { style: 'none' }, catGridLine: { style: 'none' }, catAxisOrientation: 'maxMin', barGapWidthPct: 45 })
  src(s, 'Innate Challenge: Aalto typing37k (Palin et al., MobileHCI 2019), 2,260 typists, timing only. TypeFormer: Stragapede et al., 2023. Adaptive attackers: Wang et al., ActReal, 2026 (preprint); Tey et al., NDSS 2013.')
  s.addNotes('Be direct about the weak spots; they explain why the design steps up instead of blocking.')
}

// ---- 10 Impact (dark)
{
  const s = pres.addSlide({ masterName: 'DARKBG' }); head(s, 9, 'Impact', true)
  s.addText('Security the user never has to think about', { placeholder: 'title' })
  const C = [['Users', 'Protected on every transfer\nwith no extra steps. Asked\nfor more only when it looks off.'], ['The wallet', 'Catches what PIN, OTP and\ndevice checks cannot: right\ncredentials, wrong hands.'], ['Operations', 'Fewer vague alerts, more\nexplained evidence. Analyst\nlabels train the model.']]
  const CW = 11.83 / 3
  C.forEach(([h, d], i) => {
    const x = 0.75 + i * CW
    T(s, h, { x, y: 2.0, w: CW, h: 0.4, fontFace: H, fontSize: 18, bold: true, color: MINT, align: 'center' })
    T(s, d, { x, y: 2.55, w: CW, h: 1.0, fontSize: 14, color: 'DCE7E6', align: 'center' })
  })
  T(s, 'PIN is what you know.', { x: 0.75, y: 4.2, w: 11.83, h: 0.75, fontFace: H, fontSize: 38, bold: true, color: 'FFFFFF', align: 'center' })
  T(s, 'Innate is how you are.', { x: 0.75, y: 4.95, w: 11.83, h: 0.75, fontFace: H, fontSize: 38, bold: true, color: MINT, align: 'center' })
  T(s, URL + '  ·  Team Odylytics', { x: 0.75, y: 5.95, w: 11.83, h: 0.3, fontSize: 13, color: MUTED_D, align: 'center' })
  s.addNotes('Close on the line, then point to the QR on slide 6.')
}

;(async () => { await pres.writeFile({ fileName: OUT }); await applyTheme(OUT, THEME); console.log('wrote', OUT) })()
