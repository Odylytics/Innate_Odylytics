import { useRef, useState, type PointerEvent } from 'react'
import { Arrow, SectionHead, useL } from './ui'

type Tap = { key: string; down: number; up: number; dx: number; dy: number }

const KEYS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '', '0', '']
const LEN = 4
const BOT_PIN = ['1', '5', '9', '3']

const mean = (xs: number[]) => xs.reduce((a, b) => a + b, 0) / xs.length
const cv = (xs: number[]) => {
  const m = mean(xs)
  return m > 0 ? Math.sqrt(mean(xs.map((x) => (x - m) ** 2))) / m : 0
}
const clip = (v: number) => Math.min(Math.max(v, 0), 1)

/** Same "naturalness" rules as the backend baseline (backend/app/scoring/human.py). Runs in the browser only. */
function humanScore(taps: Tap[]) {
  const holds = taps.map((t) => t.up - t.down)
  const gaps = taps.slice(1).map((t, i) => t.down - taps[i].up)
  const timingCv = Math.min(cv(holds), gaps.length >= 2 ? cv(gaps) : Infinity)
  const dist = mean(taps.map((t) => Math.hypot(t.dx, t.dy)))
  const regular = clip((0.08 - timingCv) / 0.08)
  const centered = clip((0.06 - dist) / 0.06)
  return { score: 1 - Math.max(regular, centered), timingCv, dist, regular, centered, holds, gaps }
}

