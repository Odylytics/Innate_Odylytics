import { useContext, useEffect, useRef, useState, type PointerEvent as RPointerEvent } from 'react'
import { ApiError, api, explanationText, reasonText, type AccountStatus, type CollectionMeta, type Posture, type Score, type SessionIn, type UserStatus } from './api'
import { MAX_ENROLL, MIN_JUDGE_ENROLL, impostorStopped } from './enrollCurve'
import { Recorder } from './capture'
import { LangContext } from './i18n'
import { canPromptInstall, isIOS, isInstalled, isPhone, onInstallChange, promptInstall } from './device'
import { AppIcon } from './landing/ui'
import qrcode from 'qrcode-generator'
import './collect.css'

// Data-collection app (#/collect), the phone entry of the project: sign up (one account per email, password hashed on the server)
// or sign in; then the rhythm set-up, a 10-digit pad (+ delete) where the volunteer creates a 6-digit PIN and types it 5 to 10 times,
// each entry sent and enrolled at once, with the Accuracy check bar under the keypad (enrollCurve.ts); then transfers confirmed
// with the PIN and scored live against that rhythm. Every session carries a self-reported posture (sit/stand/walk, E33); set-up sessions
// carry name + email; transfer sessions carry who typed (owner = genuine, someone else = impostor with a random participant id).
// The PIN digits are stored on purpose (pin_taps[].key, for per-key research); the form warns not to reuse a real one.
// Phone only: on a desktop it shows a "open on your phone" notice (add ?dev=1 to test in devtools).
const PIN_LEN = 6
const KEYS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '', '0', '⌫']
const CONTACT = import.meta.env.VITE_COLLECT_CONTACT as string | undefined
const EMAIL = /^[^@\s]+@[^@\s]+\.[^@\s]+$/

/** the site language (LangContext from App.tsx); tx(english, vietnamese) picks one */
function useTx() {
  const { lang } = useContext(LangContext)
  return (en: string, vi: string) => (lang === 'en' ? en : vi)
}

// shown when the build has no SDK key (VITE_SDK_KEY) or the API rejects it: nothing could ever be saved
const NO_KEY = ['This build has no API key configured. Tell the team.', 'Bản này chưa cấu hình khoá API. Báo cho đội.'] as const
const isKeyError = (e: unknown) => e instanceof ApiError && (e.status === 401 || e.status === 403)

// Stable id from the email (cyrb53), so all sessions of one person group together.
function idOf(email: string) {
  let h1 = 0xdeadbeef, h2 = 0x41c6ce57
  for (const c of email.toLowerCase()) {
    const k = c.codePointAt(0)!
    h1 = Math.imul(h1 ^ k, 2654435761); h2 = Math.imul(h2 ^ k, 1597334677)
  }
  h1 = Math.imul(h1 ^ (h1 >>> 16), 2246822507) ^ Math.imul(h2 ^ (h2 >>> 13), 3266489909)
  h2 = Math.imul(h2 ^ (h2 >>> 16), 2246822507) ^ Math.imul(h1 ^ (h1 >>> 13), 3266489909)
  return 'e' + (4294967296 * (2097151 & h2) + (h1 >>> 0)).toString(16)
}


// Signed-in account: kept on this phone only (never the password), so the next visit goes straight to the transfer.
const ACCOUNT_KEY = 'innate.collectAccount'
const loadAccount = (): AccountStatus | null => { try { return JSON.parse(localStorage.getItem(ACCOUNT_KEY) ?? 'null') } catch { return null } }
const saveAccount = (a: AccountStatus | null) => { try { if (a) localStorage.setItem(ACCOUNT_KEY, JSON.stringify(a)); else localStorage.removeItem(ACCOUNT_KEY) } catch { /* private mode */ } }
const enrolling = (a: AccountStatus) => !a.template_ready || a.enroll_open === true

