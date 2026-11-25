import { useContext, useEffect, useRef, useState, type PointerEvent as RPointerEvent } from 'react'
import { ApiError, api, type CollectionMeta, type SessionIn } from './api'
import { Recorder } from './capture'
import { LangContext } from './i18n'
import './collect.css'

// Data-collection page (#/collect): a plain transfer app for volunteers on their own phone.
// Flow: consent → email + full name → create a PIN (twice) → enter it 5 times through the transfer screens.
// It records only times, finger positions and touch size (same SDK as the demo) plus the key labels the API stores,
// and sends them with a `meta` label. Email and name go to a separate table (POST /v1/participants), never into the sessions.
// Phone only: on a desktop it shows an "open on your phone" notice (add ?dev=1 to test in devtools).
// Language follows the site (LangContext from App.tsx).
const PIN_LEN = 6 // the learned owner model was trained on 6-digit PINs (backend/app/scoring/owner_model.py)
const ENTRIES = 5
const ENROLL = 3 // the first entries become the owner's rhythm template, like the demo's 3 enrolment entries
const KEYS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '', '0', '⌫']
const CONTACT = import.meta.env.VITE_COLLECT_CONTACT as string | undefined
const EMAIL = /^[^@\s]+@[^@\s]+\.[^@\s]+$/
const AMOUNTS = [200_000, 500_000, 1_000_000, 2_000_000]
const PEOPLE = [
  { id: 'a', en: 'Mum', vi: 'Mẹ', acct: '0901 234 567', ini: 'M' },
  { id: 'b', en: 'Tuấn (landlord)', vi: 'Anh Tuấn (chủ nhà)', acct: '0912 888 120', ini: 'T' },
  { id: 'c', en: 'Lan Anh', vi: 'Lan Anh', acct: '0987 456 321', ini: 'L' },
]

/** at least two words, each starting with a capital letter followed by lowercase letters (diacritics allowed) */
const nameOk = (name: string) => {
  const words = name.normalize('NFC').trim().split(/\s+/)
  return words.length >= 2 && words.every((w) => /^\p{Lu}[\p{Ll}\p{M}]*$/u.test(w))
}
const newId = () => `u_${[...crypto.getRandomValues(new Uint8Array(6))].map((b) => b.toString(16).padStart(2, '0')).join('')}`

/** the site language; tx(english, vietnamese) picks one */
function useTx() {
  const { lang } = useContext(LangContext)
  const tx = (en: string, vi: string) => (lang === 'en' ? en : vi)
  const vnd = (n: number) => `${n.toLocaleString(lang === 'en' ? 'en-US' : 'vi-VN')} ₫`
  return { tx, vnd, lang }
}

function isPhone() {
  return window.matchMedia('(pointer: coarse)').matches && Math.min(window.innerWidth, window.innerHeight) <= 600
}

type Step = 'consent' | 'profile' | 'create' | 'confirm' | 'run'
interface Profile { id: string; email: string; name: string }

// Progress survives a reload for the life of the tab (sessionStorage is cleared when the tab closes). The PIN is a made-up
// practice PIN that is already part of the data sent to the API, so keeping it here adds no exposure.
const STATE_KEY = 'innate.collect.state'
interface Saved { step: Step; profile: Profile | null; pin: string; done: number }
const loadSaved = (): Saved => {
  try {
    const v = JSON.parse(sessionStorage.getItem(STATE_KEY) ?? 'null') as Saved | null
    if (v && v.step && (v.step === 'consent' || v.step === 'profile' || v.profile)) return v
  } catch { /* private mode or bad JSON */ }
  return { step: 'consent', profile: null, pin: '', done: 0 }
}

