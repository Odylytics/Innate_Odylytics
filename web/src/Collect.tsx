import { useEffect, useRef, useState, type PointerEvent as RPointerEvent } from 'react'
import { ApiError, api, type CollectionMeta, type SessionIn } from './api'
import { Recorder } from './capture'
import './collect.css'

// Data-collection page (#/collect): the volunteer types their name and email, creates their own 6-digit PIN and
// types it 5 times. All 5 entries are sent together at the end, with name + email in `meta` (they consent first).
// The PIN is their own, so key labels are masked ('*'): the API stores times and finger positions, never the digits.
// Phone only: on a desktop it shows a "open on your phone" notice (add ?dev=1 to test in devtools).
const PIN_LEN = 6
const ENTRIES = 5
const KEYS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '', '0', '⌫']
const CONTACT = (import.meta.env.VITE_COLLECT_CONTACT as string | undefined) ?? 'người mời bạn tham gia'
const EMAIL = /^[^@\s]+@[^@\s]+\.[^@\s]+$/

interface Setup { name: string; email: string; posture: string }
const SETUP_KEY = 'innate.collect.person'
const loadSetup = (): Setup | null => { try { return JSON.parse(localStorage.getItem(SETUP_KEY) ?? 'null') } catch { return null } }

// Stable id from the email (cyrb53), so sessions of one person group together across sittings.
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

// Sitting = how many different days this person has finished a round on this phone (same day = same sitting).
// shortcut: counted per phone in localStorage, a person switching phones restarts at 1; derive from created_at if that matters.
const today = () => new Date().toLocaleDateString('sv')
const lastKey = (id: string) => `innate.collect.last.${id}`
function sittingOf(id: string) {
  try {
    const last = JSON.parse(localStorage.getItem(lastKey(id)) ?? 'null') as { sitting: number; day: string } | null
    return !last ? 1 : last.day === today() ? last.sitting : Math.min(last.sitting + 1, 20)
  } catch { return 1 }
}

function isPhone() {
  return window.matchMedia('(pointer: coarse)').matches && Math.min(window.innerWidth, window.innerHeight) <= 600
}

export default function Collect() {
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

  const [setup, setSetup] = useState<Setup | null>(loadSetup)
  const [agreed, setAgreed] = useState(false)
  const [round, setRound] = useState(0)

  if (!phone) {
    return (
      <div className="cl cl-gate"><h1>Mở trang này trên điện thoại</h1>
        <p>Trang thu thập dữ liệu chỉ chạy trên điện thoại cảm ứng. Hãy mở lại đường link này bằng điện thoại của bạn.</p></div>
    )
  }
  if (!agreed) return <Consent onAgree={() => setAgreed(true)} />
  if (!setup) return <SetupForm onDone={(s) => { localStorage.setItem(SETUP_KEY, JSON.stringify(s)); setSetup(s) }} />
  return <PinRound key={round} setup={setup} onAgain={() => setRound((r) => r + 1)}
    onChange={() => { localStorage.removeItem(SETUP_KEY); setSetup(null) }} />
}