export default function Collect() {
  const tx = useTx()
  useEffect(() => {
    const html = document.documentElement
    html.dataset.page = 'collect'
    const robots = document.createElement('meta'); robots.name = 'robots'; robots.content = 'noindex'
    document.head.appendChild(robots)
    // browser / status bar colour matches this light app while it is shown
    const theme = document.querySelector('meta[name="theme-color"]')
    const prevTheme = theme?.getAttribute('content') ?? null
    theme?.setAttribute('content', '#f3f5f8')
    return () => { delete html.dataset.page; robots.remove(); if (theme && prevTheme) theme.setAttribute('content', prevTheme) }
  }, [])
  const dev = new URLSearchParams(window.location.hash.split('?')[1] ?? '').get('dev') === '1'
  const [phone, setPhone] = useState(() => dev || isPhone())
  useEffect(() => {
    const on = () => setPhone(dev || isPhone())
    window.addEventListener('resize', on)
    return () => window.removeEventListener('resize', on)
  }, [dev])
  const [account, setAccountState] = useState<AccountStatus | null>(loadAccount)
  const setAccount = (a: AccountStatus | null) => { saveAccount(a); setAccountState(a) }

  if (!phone) return <PhoneGate />
  if (!account) return <Start onDone={setAccount} />
  const strip = (right: string) => (
    <div className="cl-strip"><span>{account.full_name || account.email}</span>
      <span><b>{right}</b> · <button className="cl-link cl-out" onClick={() => setAccount(null)}>{tx('Sign out', 'Đăng xuất')}</button></span></div>
  )
  if (enrolling(account)) return <EnrollRounds account={account} onStatus={(st) => setAccount({ ...account, ...st })} strip={strip} />
  return <Transfer account={account} strip={strip} />
}

