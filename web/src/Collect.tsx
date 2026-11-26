import { useContext, useEffect, useRef, useState, type PointerEvent as RPointerEvent } from 'react'
import { ApiError, api, type Challenge, type CollectionMeta, type FieldEvent, type SessionIn } from './api'
import { Recorder } from './capture'
import { ComposeRecorder } from './compose'
import { LangContext } from './i18n'
import { canPromptInstall, isIOS, isInstalled, isPhone, onInstallChange, promptInstall } from './device'
import { AppIcon } from './landing/ui'
import qrcode from 'qrcode-generator'
import './collect.css'

// Data-collection page (#/collect): one form (name, email, consent), then a 10-digit pad (+ delete) where the volunteer creates
// a 6-digit PIN and types it 5 times in all; after each entry they type a short random Vietnamese sentence (the "Innate Challenge",
// docs/plan/innate-challenge-vi.md; only times, key kinds and lengths are sent). The 5 sessions are sent together, with name + email in `meta`.
// The PIN digits are stored on purpose (pin_taps[].key, for per-key research); the form warns not to reuse a real one.
// Phone only: on a desktop it shows a "open on your phone" notice (add ?dev=1 to test in devtools).
const PIN_LEN = 6
const ENTRIES = 5
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

interface Person { name: string; email: string }

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
  const [person, setPerson] = useState<Person | null>(null)

  if (!phone) return <PhoneGate />
  if (!person) return <Start onDone={setPerson} />
  return <PinRound person={person} onNext={() => setPerson(null)} />
}

function Start({ onDone }: { onDone: (p: Person) => void }) {
  const tx = useTx()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [ok, setOk] = useState(false)
  const n = name.trim().replace(/\s+/g, ' '), m = email.trim().toLowerCase()
  const valid = n.length >= 2 && n.length <= 100 && EMAIL.test(m) && m.length <= 254 && ok
  return (
    <div className="cl cl-page">
      <AppBar />
      <InstallHint />
      <h1>{tx('Touch data collection', 'Thu thập dữ liệu thao tác')}</h1>
      <label className="cl-field"><span>{tx('Full name', 'Họ và tên')}</span>
        <input value={name} onChange={(e) => setName(e.target.value)} autoComplete="name" maxLength={100} /></label>
      <label className="cl-field"><span>Email</span>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" inputMode="email"
          autoCapitalize="none" autoCorrect="off" spellCheck={false} maxLength={254} /></label>
      <p className="cl-note">{tx('You will make up a 6-digit PIN and type it 5 times. ', 'Bạn sẽ tự đặt một mã PIN 6 số rồi nhập 5 lần. ')}
        <b>{tx('This PIN is stored', 'Mã này được lưu lại')}</b>{tx(' for research, so it ', ' để nghiên cứu, nên ')}
        <b>{tx('must not match', 'không được trùng')}</b>{tx(' any password or PIN you really use (bank, wallet, ATM card, phone unlock, email...).',
          ' với mật khẩu hay mã PIN nào bạn đang dùng (ngân hàng, ví, thẻ ATM, mở khoá điện thoại, email...).')}</p>
      <details className="cl-more"><summary>{tx('What we collect and how we use it', 'Chúng tôi thu gì và dùng thế nào')}</summary>
        <ul>
          <li>{tx('Collected: full name, email, the practice PIN you make up, the time, position and contact size of each tap, and how you type a short sentence shown on screen (only timing, key kinds and length; the sentence text is not recorded). No phone number, photos, voice, location or messages.',
            'Thu: họ tên, email, mã PIN thử bạn đặt, thời điểm, vị trí và kích thước vùng chạm khi gõ; và cách bạn gõ một câu ngắn hiện trên màn hình (chỉ thời điểm, loại phím và độ dài, không ghi nội dung câu). Không thu số điện thoại, ảnh, giọng nói, vị trí hay tin nhắn.')}</li>
          <li>{tx('Purpose: to train and evaluate the bot-detection and account-owner models of the Innate product (MoMo Tech Contest 2026); only aggregate figures are published.',
            'Mục đích: huấn luyện và đánh giá mô hình phát hiện bot và nhận ra chủ tài khoản của sản phẩm Innate (MoMo Tech Contest 2026); chỉ công bố số liệu tổng hợp.')}</li>
          <li>{tx('Stored in the team database, never sold or shared with third parties. You can withdraw, view or ask for deletion of your data at any time: contact ', 'Lưu trong cơ sở dữ liệu của đội, không bán hay chia cho bên thứ ba. Bạn có thể rút lui, xem hoặc yêu cầu xoá dữ liệu bất cứ lúc nào: liên hệ ')}{CONTACT ?? tx('the person who invited you', 'người mời bạn tham gia')}.</li>
          <li>{tx('This is personal data (touch data can be sensitive) under the 2025 Vietnamese Personal Data Protection Law; collection is based on your consent.',
            'Đây là dữ liệu cá nhân (dữ liệu thao tác có thể là dữ liệu nhạy cảm) theo Luật Bảo vệ dữ liệu cá nhân 2025; việc thu dựa trên sự đồng ý của bạn.')}</li>
        </ul>
      </details>
      <label className="cl-check"><input type="checkbox" checked={ok} onChange={(e) => setOk(e.target.checked)} />
        <span>{tx('I agree to take part and will use a new PIN that does not match any password or PIN I really use.', 'Tôi đồng ý tham gia và sẽ đặt mã PIN mới, không trùng mật khẩu hay mã PIN nào tôi đang dùng.')}</span></label>
      {!api.hasSdkKey() && <p className="cl-err" role="alert">{tx(...NO_KEY)}</p>}
      <button className="cl-btn" disabled={!valid || !api.hasSdkKey()} onClick={() => onDone({ name: n, email: m })}>{tx('Start', 'Bắt đầu')}</button>
    </div>
  )
}