function Consent({ onAgree }: { onAgree: () => void }) {
  const [ok, setOk] = useState(false)
  return (
    <div className="cl cl-page">
      <h1>Phiếu đồng ý tham gia thu thập dữ liệu thao tác</h1>
      <p>Chúng tôi thu cách bạn chạm và gõ trên màn hình để nghiên cứu cho sản phẩm Innate tham dự MoMo Tech Contest 2026.</p>
      <ul>
        <li><b>Dữ liệu thu:</b> họ tên và email bạn nhập; thời điểm, vị trí và kích thước vùng chạm khi bạn gõ mã PIN. <b>Không</b> ghi các chữ số PIN, số điện thoại, ảnh, giọng nói, vị trí hay tin nhắn.</li>
        <li><b>Mã PIN:</b> bạn tự đặt một mã 6 số rồi nhập 5 lần. <b>Đừng dùng mã PIN ngân hàng hay ví thật của bạn.</b> Đây là ứng dụng giả, không có tiền thật.</li>
        <li><b>Mục đích:</b> huấn luyện và đánh giá mô hình phát hiện bot và nhận ra chủ tài khoản; chỉ công bố số liệu tổng hợp, không công bố tên hay email.</li>
        <li><b>Lưu trữ:</b> họ tên, email và dữ liệu chạm lưu cùng nhau trong cơ sở dữ liệu của đội, không bán hay chia cho bên thứ ba. Bạn có thể từ chối, rút lui hoặc yêu cầu xem và xoá dữ liệu của mình bất cứ lúc nào: liên hệ {CONTACT}.</li>
        <li>Họ tên, email và dữ liệu thao tác là dữ liệu cá nhân (dữ liệu thao tác có thể là dữ liệu nhạy cảm) theo Luật Bảo vệ dữ liệu cá nhân 2025; việc thu dựa trên sự đồng ý của bạn tại đây.</li>
      </ul>
      <label className="cl-check"><input type="checkbox" checked={ok} onChange={(e) => setOk(e.target.checked)} />
        <span>Tôi đã đọc và đồng ý tham gia.</span></label>
      <button className="cl-btn" disabled={!ok} onClick={onAgree}>Tiếp tục</button>
    </div>
  )
}

function SetupForm({ onDone }: { onDone: (s: Setup) => void }) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [posture, setPosture] = useState('ngồi')
  const n = name.trim().replace(/\s+/g, ' '), m = email.trim().toLowerCase()
  const ok = n.length >= 2 && n.length <= 100 && EMAIL.test(m) && m.length <= 254
  return (
    <div className="cl cl-page">
      <h1>Bắt đầu</h1>
      <label className="cl-field"><span>Họ và tên</span>
        <input value={name} onChange={(e) => setName(e.target.value)} autoComplete="name" maxLength={100} /></label>
      <label className="cl-field"><span>Email</span>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" inputMode="email"
          autoCapitalize="none" autoCorrect="off" spellCheck={false} maxLength={254} /></label>
      <label className="cl-field"><span>Tư thế lúc này</span>
        <select value={posture} onChange={(e) => setPosture(e.target.value)}>{['ngồi', 'đứng', 'đi bộ', 'nằm'].map((p) => <option key={p}>{p}</option>)}</select></label>
      <button className="cl-btn" disabled={!ok} onClick={() => onDone({ name: n, email: m, posture })}>Tạo mã PIN</button>
    </div>
  )
}