function Start({ onDone }: { onDone: (a: AccountStatus) => void }) {
  const tx = useTx()
  const [mode, setMode] = useState<'signup' | 'login'>('signup')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [ok, setOk] = useState(false)
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState<string | null>(null)
  const n = name.trim().replace(/\s+/g, ' '), m = email.trim().toLowerCase()
  const valid = EMAIL.test(m) && m.length <= 254 && password.length >= (mode === 'signup' ? 6 : 1)
    && (mode === 'login' || (n.length >= 2 && n.length <= 100 && !/\d/.test(n) && ok))

  async function submit() {
    setBusy(true); setErr(null)
    try {
      if (mode === 'signup') {
        const a = await api.signup({ email: m, password, full_name: n })
        // research link (participants table), as before; the account works even if this fails
        await api.registerParticipant({ participant_id: idOf(m), email: m, full_name: n }).catch(() => undefined)
        onDone(a)
      } else onDone(await api.login({ email: m, password }))
    } catch (e) {
      const st = e instanceof ApiError ? e.status : -1
      setErr(st === 409 ? tx('This email already has an account. Sign in instead.', 'Email này đã có tài khoản. Hãy đăng nhập.')
        : st === 401 && mode === 'login' ? tx('Wrong email or password.', 'Sai email hoặc mật khẩu.')
        : isKeyError(e) ? tx(...NO_KEY)
        : st === 0 ? tx('No connection. Check your network.', 'Không có mạng. Kiểm tra kết nối.')
        : `${tx('Error', 'Lỗi')} ${st}`)
    } finally { setBusy(false) }
  }

  return (
    <div className="cl cl-page">
      <AppBar />
      <InstallHint />
      <h1>{tx('Touch data collection', 'Thu thập dữ liệu thao tác')}</h1>
      <div className="cl-tabs" role="tablist">
        {(['signup', 'login'] as const).map((k) => (
          <button key={k} role="tab" aria-selected={mode === k} className={mode === k ? 'on' : ''} onClick={() => { setMode(k); setErr(null) }}>
            {k === 'signup' ? tx('Sign up', 'Đăng ký') : tx('Sign in', 'Đăng nhập')}</button>
        ))}
      </div>
      {mode === 'signup' && <label className="cl-field"><span>{tx('Full name', 'Họ và tên')}</span>
        <input value={name} onChange={(e) => setName(e.target.value)} autoComplete="name" maxLength={100} /></label>}
      <label className="cl-field"><span>Email</span>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" inputMode="email"
          autoCapitalize="none" autoCorrect="off" spellCheck={false} maxLength={254} /></label>
      <label className="cl-field"><span>{tx('Password', 'Mật khẩu')}</span>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} maxLength={128}
          autoComplete={mode === 'signup' ? 'new-password' : 'current-password'} /></label>
      {mode === 'signup' && <>
        <p className="cl-note">{tx(`One account per email. Make up a 6-digit PIN and type it ${MIN_JUDGE_ENROLL} to ${MAX_ENROLL} times; the bar under the keypad shows how well Innate can tell you apart. `, `Mỗi email một tài khoản. Bạn tự đặt một mã PIN 6 số rồi nhập ${MIN_JUDGE_ENROLL} đến ${MAX_ENROLL} lần; thanh dưới bàn phím cho biết Innate nhận ra bạn tốt đến đâu. `)}
          <b>{tx('The PIN is stored', 'Mã PIN được lưu lại')}</b>{tx(' for research, so it ', ' để nghiên cứu, nên ')}
          <b>{tx('must not match', 'không được trùng')}</b>{tx(' any password or PIN you really use. Use a new password here too.',
            ' với mật khẩu hay mã PIN nào bạn đang dùng. Mật khẩu ở đây cũng nên là mật khẩu mới.')}</p>
        <details className="cl-more"><summary>{tx('What we collect and how we use it', 'Chúng tôi thu gì và dùng thế nào')}</summary>
          <ul>
            <li>{tx('Collected: full name, email, a password (stored only as a hash), the practice PIN you make up, and the time, position and contact size of each tap. No phone number, photos, voice, location or messages.',
              'Thu: họ tên, email, mật khẩu (chỉ lưu dạng băm), mã PIN thử bạn đặt, thời điểm, vị trí và kích thước vùng chạm khi gõ. Không thu số điện thoại, ảnh, giọng nói, vị trí hay tin nhắn.')}</li>
            <li>{tx('Purpose: to train and evaluate the bot-detection and account-owner models of the Innate product (MoMo Tech Contest 2026); only aggregate figures are published.',
              'Mục đích: huấn luyện và đánh giá mô hình phát hiện bot và nhận ra chủ tài khoản của sản phẩm Innate (MoMo Tech Contest 2026); chỉ công bố số liệu tổng hợp.')}</li>
            <li>{tx('Stored in the team database, never sold or shared with third parties. You can withdraw, view or ask for deletion of your data at any time: contact ', 'Lưu trong cơ sở dữ liệu của đội, không bán hay chia cho bên thứ ba. Bạn có thể rút lui, xem hoặc yêu cầu xoá dữ liệu bất cứ lúc nào: liên hệ ')}{CONTACT ?? tx('the person who invited you', 'người mời bạn tham gia')}.</li>
            <li>{tx('This is personal data (touch data can be sensitive) under the 2025 Vietnamese Personal Data Protection Law; collection is based on your consent.',
              'Đây là dữ liệu cá nhân (dữ liệu thao tác có thể là dữ liệu nhạy cảm) theo Luật Bảo vệ dữ liệu cá nhân 2025; việc thu dựa trên sự đồng ý của bạn.')}</li>
          </ul>
        </details>
        <label className="cl-check"><input type="checkbox" checked={ok} onChange={(e) => setOk(e.target.checked)} />
          <span>{tx('I agree to take part and will use a new PIN that does not match any password or PIN I really use.', 'Tôi đồng ý tham gia và sẽ đặt mã PIN mới, không trùng mật khẩu hay mã PIN nào tôi đang dùng.')}</span></label>
      </>}
      {!api.hasSdkKey() && <p className="cl-err" role="alert">{tx(...NO_KEY)}</p>}
      {err && <p className="cl-err" role="alert">{err}</p>}
      <button className="cl-btn" disabled={!valid || busy || !api.hasSdkKey()} onClick={() => void submit()}>
        {busy ? '…' : mode === 'signup' ? tx('Create account', 'Tạo tài khoản') : tx('Sign in', 'Đăng nhập')}</button>
    </div>
  )
}