export default function Collect() {
  const { tx } = useTx()
  useEffect(() => {
    const html = document.documentElement
    html.dataset.page = 'collect'
    const robots = document.createElement('meta'); robots.name = 'robots'; robots.content = 'noindex'
    document.head.appendChild(robots)
    return () => { delete html.dataset.page; robots.remove() }
  }, [])
  const dev = new URLSearchParams(window.location.hash.split('?')[1] ?? '').get('dev') === '1'
  const [phone, setPhone] = useState(() => dev || isPhone())
  useEffect(() => {
    const on = () => setPhone(dev || isPhone())
    window.addEventListener('resize', on)
    return () => window.removeEventListener('resize', on)
  }, [dev])

  const [saved] = useState(loadSaved)
  const [step, setStep] = useState<Step>(saved.step)
  const [profile, setProfile] = useState<Profile | null>(saved.profile)
  const [pin, setPin] = useState(saved.pin)
  const [done, setDone] = useState(saved.done)
  useEffect(() => {
    try { sessionStorage.setItem(STATE_KEY, JSON.stringify({ step, profile, pin, done } satisfies Saved)) } catch { /* private mode */ }
  }, [step, profile, pin, done])

  if (!phone) {
    return (
      <div className="cl cl-gate"><h1>{tx('Open this page on your phone', 'Mở trang này trên điện thoại')}</h1>
        <p>{tx('The data-collection page only works on a touchscreen phone. Please open this link again on your phone.',
          'Trang thu thập dữ liệu chỉ chạy trên điện thoại cảm ứng. Hãy mở lại đường link này bằng điện thoại của bạn.')}</p></div>
    )
  }
  if (step === 'consent') return <Consent onAgree={() => setStep('profile')} />
  if (step === 'profile' || !profile) return <ProfileForm onDone={(p) => { setProfile(p); setStep('create') }} />
  if (step === 'create') return <PinSetup key="create" mode="create" onDone={(p) => { setPin(p); setStep('confirm') }} />
  if (step === 'confirm') return <PinSetup key="confirm" mode="confirm" expected={pin} onBack={() => setStep('create')} onDone={() => setStep('run')} />
  return <TransferApp profile={profile} pin={pin} done={done} onDone={setDone} onRestart={() => { setPin(''); setDone(0); setStep('create') }} />
}

function Consent({ onAgree }: { onAgree: () => void }) {
  const { tx } = useTx()
  const [ok, setOk] = useState(false)
  const contact = CONTACT ?? tx('the person who invited you', 'người mời bạn tham gia')
  return (
    <div className="cl cl-page">
      <h1>{tx('Consent to take part in touch-data collection', 'Phiếu đồng ý tham gia thu thập dữ liệu thao tác')}</h1>
      <p>{tx('We record how you tap and type on the screen, for research on the Innate product entered in MoMo Tech Contest 2026.',
        'Chúng tôi thu cách bạn chạm và gõ trên màn hình để nghiên cứu cho sản phẩm Innate tham dự MoMo Tech Contest 2026.')}</p>
      <ul>
        <li><b>{tx('What we record:', 'Dữ liệu thu:')}</b> {tx('your email and full name; when and where you touch the keys, the size of the touch, and when you swipe; and the practice PIN you create, as it is typed. We do not record photos, voice, location, contacts or messages.',
          'email và họ tên của bạn; thời điểm và vị trí các lần chạm phím, kích thước vùng chạm, thời điểm các lần vuốt; và mã PIN thử bạn tự tạo, đúng như bạn gõ. Chúng tôi không ghi ảnh, giọng nói, vị trí, danh bạ hay tin nhắn.')}</li>
        <li><b>{tx('Use a made-up PIN:', 'Hãy dùng PIN tự nghĩ ra:')}</b> {tx('do not use the PIN of your bank, wallet or phone.', 'đừng dùng PIN của ngân hàng, ví hay điện thoại của bạn.')}</li>
        <li><b>{tx('This app is fake:', 'Ứng dụng này là giả:')}</b> {tx('no real money, no real transfers.', 'không có tiền thật, không chuyển tiền thật.')}</li>
        <li><b>{tx('Purpose:', 'Mục đích:')}</b> {tx('to train and evaluate models that detect bots and recognise the account owner; only aggregate results are published.', 'huấn luyện và đánh giá mô hình phát hiện bot và nhận ra chủ tài khoản; chỉ công bố số liệu tổng hợp.')}</li>
        <li><b>{tx('Storage:', 'Lưu trữ:')}</b> {tx(`your email and name are kept in a separate table from the touch data, which carries only an anonymous code. Nothing is sold or shared with third parties. You can decline, withdraw, or ask to see and delete your data at any time: contact ${contact}.`, `email và họ tên được lưu ở bảng riêng, tách khỏi dữ liệu chạm (chỉ gắn mã ẩn danh). Không bán hay chia cho bên thứ ba. Bạn có thể từ chối, rút lui hoặc yêu cầu xem và xoá dữ liệu của mình bất cứ lúc nào: liên hệ ${contact}.`)}</li>
        <li>{tx('Touch data can be sensitive data under Vietnam’s 2025 Personal Data Protection Law; we collect it on the basis of your consent here.', 'Dữ liệu thao tác có thể là dữ liệu nhạy cảm theo Luật Bảo vệ dữ liệu cá nhân 2025; việc thu dựa trên sự đồng ý của bạn tại đây.')}</li>
      </ul>
      <label className="cl-check"><input type="checkbox" checked={ok} onChange={(e) => setOk(e.target.checked)} />
        <span>{tx('I have read this and agree to take part.', 'Tôi đã đọc và đồng ý tham gia.')}</span></label>
      <button className="cl-btn" disabled={!ok} onClick={onAgree}>{tx('Continue', 'Tiếp tục')}</button>
    </div>
  )
}