function PinRound({ person, onNext }: { person: Person; onNext: () => void }) {
  const tx = useTx()
  const id = idOf(person.email)
  const [count, setCount] = useState(0) // correct entries so far (the first one creates the PIN)
  const [digits, setDigits] = useState('')
  const [shake, setShake] = useState(false)
  const [pressed, setPressed] = useState<string | null>(null)
  const [msg, setMsg] = useState<string | null>(null)
  const [state, setState] = useState<'pin' | 'phrase' | 'sending' | 'failed' | 'done'>('pin')
  const pending = useRef<SessionIn | null>(null) // PIN entry waiting for its phrase
  const pin = useRef('') // the PIN made on entry 1; later entries must match it
  const rec = useRef(new Recorder())
  const queue = useRef<SessionIn[]>([])
  useEffect(() => { rec.current.screen('pin') }, [])

  const reset = () => { setDigits(''); rec.current.clearTaps() }

  async function sendAll() {
    setState('sending')
    try {
      while (queue.current.length) {
        await api.createSession(queue.current[0])
        queue.current.shift()
      }
      setState('done')
    } catch (e) {
      setMsg(e instanceof ApiError && e.status === 0 ? tx('No connection. Check your network and tap Resend.', 'Không có mạng. Kiểm tra kết nối rồi bấm Gửi lại.')
        : isKeyError(e) ? tx(...NO_KEY)
        : `${tx('Could not send the data', 'Lỗi gửi dữ liệu')}${e instanceof ApiError ? ` (${e.status})` : ''}. ${tx('Tap Resend.', 'Bấm Gửi lại.')}`)
      setState('failed')
    }
  }

  const press = (k: string) => {
    // delete one digit and its tap (taps are pushed on key-up, so the last tap is the last digit)
    if (k === '⌫') { if (digits) { setDigits(digits.slice(0, -1)); rec.current.taps.pop() }; return }
    if (digits.length >= PIN_LEN) return
    const next = digits + k
    setDigits(next); setMsg(null)
    if (next.length < PIN_LEN) return
    if (count > 0 && next !== pin.current) {
      setShake(true); setMsg(tx('Does not match the PIN you made. Try again.', 'Không khớp mã đã tạo. Nhập lại.'))
      window.setTimeout(() => { setShake(false); reset() }, 450)
      return
    }
    window.setTimeout(() => {
      if (rec.current.taps.length < PIN_LEN) { reset(); return } // a digit came without a finger on the key
      if (count === 0) pin.current = next
      pending.current = rec.current.payload(id)
      setState('phrase')
    }, 0)
  }
  const finishPhrase = (r: { challenge: Challenge; events: FieldEvent[] } | null, note?: string) => {
    // sitting/role are required by the API schema; this page has one kind of round only
    const meta: CollectionMeta = { participant_id: id, sitting: 1, role: 'genuine', full_name: person.name, email: person.email, ...(note ? { note } : {}) }
    const base = pending.current!
    const fields = r ? [...(base.fields ?? []), { name: 'challenge' as const, token: r.challenge.token, expected_len: r.challenge.expected_len, events: r.events }] : base.fields
    queue.current.push({ ...base, ...(fields ? { fields } : {}), meta })
    pending.current = null
    rec.current = new Recorder(); rec.current.screen('pin'); setDigits('')
    const n = count + 1
    setCount(n)
    if (n === ENTRIES) { pin.current = ''; void sendAll() } else setState('pin')
  }
  const keyDown = (e: RPointerEvent<HTMLButtonElement>, k: string) => {
    if (k !== '⌫') rec.current.keyDown(e.nativeEvent, k, e.currentTarget)
    setPressed(k)
  }
  const keyUp = (e: RPointerEvent<HTMLButtonElement>) => { rec.current.keyUp(e.nativeEvent); setPressed(null) }

  if (state === 'done') {
    return (
      <div className="cl cl-app"><div className="cl-ok">
        <span className="cl-tick" aria-hidden="true">✓</span>
        <h2>{tx('Thank you', 'Cảm ơn')} {person.name}!</h2>
        <p>{tx(`Recorded ${ENTRIES} entries. You can close this page.`, `Đã ghi nhận ${ENTRIES} lần nhập. Bạn có thể đóng trang.`)}</p>
        <button className="cl-btn ghost" onClick={onNext}>{tx('Someone else takes part', 'Người khác tham gia')}</button>
      </div></div>
    )
  }

  if (state === 'phrase') {
    return (
      <div className="cl cl-app">
        <div className="cl-strip"><span>{person.name}</span><b>{count}/{ENTRIES}</b></div>
        <PhraseStep now={() => rec.current.now()} onDone={finishPhrase} />
      </div>
    )
  }

  return (
    <div className="cl cl-app">
      <div className="cl-strip"><span>{person.name}</span><b>{count}/{ENTRIES}</b></div>
      <div className="cl-pin">
        <h2>{count === 0 ? tx('Create a 6-digit PIN', 'Tạo mã PIN 6 số') : tx('Enter your PIN again', 'Nhập lại mã PIN')}</h2>
        <p className="cl-sub">{count === 0 ? tx('A new PIN, not one you really use.', 'Mã mới, không trùng PIN/mật khẩu thật.') : tx(`Entry ${count + 1}/${ENTRIES}: enter the PIN you just made`, `Lần ${count + 1}/${ENTRIES}: nhập đúng mã vừa tạo`)}</p>
        <div className={`cl-dots ${shake ? 'shake' : ''}`} aria-label={`${digits.length}/${PIN_LEN}`}>
          {Array.from({ length: PIN_LEN }, (_, i) => <i key={i} className={i < digits.length ? 'on' : ''} />)}
        </div>
        {/* always rendered so the keypad does not jump when a message appears */}
        <p className="cl-err" role="alert">{msg}{' '}
          {msg && state === 'failed' && <button className="cl-link" onClick={() => { setMsg(null); void sendAll() }}>{tx('Resend', 'Gửi lại')}</button>}</p>
        {state === 'sending' || state === 'failed'
          ? state === 'sending' && <div className="cl-wait" role="status"><span className="cl-spin" aria-hidden="true" />{tx('Saving…', 'Đang ghi nhận…')}</div>
          : (
            <div className="cl-keys">
              {KEYS.map((k, i) => k === '' ? <span key={i} /> : (
                <button key={i} className={`cl-key ${pressed === k ? 'down' : ''}`}
                  onPointerDown={(e) => keyDown(e, k)} onPointerUp={keyUp} onPointerCancel={keyUp} onClick={() => press(k)}
                  aria-label={k === '⌫' ? tx('Delete', 'Xoá') : k}>{k}</button>
              ))}
            </div>
          )}
      </div>
    </div>
  )
}