/** One PIN pad: 6 dots, a 10-digit pad (+ delete). Calls onEntry with the digits once 6 are typed with a finger on each key. */
function PinPad({ title, sub, busy, onEntry, recRef, msg }: {
  title: string; sub: string; busy: boolean; msg?: string | null
  onEntry: (digits: string) => void; recRef: React.MutableRefObject<Recorder>
}) {
  const tx = useTx()
  const [digits, setDigits] = useState('')
  const [pressed, setPressed] = useState<string | null>(null)
  const press = (k: string) => {
    if (busy) return
    // delete one digit and its tap (taps are pushed on key-up, so the last tap is the last digit)
    if (k === '⌫') { if (digits) { setDigits(digits.slice(0, -1)); recRef.current.taps.pop() }; return }
    if (digits.length >= PIN_LEN) return
    const next = digits + k
    setDigits(next)
    if (next.length < PIN_LEN) return
    window.setTimeout(() => {
      setDigits('')
      if (recRef.current.taps.length < PIN_LEN) { recRef.current.clearTaps(); return } // a digit came without a finger on the key
      onEntry(next)
    }, 120)
  }
  return (
    <div className="cl-pin">
      <h2>{title}</h2>
      <p className="cl-sub">{sub}</p>
      <div className="cl-dots" aria-label={`${digits.length}/${PIN_LEN}`}>
        {Array.from({ length: PIN_LEN }, (_, i) => <i key={i} className={i < digits.length ? 'on' : ''} />)}
      </div>
      {/* always rendered so the keypad does not jump when a message appears */}
      <p className="cl-err" role="alert">{msg}</p>
      {busy
        ? <div className="cl-wait" role="status"><span className="cl-spin" aria-hidden="true" />{tx('Saving…', 'Đang ghi nhận…')}</div>
        : (
          <div className="cl-keys">
            {KEYS.map((k, i) => k === '' ? <span key={i} /> : (
              <button key={i} className={`cl-key ${pressed === k ? 'down' : ''}`}
                onPointerDown={(e) => { if (k !== '⌫') recRef.current.keyDown(e.nativeEvent, k, e.currentTarget); setPressed(k) }}
                onPointerUp={(e) => { recRef.current.keyUp(e.nativeEvent); setPressed(null) }}
                onPointerCancel={(e) => { recRef.current.keyUp(e.nativeEvent); setPressed(null) }}
                onClick={() => press(k)} aria-label={k === '⌫' ? tx('Delete', 'Xoá') : k}>{k}</button>
            ))}
          </div>
        )}
    </div>
  )
}

const POSTURES: { id: Posture; en: string; vi: string }[] = [
  { id: 'sit', en: 'Sitting', vi: 'Ngồi' }, { id: 'stand', en: 'Standing', vi: 'Đứng' }, { id: 'walk', en: 'Walking', vi: 'Vừa đi' },
]
// E33: enrolled only sitting, owners walking get an extra check 2x as often; mixing postures at set-up evens it out
const suggestedPosture = (k: number): Posture => (k < 3 ? 'sit' : 'walk')

/** Self-reported posture for each entry (research label, sent in meta.posture). */
function PostureChips({ value, onChange }: { value: Posture; onChange: (p: Posture) => void }) {
  const tx = useTx()
  return (
    <div className="cl-tabs cl-seg3" role="radiogroup" aria-label={tx('How are you holding the phone?', 'Bạn đang nhập khi')}>
      {POSTURES.map((p) => (
        <button key={p.id} role="radio" aria-checked={value === p.id} className={value === p.id ? 'on' : ''} onClick={() => onChange(p.id)}>{tx(p.en, p.vi)}</button>
      ))}
    </div>
  )
}

