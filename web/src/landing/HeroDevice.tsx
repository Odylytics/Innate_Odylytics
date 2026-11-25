import { useEffect, useState } from 'react'
import { useT } from '../i18n'
import { ACTION_STYLE, useL, type Action, type TT } from './ui'

const KEYS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '', '0', '⌫']
const PIN = ['1', '5', '9', '3']

type Scenario = {
  who: TT
  holds: number[] // ms
  gaps: number[] // ms between taps
  offsets: [number, number][] // fraction of key size
  human: number
  owner: number | null
  action: Action
  reasons: string[]
  note: TT
}

// Values mirror the backend's synthetic personas and bot tactic 1 (backend/tests/synth.py). Illustration, not a live score.
const SCENARIOS: Scenario[] = [
  {
    who: { en: 'Account owner', vi: 'Chủ tài khoản' },
    holds: [95, 110, 88, 102],
    gaps: [180, 210, 160],
    offsets: [[0.15, -0.1], [0.2, -0.05], [0.1, -0.14], [0.18, -0.08]],
    human: 0.97,
    owner: 0.91,
    action: 'allow',
    reasons: ['rhythm_matches_owner'],
    note: { en: 'Rhythm matches the owner', vi: 'Nhịp khớp với chủ ví' },
  },
  {
    who: { en: 'Someone who knows the PIN', vi: 'Người biết mã PIN' },
    holds: [130, 145, 120, 138],
    gaps: [320, 290, 350],
    offsets: [[-0.12, 0.14], [-0.18, 0.1], [-0.08, 0.2], [-0.15, 0.12]],
    human: 0.96,
    owner: 0.21,
    action: 'step_up',
    reasons: ['pin_rhythm_slower_41pct', 'tap_offset_left'],
    note: { en: 'Human, but not the owner', vi: 'Người thật, nhưng không phải chủ ví' },
  },
  {
    who: { en: 'Remote-control malware', vi: 'Mã độc điều khiển từ xa' },
    holds: [60, 60, 60, 60],
    gaps: [140, 140, 140],
    offsets: [[0, 0], [0, 0], [0, 0], [0, 0]],
    human: 0.04,
    owner: 0.33,
    action: 'hold',
    reasons: ['timing_too_regular', 'tap_exact_center'],
    note: { en: 'Not a human finger', vi: 'Không phải ngón tay người' },
  },
]

