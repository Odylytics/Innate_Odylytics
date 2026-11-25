import { useEffect, useRef, useState, type PointerEvent as RPointerEvent } from 'react'
import { ApiError, api, type CollectionMeta, type SessionIn } from './api'
import { Recorder } from './capture'
import './collect.css'

// Data-collection page (#/collect): a plain transfer app for volunteers on their own phone. It records only times,
// finger positions and touch size (same SDK as the demo), never the digits, and sends them with a `meta` label.
// Phone only: on a desktop it shows a "open on your phone" notice (add ?dev=1 to test in devtools).
const PIN = '1593'
const KEYS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '', '0', '⌫']
const CONTACT = (import.meta.env.VITE_COLLECT_CONTACT as string | undefined) ?? 'người mời bạn tham gia'
const IDENT = /^[A-Za-z0-9_.-]{1,64}$/
const AMOUNTS = [200_000, 500_000, 1_000_000, 2_000_000]
const PEOPLE = [
  { id: 'a', name: 'Mẹ', acct: '0901 234 567', ini: 'M' },
  { id: 'b', name: 'Anh Tuấn (chủ nhà)', acct: '0912 888 120', ini: 'T' },
  { id: 'c', name: 'Lan Anh', acct: '0987 456 321', ini: 'L' },
]
const vnd = (n: number) => `${n.toLocaleString('vi-VN')} ₫`

interface Setup { code: string; role: 'genuine' | 'impostor'; owner: string; sitting: number; posture: string }
const SETUP_KEY = 'innate.collect.setup'
const loadSetup = (): Setup | null => { try { return JSON.parse(localStorage.getItem(SETUP_KEY) ?? 'null') } catch { return null } }
const doneKey = (s: Setup) => `innate.collect.done.${s.role}.${s.code}.${s.owner}.${s.sitting}`
const readDone = (s: Setup) => { try { return Number(localStorage.getItem(doneKey(s))) || 0 } catch { return 0 } }
// sitting 1: 3 enrolment entries + 5 test entries; later sittings and impostor rounds: 5 entries (docs/plan/thu-du-lieu-doi.md)
const ENROLL = 3
const targetOf = (s: Setup) => (s.role === 'genuine' && s.sitting === 1 ? ENROLL + 5 : 5)

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

  if (!phone) {
    return (
      <div className="cl cl-gate"><h1>Mở trang này trên điện thoại</h1>
        <p>Trang thu thập dữ liệu chỉ chạy trên điện thoại cảm ứng. Hãy mở lại đường link này bằng điện thoại của bạn.</p></div>
    )
  }
  if (!agreed) return <Consent onAgree={() => setAgreed(true)} />
  if (!setup) return <SetupForm onDone={(s) => { localStorage.setItem(SETUP_KEY, JSON.stringify(s)); setSetup(s) }} />
  return <TransferApp key={doneKey(setup)} setup={setup} onChange={() => { localStorage.removeItem(SETUP_KEY); setSetup(null) }} />
}

function Consent({ onAgree }: { onAgree: () => void }) {
  const [ok, setOk] = useState(false)
  return (
    <div className="cl cl-page">
      <h1>Phiếu đồng ý tham gia thu thập dữ liệu thao tác</h1>
      <p>Chúng tôi thu cách bạn chạm và gõ trên màn hình để nghiên cứu cho sản phẩm Innate tham dự MoMo Tech Contest 2026.</p>
      <ul>
        <li><b>Dữ liệu thu:</b> thời điểm và vị trí các lần chạm, kích thước vùng chạm, thời điểm các lần vuốt. <b>Không</b> ghi nội dung PIN, tên, số điện thoại, ảnh, giọng nói, vị trí hay tin nhắn.</li>
        <li><b>Ứng dụng này là giả:</b> không có tiền thật, không chuyển tiền thật. PIN thử là một số cố định hiển thị trên màn hình.</li>
        <li><b>Mục đích:</b> huấn luyện và đánh giá mô hình phát hiện bot và nhận ra chủ tài khoản; chỉ công bố số liệu tổng hợp.</li>
        <li><b>Lưu trữ:</b> dữ liệu gắn mã ẩn danh, không bán hay chia cho bên thứ ba. Bạn có thể từ chối, rút lui hoặc yêu cầu xem và xoá dữ liệu của mình bất cứ lúc nào: liên hệ {CONTACT}.</li>
        <li>Dữ liệu thao tác có thể là dữ liệu nhạy cảm theo Luật Bảo vệ dữ liệu cá nhân 2025; việc thu dựa trên sự đồng ý của bạn tại đây.</li>
      </ul>
      <label className="cl-check"><input type="checkbox" checked={ok} onChange={(e) => setOk(e.target.checked)} />
        <span>Tôi đã đọc và đồng ý tham gia.</span></label>
      <button className="cl-btn" disabled={!ok} onClick={onAgree}>Tiếp tục</button>
    </div>
  )
}