/** Rhythm set-up: the PIN typed 5 to 10 times, each entry sent and enrolled at once; the accuracy bar sits under the keypad. */
function EnrollRounds({ account, onStatus, strip }: {
  account: AccountStatus; onStatus: (st: UserStatus) => void; strip: (right: string) => JSX.Element
}) {
  const tx = useTx()
  const k = account.enrolled_sessions
  const pin = useRef('') // the PIN made on the first entry of this visit; later entries must match it
  const rec = useRef(new Recorder())
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState<string | null>(null)
  const [posture, setPosture] = useState<Posture>(suggestedPosture(k))
  useEffect(() => { rec.current.screen('pin') }, [])
  const suggested = suggestedPosture(k)
  useEffect(() => { setPosture(suggested) }, [suggested]) // follow the hint only when it changes (entry 4), keep the person's own pick otherwise

  async function onEntry(digits: string) {
    if (pin.current && digits !== pin.current) {
      setMsg(tx('Does not match the PIN you made. Try again.', 'Không khớp mã đã tạo. Nhập lại.'))
      rec.current = new Recorder(); rec.current.screen('pin'); return
    }
    const meta: CollectionMeta = { participant_id: idOf(account.email), sitting: 1, role: 'genuine', posture, email: account.email, ...(account.full_name ? { full_name: account.full_name } : {}) }
    const s: SessionIn = { ...rec.current.payload(account.user_id), meta }
    setBusy(true); setMsg(null)
    try {
      const { session_id } = await api.createSession(s)
      onStatus(await api.enroll(account.user_id, session_id, true))
      pin.current = digits
    } catch (e) {
      setMsg(e instanceof ApiError && e.status === 0 ? tx('No connection. Type the PIN again.', 'Không có mạng. Nhập lại mã PIN.')
        : isKeyError(e) ? tx(...NO_KEY) : `${tx('Could not save', 'Không lưu được')}${e instanceof ApiError ? ` (${e.status})` : ''}`)
    } finally {
      rec.current = new Recorder(); rec.current.screen('pin'); setBusy(false)
    }
  }
  async function finish() {
    setBusy(true)
    try { onStatus(await api.finishEnroll(account.user_id)) } catch { setMsg(tx('Could not save. Try again.', 'Không lưu được. Thử lại.')) } finally { setBusy(false) }
  }

  const { value, measured } = impostorStopped(k)
  const c = account.consistency
  return (
    <div className="cl cl-app">
      {strip(`${k}/${MAX_ENROLL}`)}
      <div className="cl-posture">
        <p className="cl-hint">{tx('Entries 1–3 sitting, from entry 4 type while walking.', 'Lần 1–3 ngồi, từ lần 4 vừa đi vừa nhập.')}</p>
        <PostureChips value={posture} onChange={setPosture} />
      </div>
      <PinPad recRef={rec} busy={busy} msg={msg} onEntry={(d) => void onEntry(d)}
        title={k === 0 && !pin.current ? tx('Create a 6-digit PIN', 'Tạo mã PIN 6 số') : tx('Enter your PIN again', 'Nhập lại mã PIN')}
        sub={k === 0 && !pin.current ? tx('A new PIN, not one you really use.', 'Mã mới, không trùng PIN/mật khẩu thật.')
          : tx(`Entry ${k + 1}: the same PIN, as you normally type`, `Lần ${k + 1}: đúng mã đó, gõ như bình thường`)} />
      <section className="cl-acc" aria-live="polite">
        <div className="cl-acc-head"><b>Accuracy check</b><b className="cl-acc-val">{Math.round(value * 100)}%</b></div>
        <div className="cl-acc-bar"><i style={{ width: `${value * 100}%` }} /></div>
        <p>{tx(`After ${k} entries about ${Math.round(value * 100)}% of people who know your PIN are stopped.`, `Sau ${k} lần nhập, khoảng ${Math.round(value * 100)}% người biết PIN của bạn bị chặn.`)}{' '}
          {measured ? tx('Measured on real phone PINs.', 'Đo trên PIN điện thoại thật.') : tx('Above 4 entries: estimated, not yet measured.', 'Trên 4 lần: ước lượng, chưa đo.')}
          {c != null && <> {tx('Your steadiness', 'Độ ổn định nhịp của bạn')}: <b>{Math.round(c * 100)}%</b>.</>}</p>
        <button className="cl-btn" disabled={busy || k < MIN_JUDGE_ENROLL} onClick={() => void finish()}>
          {k < MIN_JUDGE_ENROLL ? tx(`Done (at least ${MIN_JUDGE_ENROLL} entries)`, `Xong (ít nhất ${MIN_JUDGE_ENROLL} lần)`) : tx('Done, save my rhythm', 'Xong, lưu nhịp của tôi')}</button>
      </section>
    </div>
  )
}