function ProfileForm({ onDone }: { onDone: (p: Profile) => void }) {
  const { tx } = useTx()
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [touched, setTouched] = useState(false)
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState<string | null>(null)
  const emailOk = EMAIL.test(email.trim()), fullName = name.normalize('NFC').trim().replace(/\s+/g, ' ')
  const nameValid = nameOk(fullName)
  const noMarks = fullName !== '' && /^[\x20-\x7E]+$/.test(fullName) // all plain ASCII: maybe a Vietnamese name written without diacritics

  async function submit() {
    setTouched(true)
    if (!emailOk || !nameValid) return
    setBusy(true); setErr(null)
    const id = newId()
    try {
      await api.registerParticipant({ participant_id: id, email: email.trim(), full_name: fullName })
      onDone({ id, email: email.trim().toLowerCase(), name: fullName })
    } catch (e) {
      const st = e instanceof ApiError ? e.status : -1
      setErr(st === 0 ? tx('No connection. Check your network and try again.', 'Không có mạng. Kiểm tra kết nối rồi thử lại.')
        : st === 401 || st === 403 ? tx('This build has no API key configured. Tell the team.', 'Bản này chưa cấu hình khoá API. Báo cho đội.')
        : tx(`Could not save your details (${st}). Try again.`, `Không lưu được thông tin (${st}). Thử lại.`))
    } finally { setBusy(false) }
  }

  return (
    <form className="cl cl-page" noValidate onSubmit={(e) => { e.preventDefault(); void submit() }}>
      <h1>{tx('About you', 'Thông tin của bạn')}</h1>
      <label className="cl-field"><span>Email</span>
        <input type="email" inputMode="email" autoComplete="email" autoCapitalize="none" autoCorrect="off" spellCheck={false}
          value={email} onChange={(e) => setEmail(e.target.value)} aria-invalid={touched && !emailOk} />
        {touched && !emailOk && <small className="cl-bad">{tx('Enter a valid email, e.g. an@gmail.com', 'Nhập email hợp lệ, ví dụ an@gmail.com')}</small>}
      </label>
      <label className="cl-field"><span>{tx('Full name', 'Họ và tên')}</span>
        <input type="text" autoComplete="name" autoCapitalize="words" spellCheck={false}
          value={name} onChange={(e) => setName(e.target.value)} aria-invalid={touched && !nameValid} />
        <small>{tx('Capitalise each word. If you are Vietnamese, write it with full diacritics, e.g. Nguyễn Văn An.', 'Viết hoa chữ cái đầu mỗi từ. Nếu là người Việt, viết đủ dấu, ví dụ: Nguyễn Văn An.')}</small>
        {touched && !nameValid && <small className="cl-bad">{tx('First and last name, each word starting with a capital letter.', 'Cần cả họ và tên, mỗi từ viết hoa chữ cái đầu.')}</small>}
        {nameValid && noMarks && <small>{tx('No diacritics found. If your name has them, please add them.', 'Chưa thấy dấu nào. Nếu tên bạn có dấu, hãy viết đủ dấu.')}</small>}
      </label>
      {err && <p className="cl-err" role="alert">{err}</p>}
      <button className="cl-btn" type="submit" disabled={busy}>{busy ? tx('Saving…', 'Đang lưu…') : tx('Continue', 'Tiếp tục')}</button>
    </form>
  )
}