function SetupForm({ onDone }: { onDone: (s: Setup) => void }) {
  const [code, setCode] = useState('')
  const [role, setRole] = useState<Setup['role']>('genuine')
  const [owner, setOwner] = useState('')
  const [sitting, setSitting] = useState(1)
  const [posture, setPosture] = useState('ngồi')
  const codeOk = IDENT.test(code), ownerOk = role === 'genuine' || (IDENT.test(owner) && owner !== code)
  return (
    <div className="cl cl-page">
      <h1>Bắt đầu</h1>
      <label className="cl-field"><span>Mã tham gia (do đội cung cấp, vd. p07)</span>
        <input value={code} onChange={(e) => setCode(e.target.value.trim().toLowerCase())} autoCapitalize="none" autoCorrect="off" spellCheck={false} /></label>
      <fieldset className="cl-field"><legend>Bạn sẽ làm gì?</legend>
        <label className="cl-radio"><input type="radio" checked={role === 'genuine'} onChange={() => setRole('genuine')} /><span>Dùng ví của chính mình</span></label>
        <label className="cl-radio"><input type="radio" checked={role === 'impostor'} onChange={() => setRole('impostor')} /><span>Đóng vai người biết PIN, dùng ví của người khác</span></label>
      </fieldset>
      {role === 'impostor' && (
        <label className="cl-field"><span>Mã của chủ ví bạn đang thử</span>
          <input value={owner} onChange={(e) => setOwner(e.target.value.trim().toLowerCase())} autoCapitalize="none" autoCorrect="off" spellCheck={false} /></label>
      )}
      <label className="cl-field"><span>Lần ngồi thứ mấy? (1 = lần đầu, 2 = lần sau, cách ≥ 1 ngày)</span>
        <select value={sitting} onChange={(e) => setSitting(Number(e.target.value))}>{[1, 2, 3, 4].map((n) => <option key={n} value={n}>Lần {n}</option>)}</select></label>
      <label className="cl-field"><span>Tư thế lúc này</span>
        <select value={posture} onChange={(e) => setPosture(e.target.value)}>{['ngồi', 'đứng', 'đi bộ', 'nằm'].map((p) => <option key={p}>{p}</option>)}</select></label>
      <button className="cl-btn" disabled={!codeOk || !ownerOk} onClick={() => onDone({ code, role, owner: role === 'genuine' ? code : owner, sitting, posture })}>Mở ứng dụng</button>
    </div>
  )
}

type Screen = 'home' | 'transfer' | 'pin' | 'sending' | 'ok' | 'finish'