const RECIPIENTS = [
  { id: 'mum', name: ['Mum', 'Mẹ'], sub: ['Saved contact', 'Người quen'], isNew: false },
  { id: 'new', name: ['New recipient', 'Người nhận mới'], sub: ['First transfer', 'Lần đầu chuyển'], isNew: true },
] as const
const AMOUNTS = [500_000, 2_000_000, 5_000_000, 20_000_000]

/** After set-up: a transfer confirmed with the PIN, scored live against this account's rhythm. */
function Transfer({ account, strip }: { account: AccountStatus; strip: (right: string) => JSX.Element }) {
  const tx = useTx()
  const { lang } = useContext(LangContext)
  const [to, setTo] = useState<(typeof RECIPIENTS)[number]['id']>('mum')
  const [amount, setAmount] = useState(AMOUNTS[0])
  const [step, setStep] = useState<'form' | 'pin' | 'result'>('form')
  const [score, setScore] = useState<Score | null>(null)
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState<string | null>(null)
  const [who, setWho] = useState<'owner' | 'other'>('owner')
  const [posture, setPosture] = useState<Posture>('sit')
  const rec = useRef(new Recorder())
  const money = (v: number) => v.toLocaleString('vi-VN') + ' ₫'
  const r = RECIPIENTS.find((x) => x.id === to)!

  async function onEntry() {
    setBusy(true); setMsg(null)
    try {
      // research labels: who really typed (the owner, or someone else trying with the password and PIN) and in what posture
      const meta: CollectionMeta = who === 'owner'
        ? { participant_id: idOf(account.email), sitting: 2, role: 'genuine', posture, email: account.email }
        : { participant_id: `x${Math.random().toString(36).slice(2, 10)}`, sitting: 2, role: 'impostor', posture }
      const { session_id } = await api.createSession({ ...rec.current.payload(account.user_id), meta })
      setScore(await api.score(session_id, { recipient_is_new: r.isNew, amount }))
      setStep('result')
    } catch (e) {
      setMsg(e instanceof ApiError && e.status === 0 ? tx('No connection. Type the PIN again.', 'Không có mạng. Nhập lại mã PIN.') : `${tx('Error', 'Lỗi')}${e instanceof ApiError ? ` ${e.status}` : ''}`)
    } finally { rec.current = new Recorder(); rec.current.screen('pin'); setBusy(false) }
  }

  if (step === 'pin') return (
    <div className="cl cl-app">
      {strip(money(amount))}
      <PinPad recRef={rec} busy={busy} msg={msg} onEntry={() => void onEntry()}
        title={tx('Enter your PIN to confirm', 'Nhập mã PIN để xác nhận')} sub={`${money(amount)} → ${r.name[lang === 'en' ? 0 : 1]}`} />
      <button className="cl-link cl-back" onClick={() => setStep('form')}>{tx('Back', 'Quay lại')}</button>
    </div>
  )

  if (step === 'result' && score) {
    const a = score.action
    return (
      <div className="cl cl-app"><div className="cl-ok">
        <span className={`cl-tick ${a}`} aria-hidden="true">{a === 'allow' ? '✓' : a === 'step_up' ? '!' : '■'}</span>
        <h2>{a === 'allow' ? tx('Sent', 'Đã chuyển') : a === 'step_up' ? tx('Extra check needed', 'Cần xác minh thêm') : tx('Transfer on hold', 'Lệnh đang tạm giữ')}</h2>
        <p>{explanationText(score, lang)}</p>
        <p className="cl-scores">{tx('Owner match', 'Khớp chủ tài khoản')} <b>{score.owner_match == null ? '—' : `${Math.round(score.owner_match * 100)}%`}</b>
          {' · '}{tx('Human', 'Người thật')} <b>{Math.round(score.human_score * 100)}%</b></p>
        {score.reasons.length > 0 && <ul className="cl-reasons">{score.reasons.map((x) => <li key={x}>{reasonText(x, lang)}</li>)}</ul>}
        <button className="cl-btn" onClick={() => { setScore(null); setStep('form') }}>{tx('Another transfer', 'Giao dịch khác')}</button>
      </div></div>
    )
  }

  return (
    <div className="cl cl-app">
      {strip(tx('Rhythm saved', 'Đã lưu nhịp'))}
      <div className="cl-page">
      <h2 style={{ marginTop: 16 }}>{tx('Send money', 'Chuyển tiền')}</h2>
      <p className="cl-sub">{tx('Innate checks your touch rhythm when you confirm with the PIN. Hand the phone to someone who knows your password and PIN to see the difference.', 'Innate kiểm tra nhịp chạm khi bạn xác nhận bằng PIN. Đưa máy cho người biết mật khẩu và PIN của bạn để thấy khác biệt.')}</p>
      <h3>{tx('To', 'Đến')}</h3>
      {RECIPIENTS.map((x) => (
        <label key={x.id} className={`cl-person ${to === x.id ? 'on' : ''}`}>
          <input type="radio" name="to" checked={to === x.id} onChange={() => setTo(x.id)} />
          <i>{x.name[1][0]}</i><span><b>{x.name[lang === 'en' ? 0 : 1]}</b><small>{x.sub[lang === 'en' ? 0 : 1]}</small></span>
        </label>
      ))}
      <h3>{tx('Who is typing?', 'Ai đang nhập?')}</h3>
      <div className="cl-tabs" role="radiogroup">
        {(['owner', 'other'] as const).map((w) => (
          <button key={w} role="radio" aria-checked={who === w} className={who === w ? 'on' : ''} onClick={() => setWho(w)}>
            {w === 'owner' ? tx('Account owner', 'Chủ tài khoản') : tx('Someone else trying', 'Người khác thử')}</button>
        ))}
      </div>
      <h3>{tx('Typing while', 'Đang nhập khi')}</h3>
      <PostureChips value={posture} onChange={setPosture} />
      <h3>{tx('Amount', 'Số tiền')}</h3>
      <div className="cl-amounts">
        {AMOUNTS.map((v) => (
          <label key={v} className={`cl-chip ${amount === v ? 'on' : ''}`}>
            <input type="radio" name="amt" checked={amount === v} onChange={() => setAmount(v)} />{money(v)}
          </label>
        ))}
      </div>
      <button className="cl-btn" onClick={() => { rec.current = new Recorder(); rec.current.screen('pin'); setStep('pin') }}>{tx('Continue', 'Tiếp tục')}</button>
      </div>
    </div>
  )
}