function PinRound({ setup, onAgain, onChange }: { setup: Setup; onAgain: () => void; onChange: () => void }) {
  const id = idOf(setup.email)
  const [sitting] = useState(() => sittingOf(id))
  const [count, setCount] = useState(0) // correct entries so far (the first one creates the PIN)
  const [digits, setDigits] = useState('')
  const [shake, setShake] = useState(false)
  const [pressed, setPressed] = useState<string | null>(null)
  const [msg, setMsg] = useState<string | null>(null)
  const [state, setState] = useState<'pin' | 'sending' | 'failed' | 'done'>('pin')
  const pin = useRef('') // kept in memory only, never sent or stored
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
      localStorage.setItem(lastKey(id), JSON.stringify({ sitting, day: today() }))
      setState('done')
    } catch (e) {
      setMsg(e instanceof ApiError && e.status === 0 ? 'Không có mạng. Kiểm tra kết nối rồi bấm Gửi lại.'
        : e instanceof ApiError && (e.status === 401 || e.status === 403) ? 'Bản này chưa cấu hình khoá API. Báo cho đội.'
        : `Lỗi gửi dữ liệu${e instanceof ApiError ? ` (${e.status})` : ''}. Bấm Gửi lại.`)
      setState('failed')
    }
  }

  const press = (k: string) => {
    if (k === '⌫') { reset(); return }
    if (!k || digits.length >= PIN_LEN) return
    const next = digits + k
    setDigits(next); setMsg(null)
    if (next.length < PIN_LEN) return
    if (count > 0 && next !== pin.current) {
      setShake(true); setMsg('Không khớp mã đã tạo. Nhập lại.')
      window.setTimeout(() => { setShake(false); reset() }, 450)
      return
    }
    window.setTimeout(() => {
      if (rec.current.taps.length < PIN_LEN) { reset(); return } // a digit came without a finger on the key
      if (count === 0) pin.current = next
      const meta: CollectionMeta = { participant_id: id, sitting, role: 'genuine', note: setup.posture,
        full_name: setup.name, email: setup.email }
      queue.current.push({ ...rec.current.payload(id), meta })
      rec.current = new Recorder(); rec.current.screen('pin'); setDigits('')
      const n = count + 1
      setCount(n)
      if (n === ENTRIES) { pin.current = ''; void sendAll() }
    }, 0)
  }
  // the label is masked: the PIN is the volunteer's own, so the digits must not leave the phone
  const keyDown = (e: RPointerEvent<HTMLButtonElement>, k: string) => {
    if (!k || k === '⌫') return
    rec.current.keyDown(e.nativeEvent, '*', e.currentTarget); setPressed(k)
  }
  const keyUp = (e: RPointerEvent<HTMLButtonElement>) => { rec.current.keyUp(e.nativeEvent); setPressed(null) }

  if (state === 'done') {
    return (
      <div className="cl cl-app"><div className="cl-ok">
        <span className="cl-tick" aria-hidden="true">✓</span>
        <h2>Cảm ơn {setup.name}!</h2>
        <p>Đã ghi nhận {ENTRIES} lần nhập (lần ngồi {sitting}). Bạn có thể đóng trang.</p>
        <button className="cl-btn" onClick={onAgain}>Làm thêm một lượt</button>
        <button className="cl-btn ghost" onClick={onChange}>Đổi người tham gia</button>
      </div></div>
    )
  }

  return (
    <div className="cl cl-app">
      <div className="cl-strip"><span>Thu thập dữ liệu · {setup.name} · lần ngồi {sitting}</span><b>{count}/{ENTRIES}</b></div>
      <div className="cl-pin">
        <h2>{count === 0 ? 'Tạo mã PIN 6 số' : 'Nhập lại mã PIN'}</h2>
        <p className="cl-sub">{count === 0 ? 'Chọn mã dễ nhớ, đừng dùng PIN thật.' : `Lần ${count + 1}/${ENTRIES}: nhập đúng mã vừa tạo`}</p>
        <div className={`cl-dots ${shake ? 'shake' : ''}`} aria-label={`${digits.length}/${PIN_LEN}`}>
          {Array.from({ length: PIN_LEN }, (_, i) => <i key={i} className={i < digits.length ? 'on' : ''} />)}
        </div>
        {/* always rendered so the keypad does not jump when a message appears */}
        <p className="cl-err" role="alert">{msg}{' '}
          {msg && state === 'failed' && <button className="cl-link" onClick={() => { setMsg(null); void sendAll() }}>Gửi lại</button>}</p>
        {state === 'sending' || state === 'failed'
          ? state === 'sending' && <div className="cl-wait" role="status"><span className="cl-spin" aria-hidden="true" />Đang ghi nhận…</div>
          : (
            <div className="cl-keys">
              {KEYS.map((k, i) => k === '' ? <span key={i} /> : (
                <button key={i} className={`cl-key ${pressed === k ? 'down' : ''}`}
                  onPointerDown={(e) => keyDown(e, k)} onPointerUp={keyUp} onPointerCancel={keyUp} onClick={() => press(k)}
                  aria-label={k === '⌫' ? 'Xoá' : k}>{k}</button>
              ))}
            </div>
          )}
      </div>
    </div>
  )
}