/** The number pad. Only `onDown`/`onUp` feed the touch recorder; the create/confirm steps pass none. */
function Keypad({ pressed, disabled, onPress, onDown, onUp }: {
  pressed: string | null; disabled?: boolean; onPress: (k: string) => void
  onDown?: (e: RPointerEvent<HTMLButtonElement>, k: string) => void; onUp?: (e: RPointerEvent<HTMLButtonElement>) => void
}) {
  const { tx } = useTx()
  return (
    <div className="cl-keys">
      {KEYS.map((k, i) => k === '' ? <span key={i} /> : (
        <button key={i} className={`cl-key ${pressed === k ? 'down' : ''}`} disabled={disabled}
          onPointerDown={(e) => onDown?.(e, k)} onPointerUp={(e) => onUp?.(e)} onPointerCancel={(e) => onUp?.(e)} onClick={() => onPress(k)}
          aria-label={k === '⌫' ? tx('Clear', 'Xoá') : k}>{k}</button>
      ))}
    </div>
  )
}

function Dots({ n, shake }: { n: number; shake?: boolean }) {
  return (
    <div className={`cl-dots ${shake ? 'shake' : ''}`} aria-label={`${n}/${PIN_LEN}`}>
      {Array.from({ length: PIN_LEN }, (_, i) => <i key={i} className={i < n ? 'on' : ''} />)}
    </div>
  )
}

/** create the PIN, then type it again to confirm; nothing is recorded or sent here */
function PinSetup({ mode, expected, onDone, onBack }: { mode: 'create' | 'confirm'; expected?: string; onDone: (pin: string) => void; onBack?: () => void }) {
  const { tx } = useTx()
  const [digits, setDigits] = useState('')
  const [pressed, setPressed] = useState<string | null>(null)
  const [shake, setShake] = useState(false)
  const [note, setNote] = useState<string | null>(null)
  const press = (k: string) => {
    if (k === '⌫') { setDigits(''); setNote(null); return }
    if (!k || digits.length >= PIN_LEN) return
    const next = digits + k
    setDigits(next)
    if (next.length < PIN_LEN) return
    if (mode === 'create') { window.setTimeout(() => onDone(next), 150); return }
    if (next === expected) { window.setTimeout(() => onDone(next), 150); return }
    setShake(true); setNote(tx('The two PINs do not match. Try again.', 'Hai mã PIN không khớp. Nhập lại nhé.'))
    window.setTimeout(() => { setShake(false); setDigits('') }, 450)
  }
  return (
    <div className="cl cl-app">
      <div className="cl-pin">
        <h2>{mode === 'create' ? tx(`Create a ${PIN_LEN}-digit PIN`, `Tạo mã PIN ${PIN_LEN} số`) : tx('Enter it again to confirm', 'Nhập lại để xác nhận')}</h2>
        <p className="cl-hint">{mode === 'create'
          ? tx('Make one up and remember it: you will type it 5 times. Do not use a real PIN.', 'Hãy tự nghĩ một mã và nhớ nó: bạn sẽ nhập 5 lần. Đừng dùng PIN thật.')
          : tx('Same PIN as before.', 'Giống mã vừa tạo.')}</p>
        <Dots n={digits.length} shake={shake} />
        {note && <p className="cl-err" role="alert">{note}</p>}
        <div onPointerDown={(e) => { const b = (e.target as HTMLElement).closest('button'); if (b) setPressed(b.textContent) }} onPointerUp={() => setPressed(null)} onPointerCancel={() => setPressed(null)}>
          <Keypad pressed={pressed} onPress={press} />
        </div>
        {mode === 'confirm' && <button className="cl-link" onClick={onBack}>{tx('Choose a different PIN', 'Đổi mã PIN khác')}</button>}
      </div>
    </div>
  )
}

type Screen = 'home' | 'transfer' | 'pin' | 'sending' | 'ok' | 'finish'