function TransferApp({ setup, onChange }: { setup: Setup; onChange: () => void }) {
  const target = targetOf(setup)
  const [done, setDone] = useState(() => readDone(setup))
  const [screen, setScreen] = useState<Screen>(done >= target ? 'finish' : 'home')
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
      // the first 3 entries of the owner's first sitting become the rhythm template (the API keeps it locked afterwards)
      if (setup.role === 'genuine' && setup.sitting === 1 && done < ENROLL) {
        try { await api.enroll(s.user_id, session_id) } catch (e) { if (!(e instanceof ApiError && e.status === 409)) throw e }
      }
      const n = done + 1
      localStorage.setItem(doneKey(setup), String(n)); setDone(n); pending.current = null; setScreen('ok')
    } catch (e) {
      pending.current = s
      setErr(e instanceof ApiError && e.status === 0 ? 'Không có mạng. Kiểm tra kết nối rồi bấm Thử lại.'
        : e instanceof ApiError && (e.status === 401 || e.status === 403) ? 'Bản này chưa cấu hình khoá API. Báo cho đội.'
        : `Lỗi gửi dữ liệu${e instanceof ApiError ? ` (${e.status})` : ''}. Bấm Thử lại.`)
      setScreen('pin')
    }
  }

  const press = (k: string) => {
    if (k === '⌫') { setDigits(''); rec.current.clearTaps(); return }
    if (!k || digits.length >= PIN.length) return
    const next = digits + k
    setDigits(next)
    if (next.length < PIN.length) return
    if (next !== PIN) {
      setShake(true)
      window.setTimeout(() => { setShake(false); setDigits(''); rec.current.clearTaps() }, 450)
      return
    }
    window.setTimeout(() => {
      if (rec.current.taps.length < PIN.length) { setDigits(''); rec.current.clearTaps(); return } // no finger on a key
      const meta: CollectionMeta = { participant_id: setup.code, sitting: setup.sitting, role: setup.role, note: setup.posture }
      void send({ ...rec.current.payload(setup.owner), meta })
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
        <span>Thu thập dữ liệu · {setup.code}{setup.role === 'impostor' ? ` → ${setup.owner}` : ''} · lần {setup.sitting}</span>
        <b>{Math.min(done, target)}/{target}</b>
      </div>

      {screen === 'home' && (
        <div className="cl-home">
          <header><span className="cl-logo">Innate Pay</span></header>
          <div className="cl-card"><span>Số dư khả dụng</span><b>12.450.000 ₫</b></div>
          <div className="cl-grid">
            <button className="cl-tile on" onClick={begin}><i>↗</i>Chuyển tiền</button>
            <button className="cl-tile" disabled><i>＋</i>Nạp tiền</button>
            <button className="cl-tile" disabled><i>▤</i>Hóa đơn</button>
            <button className="cl-tile" disabled><i>☰</i>Lịch sử</button>
          </div>
        </div>
      )}

      {screen === 'transfer' && (
        <div className="cl-transfer">
          <h2>Chuyển tiền</h2>
          <h3>Người nhận</h3>
          {PEOPLE.map((p) => (
            <label key={p.id} className={`cl-person ${who === p.id ? 'on' : ''}`}>
              <input type="radio" name="to" checked={who === p.id} onChange={() => setWho(p.id)} />
              <i>{p.ini}</i><span><b>{p.name}</b><small>{p.acct}</small></span>
            </label>
          ))}
          <h3>Số tiền</h3>
          <div className="cl-amounts">
            {AMOUNTS.map((a) => (
              <label key={a} className={`cl-chip ${amount === a ? 'on' : ''}`}>
                <input type="radio" name="amt" checked={amount === a} onChange={() => setAmount(a)} />{vnd(a)}
              </label>
            ))}
          </div>
          <div className="cl-swipe" {...swipe} role="button" tabIndex={0}
            onKeyDown={(e) => { if (e.key === 'Enter') toPin() }}>
            <span aria-hidden="true">↑</span> Vuốt lên để xác nhận
          </div>
        </div>
      )}

      {(screen === 'pin' || screen === 'sending') && (
        <div className="cl-pin">
          <h2>Nhập mã PIN</h2>
          <p className="cl-sub">Chuyển {vnd(amount)} cho {person.name}</p>
          <p className="cl-hint">Mã PIN thử: <b>{PIN}</b> (ứng dụng giả, không có tiền thật)</p>
          <div className={`cl-dots ${shake ? 'shake' : ''}`} aria-label={`${digits.length}/4`}>
            {[0, 1, 2, 3].map((i) => <i key={i} className={i < digits.length ? 'on' : ''} />)}
          </div>
          {err && (
            <p className="cl-err" role="alert">{err}{' '}
              {pending.current && <button className="cl-link" onClick={() => void send(pending.current!)}>Thử lại</button>}</p>
          )}
          {screen === 'sending'
            ? <div className="cl-wait" role="status"><span className="cl-spin" aria-hidden="true" />Đang xử lý…</div>
            : (
              <div className="cl-keys">
                {KEYS.map((k, i) => k === '' ? <span key={i} /> : (
                  <button key={i} className={`cl-key ${pressed === k ? 'down' : ''}`} disabled={!!pending.current && !!err}
                    onPointerDown={(e) => keyDown(e, k)} onPointerUp={keyUp} onPointerCancel={keyUp} onClick={() => press(k)}
                    aria-label={k === '⌫' ? 'Xoá' : k}>{k}</button>
                ))}
              </div>
            )}
        </div>
      )}

      {screen === 'ok' && (
        <div className="cl-ok">
          <span className="cl-tick" aria-hidden="true">✓</span>
          <h2>Chuyển tiền thành công</h2>
          <p>{vnd(amount)} → {person.name}</p>
          <button className="cl-btn" onClick={() => (done >= target ? setScreen('finish') : setScreen('home'))}>
            {done >= target ? 'Hoàn tất' : 'Về trang chủ'}
          </button>
        </div>
      )}

      {screen === 'finish' && (
        <div className="cl-ok">
          <span className="cl-tick" aria-hidden="true">✓</span>
          <h2>Cảm ơn bạn!</h2>
          <p>Bạn đã hoàn thành {target} lần nhập của phần này. Bạn có thể đóng trang.</p>
          <button className="cl-btn ghost" onClick={onChange}>Làm phần khác (đổi vai, lần ngồi)</button>
        </div>
      )}
    </div>
  )
}