/** Type the random Vietnamese sentence from the API. Paste/drop/cut are blocked; only timing, key kinds and lengths are recorded. */
function PhraseStep({ now, onDone }: { now: () => number; onDone: (r: { challenge: Challenge; events: FieldEvent[] } | null, note?: string) => void }) {
  const tx = useTx()
  const [ch, setCh] = useState<Challenge | null>(null)
  const [failed, setFailed] = useState<'nokey' | 'other' | null>(null)
  const [typed, setTyped] = useState('')
  const input = useRef<HTMLInputElement>(null)
  const rec = useRef<ComposeRecorder | null>(null)
  useEffect(() => {
    let live = true
    api.challenge().then((c) => { if (live) setCh(c) }).catch((e) => { if (live) setFailed(isKeyError(e) ? 'nokey' : 'other') })
    return () => { live = false }
  }, [])
  useEffect(() => {
    if (ch && input.current && !rec.current) { rec.current = new ComposeRecorder(input.current, now); input.current.focus() }
  }, [ch, now])
  const nfc = (v: string) => v.normalize('NFC').trim()
  const match = !!ch && nfc(typed) === nfc(ch.phrase)
  return (
    <div className="cl-pin cl-phrase">
      <h2>{tx('Type this sentence again', 'Gõ lại câu này')}</h2>
      {!ch && !failed && <div className="cl-wait" role="status"><span className="cl-spin" aria-hidden="true" />{tx('Loading…', 'Đang tải…')}</div>}
      {failed === 'nokey' && <p className="cl-err" role="alert">{tx(...NO_KEY)}</p>}
      {failed === 'other' && <>
        <p className="cl-err" role="alert">{tx('Could not load the sentence. You can skip this step.', 'Không tải được câu. Bạn có thể bỏ qua bước này.')}</p>
        <button className="cl-btn" onClick={() => onDone(null, 'phrase_unavailable')}>{tx('Skip', 'Bỏ qua')}</button>
      </>}
      {ch && <>
        <p className="cl-sentence" lang="vi">{ch.phrase}</p>
        <p className="cl-sub">{tx('Use the Vietnamese keyboard you normally use (Telex or VNI) and type all the tone marks. Pasting is blocked.', 'Dùng bàn phím tiếng Việt quen thuộc của bạn (Telex hoặc VNI), gõ đủ dấu. Không dán được.')}</p>
        <input ref={input} className="cl-type" type="text" lang="vi" value={typed} onChange={(e) => setTyped(e.target.value)}
          autoComplete="off" autoCorrect="off" autoCapitalize="off" spellCheck={false} enterKeyHint="done" inputMode="text"
          onPaste={(e) => e.preventDefault()} onDrop={(e) => e.preventDefault()} onCut={(e) => e.preventDefault()}
          aria-label={tx('Type the sentence again', 'Gõ lại câu')} aria-invalid={typed.length >= ch.phrase.length && !match} />
        {typed.length >= ch.phrase.length && !match && <p className="cl-err" role="alert">{tx('Not the same yet. Check the tone marks and spaces.', 'Chưa giống. Kiểm tra dấu và khoảng trắng.')}</p>}
        <button className="cl-btn" disabled={!match} onClick={() => onDone({ challenge: ch, events: rec.current?.finish() ?? [] })}>{tx('Continue', 'Tiếp tục')}</button>
        <button className="cl-link" onClick={() => onDone(null, 'no_vi_keyboard')}>{tx('My keyboard cannot type Vietnamese tone marks', 'Bàn phím của tôi không gõ được dấu tiếng Việt')}</button>
      </>}
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