function TransferApp({ profile, pin, done, onDone, onRestart }: { profile: Profile; pin: string; done: number; onDone: (n: number) => void; onRestart: () => void }) {
  const { tx, vnd, lang } = useTx()
  const [screen, setScreen] = useState<Screen>(done >= ENTRIES ? 'finish' : 'home')
  const [who, setWho] = useState(PEOPLE[0].id)
  const [amount, setAmount] = useState(AMOUNTS[1])
  const [digits, setDigits] = useState('')
  const [shake, setShake] = useState(false)
  const [pressed, setPressed] = useState<string | null>(null)
  const [err, setErr] = useState<string | null>(null)
  const rec = useRef(new Recorder())
  const pending = useRef<SessionIn | null>(null)

  const begin = () => { rec.current = new Recorder(); rec.current.screen('transfer'); setDigits(''); setErr(null); setScreen('transfer') }
  const toPin = () => { rec.current.screen('pin'); setScreen('pin') }
  const person = PEOPLE.find((p) => p.id === who)!

  async function send(s: SessionIn) {
    setScreen('sending'); setErr(null)
    try {
      const { session_id } = await api.createSession(s)
      // the first entries become the rhythm template (the API keeps it locked afterwards)
      if (done < ENROLL) {
        try { await api.enroll(s.user_id, session_id) } catch (e) { if (!(e instanceof ApiError && e.status === 409)) throw e }
      }
      pending.current = null; onDone(done + 1); setScreen('ok')
    } catch (e) {
      pending.current = s
      const st = e instanceof ApiError ? e.status : -1
      setErr(st === 0 ? tx('No connection. Check your network, then tap Retry.', 'Không có mạng. Kiểm tra kết nối rồi bấm Thử lại.')
        : st === 401 || st === 403 ? tx('This build has no API key configured. Tell the team.', 'Bản này chưa cấu hình khoá API. Báo cho đội.')
        : tx(`Could not send the data${st > 0 ? ` (${st})` : ''}. Tap Retry.`, `Lỗi gửi dữ liệu${st > 0 ? ` (${st})` : ''}. Bấm Thử lại.`))
      setScreen('pin')
    }
  }

  const press = (k: string) => {
    if (k === '⌫') { setDigits(''); rec.current.clearTaps(); return }
    if (!k || digits.length >= PIN_LEN) return
    const next = digits + k
    setDigits(next)
    if (next.length < PIN_LEN) return
    if (next !== pin) {
      setShake(true)
      window.setTimeout(() => { setShake(false); setDigits(''); rec.current.clearTaps() }, 450)
      return
    }
    window.setTimeout(() => {
      if (rec.current.taps.length < PIN_LEN) { setDigits(''); rec.current.clearTaps(); return } // no finger on a key
      const meta: CollectionMeta = { participant_id: profile.id, sitting: 1, role: 'genuine' }
      void send({ ...rec.current.payload(profile.id), meta })
    }, 0)
  }
  const keyDown = (e: RPointerEvent<HTMLButtonElement>, k: string) => {
    if (!k || k === '⌫') return
    rec.current.keyDown(e.nativeEvent, k, e.currentTarget); setPressed(k)
  }
  const keyUp = (e: RPointerEvent<HTMLButtonElement>) => { rec.current.keyUp(e.nativeEvent); setPressed(null) }
  const swipe = {
    onPointerDown: (e: RPointerEvent<HTMLDivElement>) => { e.currentTarget.setPointerCapture(e.pointerId); rec.current.swipeStart(e.nativeEvent) },
    onPointerMove: (e: RPointerEvent<HTMLDivElement>) => rec.current.swipeMove(e.nativeEvent),
    onPointerUp: () => { if (rec.current.swipeEnd() < -60) toPin() },
  }

  return (
    <div className="cl cl-app">
      <div className="cl-strip">
        <span>{tx('Data collection', 'Thu thập dữ liệu')} · {profile.name}</span>
        <b>{done}/{ENTRIES}</b>
      </div>

      {screen === 'home' && (
        <div className="cl-home">
          <header><span className="cl-logo">Innate Pay</span></header>
          <div className="cl-card"><span>{tx('Available balance', 'Số dư khả dụng')}</span><b>{vnd(12_450_000)}</b></div>
          <div className="cl-grid">
            <button className="cl-tile on" onClick={begin}><i>↗</i>{tx('Transfer', 'Chuyển tiền')}</button>
            <button className="cl-tile" disabled><i>＋</i>{tx('Top up', 'Nạp tiền')}</button>
            <button className="cl-tile" disabled><i>▤</i>{tx('Bills', 'Hóa đơn')}</button>
            <button className="cl-tile" disabled><i>☰</i>{tx('History', 'Lịch sử')}</button>
          </div>
          <p className="cl-hint">{tx('Tap Transfer, then enter the PIN you created.', 'Bấm Chuyển tiền, rồi nhập mã PIN bạn đã tạo.')}</p>
        </div>
      )}

      {screen === 'transfer' && (
        <div className="cl-transfer">
          <h2>{tx('Send money', 'Chuyển tiền')}</h2>
          <h3>{tx('Recipient', 'Người nhận')}</h3>
          {PEOPLE.map((p) => (
            <label key={p.id} className={`cl-person ${who === p.id ? 'on' : ''}`}>
              <input type="radio" name="to" checked={who === p.id} onChange={() => setWho(p.id)} />
              <i>{p.ini}</i><span><b>{p[lang]}</b><small>{p.acct}</small></span>
            </label>
          ))}
          <h3>{tx('Amount', 'Số tiền')}</h3>
          <div className="cl-amounts">
            {AMOUNTS.map((a) => (
              <label key={a} className={`cl-chip ${amount === a ? 'on' : ''}`}>
                <input type="radio" name="amt" checked={amount === a} onChange={() => setAmount(a)} />{vnd(a)}
              </label>
            ))}
          </div>
          <div className="cl-swipe" {...swipe} role="button" tabIndex={0}
            onKeyDown={(e) => { if (e.key === 'Enter') toPin() }}>
            <span aria-hidden="true">↑</span> {tx('Swipe up to confirm', 'Vuốt lên để xác nhận')}
          </div>
        </div>
      )}

      {(screen === 'pin' || screen === 'sending') && (
        <div className="cl-pin">
          <h2>{tx('Enter your PIN', 'Nhập mã PIN')}</h2>
          <p className="cl-sub">{tx(`Send ${vnd(amount)} to ${person.en}`, `Chuyển ${vnd(amount)} cho ${person.vi}`)}</p>
          <Dots n={digits.length} shake={shake} />
          {err && (
            <p className="cl-err" role="alert">{err}{' '}
              {pending.current && <button className="cl-link" onClick={() => void send(pending.current!)}>{tx('Retry', 'Thử lại')}</button>}</p>
          )}
          {screen === 'sending'
            ? <div className="cl-wait" role="status"><span className="cl-spin" aria-hidden="true" />{tx('Processing…', 'Đang xử lý…')}</div>
            : <Keypad pressed={pressed} disabled={!!pending.current && !!err} onPress={press} onDown={keyDown} onUp={keyUp} />}
          {screen === 'pin' && !pending.current && <button className="cl-link" onClick={onRestart}>{tx('I forgot my PIN', 'Tôi quên mã PIN')}</button>}
        </div>
      )}

      {screen === 'ok' && (
        <div className="cl-ok">
          <span className="cl-tick" aria-hidden="true">✓</span>
          <h2>{tx('Transfer successful', 'Chuyển tiền thành công')}</h2>
          <p>{vnd(amount)} → {person[lang]}</p>
          <button className="cl-btn" onClick={() => setScreen(done >= ENTRIES ? 'finish' : 'home')}>
            {done >= ENTRIES ? tx('Finish', 'Hoàn tất') : tx('Back to home', 'Về trang chủ')}
          </button>
        </div>
      )}

      {screen === 'finish' && (
        <div className="cl-ok">
          <span className="cl-tick" aria-hidden="true">✓</span>
          <h2>{tx('Thank you!', 'Cảm ơn bạn!')}</h2>
          <p>{tx('You have entered your PIN 5 times. Your data has been saved. You can close this page.', 'Bạn đã nhập PIN 5 lần. Dữ liệu đã được lưu. Bạn có thể đóng trang này.')}</p>
        </div>
      )}
    </div>
  )
}