/** Top of the start screen: the app icon, a language switch and a way to the main Innate site.
 *  Not shown during the PIN and phrase steps, so nothing near the keypad can be tapped by accident. */
function AppBar() {
  const tx = useTx()
  const { lang, setLang } = useContext(LangContext)
  return (
    <header className="cl-bar">
      <span className="cl-brand"><AppIcon size={30} /><b>Innate</b></span>
      <span className="cl-bar-right">
        <span className="cl-lang" role="group" aria-label={tx('Language', 'Ngôn ngữ')}>
          {(['vi', 'en'] as const).map((k) => (
            <button key={k} type="button" aria-pressed={lang === k} onClick={() => setLang(k)}>{k.toUpperCase()}</button>
          ))}
        </span>
        <a className="cl-about" href="#/">{tx('About Innate', 'Về Innate')}</a>
      </span>
    </header>
  )
}

/** "Add to Home Screen" tip: Android gets the browser's own install button, iPhone gets the Share-menu steps. Dismissable. */
function InstallHint() {
  const tx = useTx()
  const [, force] = useState(0)
  useEffect(() => onInstallChange(() => force((n) => n + 1)), [])
  const [hidden, setHidden] = useState(() => { try { return localStorage.getItem('innate.installHint') === 'off' } catch { return false } })
  if (hidden || isInstalled()) return null
  const android = canPromptInstall()
  if (!android && !isIOS()) return null
  const close = () => { setHidden(true); try { localStorage.setItem('innate.installHint', 'off') } catch { /* private mode */ } }
  return (
    <div className="cl-install" role="note">
      <AppIcon size={36} />
      <p>{android
        ? tx('Install Innate on your home screen to open it full screen, like an app.', 'Cài Innate ra màn hình chính để mở toàn màn hình như một ứng dụng.')
        : tx('To use Innate like an app: tap Share, then “Add to Home Screen”.', 'Để dùng Innate như ứng dụng: bấm Chia sẻ, rồi “Thêm vào MH chính”.')}</p>
      {android && <button className="cl-install-go" onClick={() => void promptInstall()}>{tx('Install', 'Cài đặt')}</button>}
      <button className="cl-install-x" onClick={close} aria-label={tx('Hide', 'Ẩn')}>×</button>
    </div>
  )
}