export function SignalDemo() {
  const l = useL()
  const [taps, setTaps] = useState<Tap[]>([])
  const [source, setSource] = useState<'you' | 'bot' | null>(null)
  const [pressed, setPressed] = useState<string | null>(null)
  const t0 = useRef(0)
  const pending = useRef<Partial<Tap> | null>(null)
  const botRunning = useRef(false)

  const reset = () => { setTaps([]); setSource(null) }

  const onDown = (key: string, e: PointerEvent<HTMLButtonElement>) => {
    if (botRunning.current) return
    if (taps.length >= LEN) reset()
    const r = e.currentTarget.getBoundingClientRect()
    if (taps.length === 0 || taps.length >= LEN) t0.current = e.timeStamp
    setSource('you')
    setPressed(key)
    pending.current = {
      key,
      down: e.timeStamp - t0.current,
      dx: (e.clientX - (r.left + r.width / 2)) / r.width,
      dy: (e.clientY - (r.top + r.height / 2)) / r.height,
    }
  }

  const onUp = (e: PointerEvent<HTMLButtonElement>) => {
    const p = pending.current
    if (!p) return
    pending.current = null
    setPressed(null)
    setTaps((prev) => [...(prev.length >= LEN ? [] : prev), { ...(p as Tap), up: e.timeStamp - t0.current }])
  }

  const runBot = () => {
    if (botRunning.current) return
    botRunning.current = true
    setTaps([])
    setSource('bot')
    // Tactic 1: 60 ms hold, 140 ms gap, exact key centre, like `adb shell input tap`.
    let t = 0
    BOT_PIN.forEach((key, i) => {
      const down = t
      setTimeout(() => setPressed(key), 300 + i * 420)
      setTimeout(() => {
        setPressed(null)
        setTaps((prev) => [...prev, { key, down, up: down + 60, dx: 0, dy: 0 }])
        if (i === BOT_PIN.length - 1) botRunning.current = false
      }, 300 + i * 420 + 160)
      t += 200
    })
  }

  const done = taps.length === LEN
  const r = done ? humanScore(taps) : null
  const verdict = !r ? null : r.score < 0.3 ? 'hold' : r.score < 0.7 ? 'step_up' : 'allow'
  const total = taps.length ? Math.max(...taps.map((t) => t.up)) : 1
  const tapColor = source === 'bot' ? 'bg-hold' : 'bg-jade'

  const why = r && verdict !== 'allow'
    ? [r.regular > 0.25 && l({ en: 'timing is too even', vi: 'nhịp đều quá mức' }), r.centered > 0.25 && l({ en: 'every tap hits the exact centre', vi: 'mọi lần chạm đều trúng tâm phím' })]
        .filter(Boolean)
        .join(l({ en: ' and ', vi: ' và ' }))
    : ''

  return (
    <section id="signal" className="px-5 pb-16 pt-4 md:pb-24 md:pt-6 lg:pb-28 lg:pt-8">
      <div className="mx-auto max-w-6xl">
        <SectionHead
          eyebrow={l({ en: '02 · Live signal', vi: '02 · Tín hiệu trực tiếp' })}
          title={
            <>
              {l({ en: 'Tap any four keys.', vi: 'Chạm bốn phím bất kỳ.' })}
              <br />
              <span className="text-jade">{l({ en: 'Watch your rhythm appear.', vi: 'Xem nhịp của bạn hiện ra.' })}</span>
            </>
          }
          lead={l({
            en: 'This is the same signal Innate reads at checkout: how long you hold each key, the pause between them, and where your finger lands. Then let a bot try.',
            vi: 'Đây chính là tín hiệu Innate đọc lúc xác nhận chuyển tiền: bạn giữ mỗi phím bao lâu, nghỉ giữa hai phím bao lâu, và ngón tay chạm vào đâu. Rồi để một con bot thử.',
          })}
        />

        <div className="mt-10 md:mt-14 grid gap-6 lg:grid-cols-[380px_1fr]">
          {/* keypad */}
          <div className="rounded-[var(--radius-card)] border border-line bg-surface p-6">
            <div className="flex justify-center gap-3 pb-6">
              {Array.from({ length: LEN }).map((_, k) => (
                <span key={k} className={`h-3.5 w-3.5 rounded-full transition-colors ${taps.length > k ? tapColor : 'border border-line'}`} />
              ))}
            </div>
            <div className="grid grid-cols-3 gap-3">
              {KEYS.map((k, i) =>
                k ? (
                  <button
                    key={i}
                    type="button"
                    onPointerDown={(e) => onDown(k, e)}
                    onPointerUp={onUp}
                    onPointerLeave={(e) => pending.current && onUp(e)}
                    className={`relative h-16 touch-none select-none rounded-2xl font-display text-2xl text-ink transition-all ${pressed === k ? 'scale-95 bg-mist' : 'bg-canvas hover:bg-mist/70'}`}
                  >
                    {k}
                    {/* where the finger landed */}
                    {taps.filter((t) => t.key === k).map((t, j) => (
                      <span key={j} className={`absolute h-2.5 w-2.5 -translate-x-1/2 -translate-y-1/2 rounded-full ${tapColor}`} style={{ left: `${50 + t.dx * 100}%`, top: `${50 + t.dy * 100}%` }} />
                    ))}
                    {/* key centre marker */}
                    <span className="absolute left-1/2 top-1/2 h-1 w-1 -translate-x-1/2 -translate-y-1/2 rounded-full bg-ink/15" />
                  </button>
                ) : (
                  <span key={i} />
                ),
              )}
            </div>
            <div className="mt-6 flex gap-3">
              <button type="button" onClick={runBot} className="h-11 flex-1 rounded-full bg-ink text-sm font-semibold text-canvas transition-colors hover:bg-navy">
                {l({ en: 'Let a bot try', vi: 'Để bot thử' })}
              </button>
              <button type="button" onClick={reset} className="h-11 rounded-full border border-line px-5 text-sm font-semibold text-ink hover:border-jade">
                {l({ en: 'Reset', vi: 'Làm lại' })}
              </button>
            </div>
          </div>

          {/* readout */}
          <div className="flex flex-col rounded-[var(--radius-card)] bg-ink p-6 text-canvas md:p-8">
            <div className="flex items-center justify-between gap-3">
              <p className="font-mono text-[11px] uppercase tracking-wider text-mint">{l({ en: 'Rhythm timeline', vi: 'Dòng thời gian nhịp' })}</p>
              <p className="font-mono text-[11px] text-canvas/50">
                {taps.length}/{LEN} · {source === 'bot' ? l({ en: 'source: script', vi: 'nguồn: kịch bản' }) : source === 'you' ? l({ en: 'source: you', vi: 'nguồn: bạn' }) : l({ en: 'waiting', vi: 'đang chờ' })}
              </p>
            </div>

            <div className="relative mt-6 h-20 rounded-xl bg-canvas/5">
              {taps.map((t, k) => (
                <span
                  key={k}
                  className={`absolute top-1/2 h-10 -translate-y-1/2 rounded-md ${source === 'bot' ? 'bg-hold' : 'bg-mint'}`}
                  style={{ left: `${(t.down / total) * 96 + 2}%`, width: `${Math.max(((t.up - t.down) / total) * 96, 1.2)}%` }}
                />
              ))}
              {!taps.length && <p className="absolute inset-0 flex items-center justify-center text-sm text-canvas/50">{l({ en: 'Tap the keypad to start', vi: 'Chạm bàn phím để bắt đầu' })}</p>}
            </div>

            <dl className="mt-6 grid grid-cols-2 gap-3 md:grid-cols-4">
              {[
                [l({ en: 'Avg hold', vi: 'Giữ TB' }), r ? `${Math.round(mean(r.holds))} ms` : '—'],
                [l({ en: 'Avg gap', vi: 'Nghỉ TB' }), r ? `${Math.round(mean(r.gaps))} ms` : '—'],
                [l({ en: 'Timing variation', vi: 'Độ dao động nhịp' }), r ? `${(r.timingCv * 100).toFixed(0)}%` : '—'],
                [l({ en: 'Off-centre', vi: 'Lệch tâm' }), r ? `${(r.dist * 100).toFixed(0)}% ${l({ en: 'key', vi: 'phím' })}` : '—'],
              ].map(([k, v]) => (
                <div key={k} className="rounded-xl bg-canvas/5 p-3">
                  <dt className="text-[11px] text-canvas/55">{k}</dt>
                  <dd className="mt-1 font-mono text-lg">{v}</dd>
                </div>
              ))}
            </dl>

            <div className="mt-auto pt-8">
              <div className="flex items-end justify-between">
                <p className="text-sm text-canvas/60">{l({ en: 'Human score', vi: 'Điểm người thật' })}</p>
                <p className="font-mono text-4xl font-semibold">{r ? r.score.toFixed(2) : '—'}</p>
              </div>
              <div className="mt-3 h-2 overflow-hidden rounded-full bg-canvas/10">
                <div
                  className={`h-full rounded-full transition-all duration-700 ${verdict === 'hold' ? 'bg-hold' : verdict === 'step_up' ? 'bg-stepup' : 'bg-jade'}`}
                  style={{ width: `${(r?.score ?? 0) * 100}%` }}
                />
              </div>
              <p className="mt-4 min-h-[48px] text-[15px] leading-relaxed text-canvas/80">
                {!r && l({ en: 'Your hold times and pauses will never be perfectly even. That unevenness is the signal.', vi: 'Thời gian giữ phím và khoảng nghỉ của bạn không bao giờ đều tuyệt đối. Chính sự không đều đó là tín hiệu.' })}
                {r && verdict === 'allow' && l({ en: 'Natural variation in timing and touch position. This looks like a human finger.', vi: 'Nhịp và vị trí chạm dao động tự nhiên. Đây là ngón tay người.' })}
                {r && verdict !== 'allow' && `${l({ en: 'Looks scripted: ', vi: 'Giống kịch bản tự động: ' })}${why}.`}
              </p>
            </div>
          </div>
        </div>
        <div className="mt-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <p className="text-[13px] text-teal">
            {l({
              en: 'Runs entirely in your browser; nothing from this box is sent anywhere. Human-vs-bot only: matching the owner needs an enrolled rhythm.',
              vi: 'Chạy hoàn toàn trong trình duyệt, không gửi gì đi. Chỉ phân biệt người và máy: muốn khớp chủ ví cần đăng ký nhịp trước.',
            })}
          </p>
          <a href="#/demo" className="inline-flex shrink-0 items-center gap-2 text-[14px] font-semibold text-ink hover:text-jade-ink">
            {l({ en: 'Enroll your rhythm on the demo wallet', vi: 'Đăng ký nhịp trên ví demo' })} <Arrow />
          </a>
        </div>
      </div>
    </section>
  )
}