export function HeroDevice() {
  const l = useL()
  const { money } = useT()
  const [i, setI] = useState(0)
  const [taps, setTaps] = useState(0) // taps shown so far in the current scenario; 5 = verdict
  const s = SCENARIOS[i]

  useEffect(() => {
    const timers: ReturnType<typeof setTimeout>[] = []
    let t = 700
    s.holds.forEach((h, k) => {
      timers.push(setTimeout(() => setTaps(k + 1), t))
      t += (h + (s.gaps[k] ?? 0)) * 2.2 // slowed down so the eye can follow
    })
    timers.push(setTimeout(() => setTaps(5), t + 300))
    timers.push(setTimeout(() => { setTaps(0); setI((v) => (v + 1) % SCENARIOS.length) }, t + 3600))
    return () => timers.forEach(clearTimeout)
  }, [i, s])

  const done = taps === 5
  const style = ACTION_STYLE[s.action]

  return (
    <div className="relative mx-auto w-full max-w-[520px] lg:max-w-[600px]">
      {/* soft warm glow */}
      <div className="absolute -inset-10 -z-10 rounded-full bg-[radial-gradient(closest-side,var(--color-mist),transparent)] opacity-90" />

      {/* phone */}
      <div className="relative mx-auto w-[256px] rounded-[44px] bg-ink p-3 shadow-[0_30px_60px_-30px_rgba(13,27,42,0.35)] sm:w-[280px] lg:w-[340px] lg:translate-x-6 lg:rounded-[52px] lg:p-3.5 xl:w-[372px]">
        <div className="overflow-hidden rounded-[34px] bg-canvas lg:rounded-[40px]">
          <div className="flex items-center justify-between px-6 pt-4 text-[11px] font-semibold text-ink/60 lg:px-8 lg:pt-5 lg:text-[13px]">
            <span>9:41</span>
            <span className="h-4 w-16 rounded-full bg-ink lg:h-5 lg:w-20" />
            <span>5G</span>
          </div>
          <div className="px-6 pt-6 text-center lg:px-8 lg:pt-8">
            <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-teal lg:text-[13px]">{l({ en: 'Confirm transfer', vi: 'Xác nhận chuyển tiền' })}</p>
            <p className="mt-2 font-display text-[26px] font-semibold text-ink lg:text-[34px] xl:text-[38px]">{money(2500000)}</p>
            <p className="text-[13px] text-teal lg:mt-1 lg:text-[16px]">{l({ en: 'to Minh Anh · ••• 4821', vi: 'tới Minh Anh · ••• 4821' })}</p>
            <div className="mt-6 flex justify-center gap-3 lg:mt-8 lg:gap-4">
              {PIN.map((_, k) => (
                <span key={k} className={`h-3 w-3 rounded-full transition-colors duration-200 lg:h-3.5 lg:w-3.5 ${taps > k ? 'bg-jade' : 'border border-line bg-surface'}`} />
              ))}
            </div>
          </div>
          <div className="mt-6 grid grid-cols-3 gap-2 px-5 pb-6 lg:mt-8 lg:gap-2.5 lg:px-6 lg:pb-8">
            {KEYS.map((k, idx) => {
              const pinIdx = PIN.indexOf(k)
              const active = pinIdx >= 0 && taps === pinIdx + 1
              const [dx, dy] = pinIdx >= 0 ? s.offsets[pinIdx] : [0, 0]
              return (
                <div key={idx} className={`relative flex h-12 items-center justify-center rounded-2xl font-display text-lg lg:h-14 lg:text-[22px] xl:h-[60px] xl:text-2xl ${k ? 'bg-surface text-ink shadow-[0_1px_0_var(--color-line)]' : ''}`}>
                  {k}
                  {active && (
                    <span className="pointer-events-none absolute h-6 w-6" style={{ left: `calc(50% + ${dx * 100}% - 12px)`, top: `calc(50% + ${dy * 100}% - 12px)` }}>
                      <span className="absolute inset-0 rounded-full bg-jade/50 animate-pulse-ring" />
                      <span className="absolute inset-[7px] rounded-full bg-jade" />
                    </span>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* live rhythm card */}
      <div className="absolute -left-12 -top-6 hidden w-[200px] rounded-2xl border border-line bg-surface/95 p-4 shadow-[0_14px_32px_-18px_rgba(13,27,42,0.28)] backdrop-blur lg:block xl:w-[220px] xl:p-5">
        <p className="font-mono text-[10px] uppercase tracking-wider text-teal xl:text-[11px]">{l({ en: 'PIN rhythm · ms', vi: 'Nhịp PIN · ms' })}</p>
        <div className="mt-3 flex h-14 items-end gap-1">
          {s.holds.map((h, k) => (
            <div key={k} className="flex items-end gap-1">
              <span className={`w-3 rounded-sm transition-all duration-300 ${taps > k ? 'bg-jade' : 'bg-line'}`} style={{ height: `${(h / 150) * 56}px` }} />
              {k < 3 && (
                <span className={`w-5 rounded-sm transition-all duration-300 ${taps > k + 1 ? 'bg-mint' : 'bg-line/60'}`} style={{ height: `${(s.gaps[k] / 360) * 56}px` }} />
              )}
            </div>
          ))}
        </div>
        <p className="mt-2 font-mono text-[10px] text-teal xl:text-[11px]">
          <span className="text-jade">▮</span> {l({ en: 'hold', vi: 'giữ' })} · <span className="text-mint">▮</span> {l({ en: 'gap', vi: 'nghỉ' })}
        </p>
      </div>

      {/* verdict card */}
      <div
        key={i}
        className={`absolute -bottom-6 -right-2 w-[230px] rounded-2xl border border-line bg-surface p-4 lg:w-[260px] lg:p-5 shadow-[0_14px_32px_-18px_rgba(13,27,42,0.28)] transition-all duration-500 lg:-right-8 ${done ? 'translate-y-0 opacity-100' : 'translate-y-3 opacity-0'}`}
      >
        <div className="flex items-center justify-between gap-2">
          <p className="text-[12px] font-semibold text-ink lg:text-[14px]">{l(s.who)}</p>
          <span className={`shrink-0 rounded-full px-2 py-0.5 text-[11px] font-bold lg:text-[12px] ${style.chip}`}>{l(style.label)}</span>
        </div>
        <dl className="mt-3 grid grid-cols-2 gap-2 font-mono text-[11px]">
          <div className="rounded-lg bg-canvas p-2">
            <dt className="text-teal">{l({ en: 'human', vi: 'người' })}</dt>
            <dd className="text-base font-semibold text-ink lg:text-lg">{s.human.toFixed(2)}</dd>
          </div>
          <div className="rounded-lg bg-canvas p-2">
            <dt className="text-teal">{l({ en: 'owner', vi: 'chủ ví' })}</dt>
            <dd className="text-base font-semibold text-ink lg:text-lg">{s.owner?.toFixed(2) ?? '—'}</dd>
          </div>
        </dl>
        <p className="mt-3 text-[12px] leading-snug text-teal lg:text-[14px]">{l(s.note)}</p>
        <p className="mt-1 truncate font-mono text-[10px] text-teal/70">{s.reasons.join(' · ')}</p>
      </div>
    </div>
  )
}