/** On a laptop or tablet: point to the phone with a QR code of this page. */
function PhoneGate() {
  const tx = useTx()
  const url = `${window.location.origin}${window.location.pathname}#/collect`
  const local = /^(localhost|127\.|\[::1\])/.test(window.location.hostname)
  const qr = qrcode(0, 'M')
  qr.addData(url)
  qr.make()
  const n = qr.getModuleCount()
  const cells: string[] = []
  for (let r = 0; r < n; r++) for (let c = 0; c < n; c++) if (qr.isDark(r, c)) cells.push(`M${c} ${r}h1v1h-1z`)
  return (
    <div className="cl cl-gate">
      <AppIcon size={56} className="cl-gate-icon" />
      <h1>{tx('Open this page on your phone', 'Mở trang này trên điện thoại')}</h1>
      <p>{tx('Innate collects touch data from a phone screen, so this page only works on a touchscreen phone. Scan the code with your phone camera.',
        'Innate thu dữ liệu chạm trên màn hình điện thoại, nên trang này chỉ chạy trên điện thoại cảm ứng. Quét mã bằng camera điện thoại.')}</p>
      <svg className="cl-qr" viewBox={`-2 -2 ${n + 4} ${n + 4}`} role="img" aria-label={url} shapeRendering="crispEdges">
        <rect x="-2" y="-2" width={n + 4} height={n + 4} fill="#fff" />
        <path d={cells.join('')} fill="#16202c" />
      </svg>
      <p className="cl-url">{url}</p>
      {local && <p className="cl-note">{tx('This is a localhost address, which a phone cannot open. Start the dev server with --host and open the Network address it prints instead.',
        'Đây là địa chỉ localhost, điện thoại không mở được. Chạy dev server với --host rồi mở địa chỉ Network nó in ra.')}</p>}
      <a className="cl-about" href="#/">{tx('Back to the Innate site', 'Về trang Innate')}</a>
    </div>
  )
}
