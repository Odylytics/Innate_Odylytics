import { useContext, useEffect, useState, type MouseEvent } from 'react'
import { LangContext } from '../i18n'
import { Atmosphere } from './Atmosphere'
import { HeroDevice } from './HeroDevice'
import { ACTION_STYLE, AppIcon, Arrow, Button, Eyebrow, jump, Logo, SectionHead, useL, type Action, type TT } from './ui'

/* ───────────── Nav ───────────── */
export function LangSwitch() {
  const { lang, setLang } = useContext(LangContext)
  return (
    <div className="flex rounded-full border border-line bg-surface p-0.5 text-[12px] font-bold" role="group" aria-label="Language">
      {(['vi', 'en'] as const).map((k) => (
        <button
          key={k}
          type="button"
          aria-pressed={lang === k}
          onClick={() => setLang(k)}
          className={`h-7 rounded-full px-2.5 uppercase transition-colors ${lang === k ? 'bg-ink text-canvas' : 'text-teal hover:text-ink'}`}
        >
          {k}
        </button>
      ))}
    </div>
  )
}

const NAV_LINKS: [string, TT][] = [
  ['signal', { en: 'Live signal', vi: 'Tín hiệu' }],
  ['demo', { en: 'Demo', vi: 'Demo' }],
  ['how', { en: 'How it works', vi: 'Cách hoạt động' }],
  ['privacy', { en: 'Privacy', vi: 'Quyền riêng tư' }],
  ['developers', { en: 'Developers', vi: 'Nhà phát triển' }],
]

function MenuIcon({ open }: { open: boolean }) {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
      {open ? (
        <path d="M5 5l10 10M15 5 5 15" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      ) : (
        <path d="M3 6h14M3 10h14M3 14h14" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      )}
    </svg>
  )
}

export function Nav() {
  const l = useL()
  const [open, setOpen] = useState(false)

  // Close on Escape, and when the viewport grows past the breakpoint where the inline links show.
  useEffect(() => {
    if (!open) return
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') setOpen(false) }
    const mq = window.matchMedia('(min-width: 1280px)')
    const onMq = () => { if (mq.matches) setOpen(false) }
    window.addEventListener('keydown', onKey)
    mq.addEventListener('change', onMq)
    return () => { window.removeEventListener('keydown', onKey); mq.removeEventListener('change', onMq) }
  }, [open])

  const go = (id: string) => (e: MouseEvent) => { setOpen(false); jump(id)(e) }

  return (
    <header id="lp-head" className="sticky top-0 z-50">
      <nav className="border-b border-line/60 bg-white/60 backdrop-blur-md" aria-label="Main">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between gap-3 px-5">
          <a href="#/" onClick={go('top')} aria-label="Innate" className="shrink-0">
            <Logo height={22} />
          </a>
          <div className="hidden items-center gap-7 text-[15px] font-medium text-teal xl:flex">
            {NAV_LINKS.map(([id, label]) => (
              <a key={id} href={`#${id}`} onClick={go(id)} className="whitespace-nowrap hover:text-ink">{l(label)}</a>
            ))}
            <a href="#/ops" className="whitespace-nowrap hover:text-ink">{l({ en: 'Ops', vi: 'Vận hành' })}</a>
            <a href="#/collect" className="whitespace-nowrap hover:text-ink">{l({ en: 'Join the study', vi: 'Tham gia thu dữ liệu' })}</a>
          </div>
          <div className="flex items-center gap-2 sm:gap-3">
            <LangSwitch />
            <Button href="#/demo?choose=1" className="!h-10 !px-4 text-sm sm:!px-5">
              {l({ en: 'Open demo', vi: 'Mở demo' })}
            </Button>
            <button
              type="button"
              className="flex h-10 w-10 items-center justify-center rounded-full border border-line bg-surface text-ink xl:hidden"
              aria-expanded={open}
              aria-controls="lp-menu"
              aria-label={open ? l({ en: 'Close menu', vi: 'Đóng menu' }) : l({ en: 'Open menu', vi: 'Mở menu' })}
              onClick={() => setOpen((v) => !v)}
            >
              <MenuIcon open={open} />
            </button>
          </div>
        </div>
        {open && (
          <div id="lp-menu" className="border-t border-line/80 bg-surface/95 xl:hidden">
            <ul className="mx-auto grid max-w-6xl gap-1 px-5 py-3 sm:grid-cols-2">
              {NAV_LINKS.map(([id, label]) => (
                <li key={id}>
                  <a href={`#${id}`} onClick={go(id)} className="flex min-h-12 items-center rounded-xl px-3 text-[16px] font-medium text-ink hover:bg-canvas">{l(label)}</a>
                </li>
              ))}
              <li>
                <a href="#/ops" onClick={() => setOpen(false)} className="flex min-h-12 items-center rounded-xl px-3 text-[16px] font-medium text-ink hover:bg-canvas">
                  {l({ en: 'Ops dashboard', vi: 'Bảng vận hành' })}
                </a>
              </li>
              <li>
                <a href="#/collect" onClick={() => setOpen(false)} className="flex min-h-12 items-center rounded-xl px-3 text-[16px] font-medium text-ink hover:bg-canvas">
                  {l({ en: 'Join the data collection', vi: 'Tham gia thu thập dữ liệu' })}
                </a>
              </li>
            </ul>
          </div>
        )}
      </nav>
    </header>
  )
}

/* ───────────── 01 Hero ───────────── */
export function Hero() {
  const l = useL()
  return (
    <section id="top" className="lp-hero relative -mt-[var(--lp-head)] overflow-hidden px-5 pb-24 pt-[calc(var(--lp-head)+2rem)] sm:pt-[calc(var(--lp-head)+2.5rem)] md:pb-32 md:pt-[calc(var(--lp-head)+3.5rem)] lg:flex lg:min-h-[min(100svh,60rem)] lg:items-center lg:pb-36 lg:pt-[calc(var(--lp-head)+5rem)] xl:pb-40">
      {/* pale-blue atmosphere that fades into the white page inside the hero (no seam) */}
      <Atmosphere />
      <div className="relative mx-auto grid w-full max-w-6xl items-center gap-10 md:grid-cols-[1.05fr_1fr] md:gap-8 lg:gap-16">
        <div className="animate-float-up">
          <a href="#how" onClick={jump('how')} className="inline-flex max-w-full items-center gap-2 rounded-full border border-line bg-surface/80 py-1 pl-1 pr-3 text-[13px] text-teal sm:pr-4">
            <span className="shrink-0 rounded-full bg-mist px-2.5 py-1 text-[11px] font-bold uppercase tracking-wider text-jade-ink">{l({ en: 'Behavioral AI', vi: 'AI hành vi' })}</span>
            <span className="truncate">{l({ en: 'Human or bot? Owner or not?', vi: 'Người hay máy? Chủ hay không?' })}</span> <Arrow />
          </a>
          <h1 className="mt-5 font-display text-[38px] font-semibold leading-[1.06] tracking-tight text-ink sm:text-[48px] md:mt-6 md:text-[44px] lg:mt-8 lg:text-[58px] xl:text-[72px]">
            {l({ en: 'Your behavior is your ', vi: 'Hành vi của bạn là ' })}
            <span className="whitespace-nowrap text-jade">{l({ en: 'signature.', vi: 'chữ ký.' })}</span>
          </h1>
          <p className="mt-4 max-w-xl text-[17px] leading-relaxed text-teal md:mt-5 lg:mt-7 lg:text-xl xl:text-[22px]">
            {l({
              en: 'Innate reads the rhythm behind every tap, swipe and transfer, quietly stopping remote-control malware and PIN thieves without adding friction for the real owner.',
              vi: 'Innate đọc nhịp đằng sau mỗi lần chạm, vuốt và chuyển tiền, lặng lẽ chặn mã độc điều khiển từ xa và kẻ lộ PIN mà không làm phiền chủ ví thật.',
            })}
          </p>
          {/* one action group: equal-width stack on phones and in the narrow tablet column, a row elsewhere */}
          <div className="mt-6 grid gap-2.5 sm:flex sm:flex-wrap sm:gap-3 md:grid md:gap-2.5 lg:mt-10 lg:flex lg:gap-3">
            <Button href="#/demo?story=1" className="justify-center">
              {l({ en: 'Watch the 2-minute demo', vi: 'Xem demo 2 phút' })} <Arrow />
            </Button>
            <Button href="#/demo" variant="ghost" className="justify-center">
              {l({ en: 'Try the demo wallet', vi: 'Tự thử ví demo' })}
            </Button>
            <Button href="#/collect" variant="ghost" className="justify-center">
              {l({ en: 'Join the data collection (phone only)', vi: 'Tham gia thu dữ liệu (chỉ trên điện thoại)' })}
            </Button>
          </div>
          <div className="mt-8 hidden flex-wrap gap-2 sm:flex lg:mt-10">
            {[
              { en: 'Human signal', vi: 'Tín hiệu người thật' },
              { en: 'Quiet security', vi: 'Bảo vệ lặng lẽ' },
              { en: 'Explainable by default', vi: 'Luôn giải thích được' },
            ].map((t) => (
              <span key={t.en} className="rounded-full border border-line bg-surface/60 px-3 py-1.5 text-[12px] font-semibold text-teal">{l(t)}</span>
            ))}
          </div>
        </div>
        <HeroDevice />
      </div>
    </section>
  )
}

/* ───────────── Full demo (the wallet, story and ops pages) ───────────── */
export function DemoPaths() {
  const l = useL()
  const paths: { href: string; tag: TT; title: TT; body: TT; cta: TT; dark?: boolean }[] = [
    {
      href: '#/demo?story=1',
      tag: { en: '~2 min · with sound', vi: '~2 phút · có âm thanh' },
      title: { en: 'Watch the story', vi: 'Xem tình huống' },
      body: {
        en: 'Hà enrolls, pays her mum, then malware types her PIN at 2 a.m. and a colleague tries with the PIN he saw. Seeded sessions, scored live.',
        vi: 'Hà đăng ký nhịp, chuyển tiền cho mẹ, rồi mã độc gõ PIN lúc 2 giờ sáng và đồng nghiệp thử bằng mã PIN đã nhìn lén. Phiên dựng sẵn, chấm thật trên API.',
      },
      cta: { en: 'Play the story', vi: 'Xem tình huống' },
      dark: true,
    },
    {
      href: '#/demo',
      tag: { en: 'PIN 159357 · live API', vi: 'PIN 159357 · API thật' },
      title: { en: 'Try the wallet yourself', vi: 'Tự thử ví demo' },
      body: {
        en: 'Enroll your rhythm with three PIN entries, send money, then let the attacker console replay malware or another person on the same screens.',
        vi: 'Đăng ký nhịp bằng 3 lần nhập PIN, chuyển tiền, rồi để bảng điều khiển kẻ tấn công thử lại bằng mã độc hoặc người khác trên cùng màn hình.',
      },
      cta: { en: 'Open the wallet', vi: 'Mở ví demo' },
    },
    {
      href: '#/ops',
      tag: { en: 'Ops key required', vi: 'Cần khoá vận hành' },
      title: { en: 'Review as the risk team', vi: 'Xem như đội rủi ro' },
      body: {
        en: 'Flagged sessions with their reasons. Label each one fraud or legit so the model learns from real cases.',
        vi: 'Các phiên bị gắn cờ kèm lý do. Gắn nhãn gian lận hay hợp lệ để mô hình học từ ca thật.',
      },
      cta: { en: 'Open the dashboard', vi: 'Mở bảng vận hành' },
    },
  ]
  return (
    <section id="demo" className="px-5 py-16 md:py-24 lg:py-28">
      <div className="mx-auto max-w-6xl">
        <SectionHead
          eyebrow={l({ en: '03 · The full demo', vi: '03 · Demo đầy đủ' })}
          title={l({ en: 'One wallet, three people, one PIN.', vi: 'Một ví, ba người, một mã PIN.' })}
          lead={l({
            en: 'The box above is the signal. The demo is the product: a wallet with the Innate SDK inside, every score coming from the live API.',
            vi: 'Ô phía trên là tín hiệu. Demo là sản phẩm: một ví có SDK Innate bên trong, mọi điểm số lấy từ API thật.',
          })}
        />
        <div className="mt-10 grid gap-5 md:mt-14 lg:grid-cols-3">
          {paths.map((p) => (
            <a
              key={p.href}
              href={p.href}
              className={`group flex flex-col rounded-[var(--radius-card)] p-7 transition-transform hover:-translate-y-1 ${p.dark ? 'bg-ink text-canvas' : 'border border-line bg-canvas/70 text-ink'}`}
            >
              <p className={`font-mono text-[11px] uppercase tracking-wider ${p.dark ? 'text-mint' : 'text-teal'}`}>{l(p.tag)}</p>
              <h3 className={`mt-4 font-display text-2xl font-semibold ${p.dark ? 'text-canvas' : 'text-ink'}`}>{l(p.title)}</h3>
              <p className={`mt-3 flex-1 text-[15px] leading-relaxed ${p.dark ? 'text-canvas/70' : 'text-teal'}`}>{l(p.body)}</p>
              <span className={`mt-8 inline-flex items-center gap-2 text-[15px] font-semibold ${p.dark ? 'text-mint' : 'text-ink'}`}>
                {l(p.cta)} <span className="transition-transform group-hover:translate-x-1"><Arrow /></span>
              </span>
            </a>
          ))}
        </div>
      </div>
    </section>
  )
}

/* ───────────── 04 Human vs bot vs impostor ───────────── */
type Persona = { who: TT; tag: TT; holds: number[]; gaps: number[]; spread: number; action: Action; signal: TT; body: TT }

const PERSONAS: Persona[] = [
  {
    who: { en: 'The owner', vi: 'Chủ ví' },
    tag: { en: 'Human · matches', vi: 'Người thật · khớp' },
    holds: [95, 110, 88, 102],
    gaps: [180, 210, 160],
    spread: 1,
    action: 'allow',
    signal: { en: 'Familiar rhythm, familiar thumb', vi: 'Nhịp quen, ngón tay quen' },
    body: {
      en: 'Same pace, same habit of landing a little up and to the right. Innate stays invisible.',
      vi: 'Cùng tốc độ, cùng thói quen chạm hơi lệch lên trên bên phải. Innate hoàn toàn vô hình.',
    },
  },
  {
    who: { en: 'Someone who knows the PIN', vi: 'Người biết mã PIN' },
    tag: { en: 'Human · not the owner', vi: 'Người thật · không phải chủ' },
    holds: [130, 145, 120, 138],
    gaps: [320, 290, 350],
    spread: 1,
    action: 'step_up',
    signal: { en: 'Right PIN, wrong hands', vi: 'Đúng PIN, sai bàn tay' },
    body: {
      en: 'A shoulder-surfer types 40% slower and lands left. The PIN is correct; the rhythm is not.',
      vi: 'Người nhìn lén gõ chậm hơn 40% và chạm lệch trái. Mã PIN đúng, nhưng nhịp thì không.',
    },
  },
  {
    who: { en: 'Remote-control malware', vi: 'Mã độc điều khiển từ xa' },
    tag: { en: 'Not a human finger', vi: 'Không phải ngón tay người' },
    holds: [60, 60, 60, 60],
    gaps: [140, 140, 140],
    spread: 0,
    action: 'hold',
    signal: { en: 'Too even, too exact', vi: 'Quá đều, quá chính xác' },
    body: {
      en: 'Accessibility-abuse malware taps with machine timing on the exact centre of every key.',
      vi: 'Mã độc lạm dụng Trợ năng chạm với nhịp của máy, trúng chính giữa mọi phím.',
    },
  },
]

function RhythmStrip({ p }: { p: Persona }) {
  const total = p.holds.reduce((a, b) => a + b, 0) + p.gaps.reduce((a, b) => a + b, 0)
  const starts = p.holds.map((_, i) => p.holds.slice(0, i).reduce((a, h, j) => a + h + (p.gaps[j] ?? 0), 0))
  return (
    <svg viewBox="0 0 300 64" className="h-16 w-full" aria-hidden="true">
      <line x1="0" y1="32" x2="300" y2="32" stroke="var(--color-line)" strokeDasharray="2 4" />
      {p.holds.map((h, i) => (
        <rect key={i} x={(starts[i] / total) * 300} y={14} width={(h / total) * 300} height={36} rx={6} fill={ACTION_STYLE[p.action].color} />
      ))}
    </svg>
  )
}

function TapScatter({ spread, action }: { spread: number; action: Action }) {
  const pts = [[0.14, -0.1], [0.2, -0.03], [0.08, -0.16], [0.17, -0.07], [0.24, -0.12], [0.11, -0.02]]
  const sign = action === 'step_up' ? -1 : 1
  return (
    <svg viewBox="-50 -35 100 70" className="h-20 w-28 shrink-0" aria-hidden="true">
      <rect x="-48" y="-33" width="96" height="66" rx="14" fill="var(--color-surface)" stroke="var(--color-line)" />
      <circle cx="0" cy="0" r="1.6" fill="var(--color-ink)" opacity="0.25" />
      {pts.map(([dx, dy], i) => (
        <circle key={i} cx={sign * dx * 100 * spread} cy={-sign * dy * 70 * spread} r={4} fill={ACTION_STYLE[action].color} opacity={spread ? 0.8 : 0.4} />
      ))}
    </svg>
  )
}

export function Personas() {
  const l = useL()
  return (
    <section id="signals" className="px-5 py-16 md:py-24 lg:py-28">
      <div className="mx-auto max-w-6xl">
        <SectionHead
          eyebrow={l({ en: '04 · Human vs bot vs impostor', vi: '04 · Người, máy hay kẻ mạo danh' })}
          title={l({ en: 'Same phone. Same PIN. Three very different hands.', vi: 'Cùng điện thoại. Cùng PIN. Ba bàn tay rất khác nhau.' })}
          lead={l({
            en: 'Passwords, OTPs and device checks all say “yes” in these three cases. The rhythm of the hand tells them apart.',
            vi: 'Mật khẩu, OTP và kiểm tra thiết bị đều nói “được” trong cả ba trường hợp. Nhịp của bàn tay thì phân biệt được.',
          })}
        />
        <div className="mt-10 grid gap-5 md:mt-14 lg:grid-cols-3">
          {PERSONAS.map((p) => {
            const s = ACTION_STYLE[p.action]
            return (
              <article key={p.who.en} className="flex flex-col rounded-[var(--radius-card)] border border-line bg-surface p-6">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-[12px] font-semibold uppercase tracking-wider text-teal">{l(p.tag)}</p>
                    <h3 className="mt-1 font-display text-xl font-semibold text-ink">{l(p.who)}</h3>
                  </div>
                  <span className={`shrink-0 rounded-full px-3 py-1 text-[12px] font-bold ${s.chip}`}>{l(s.label)}</span>
                </div>
                <div className="mt-6 rounded-2xl bg-canvas p-4">
                  <p className="font-mono text-[10px] uppercase tracking-wider text-teal">{l({ en: 'PIN rhythm', vi: 'Nhịp PIN' })}</p>
                  <RhythmStrip p={p} />
                  <div className="mt-2 flex items-center gap-4">
                    <TapScatter spread={p.spread} action={p.action} />
                    <p className="font-mono text-[11px] leading-relaxed text-teal">
                      {l({ en: 'hold', vi: 'giữ' })} {Math.min(...p.holds)}–{Math.max(...p.holds)} ms
                      <br />
                      {l({ en: 'gap', vi: 'nghỉ' })} {Math.min(...p.gaps)}–{Math.max(...p.gaps)} ms
                      <br />
                      {p.spread ? l({ en: 'off-centre taps', vi: 'chạm lệch tâm' }) : l({ en: 'dead-centre taps', vi: 'chạm trúng tâm' })}
                    </p>
                  </div>
                </div>
                <p className="mt-6 font-semibold text-ink">{l(p.signal)}</p>
                <p className="mt-2 text-[15px] leading-relaxed text-teal">{l(p.body)}</p>
              </article>
            )
          })}
        </div>
      </div>
    </section>
  )
}

/* ───────────── Three decisions ───────────── */
export function Decisions() {
  const l = useL()
  const items: { a: Action; when: TT; body: TT }[] = [
    { a: 'allow', when: { en: 'risk < 0.25', vi: 'rủi ro < 0.25' }, body: { en: 'The owner, behaving like the owner. No prompts, no extra steps: security you never notice.', vi: 'Chủ ví, thao tác như chính mình. Không hỏi thêm, không thêm bước: bảo vệ mà bạn không hề nhận ra.' } },
    { a: 'step_up', when: { en: '0.25 – 0.55', vi: '0.25 – 0.55' }, body: { en: 'Something is off. Ask for a short typed sentence before the money moves, instead of blocking outright.', vi: 'Có gì đó lạ. Yêu cầu gõ một câu ngắn trước khi chuyển tiền, thay vì chặn thẳng.' } },
    { a: 'hold', when: { en: 'risk > 0.55 or bot', vi: 'rủi ro > 0.55 hoặc bot' }, body: { en: 'Pause the transfer and tell the person. Innate suggests; it never locks an account on its own.', vi: 'Tạm giữ lệnh và báo cho người dùng. Innate chỉ đề xuất, không bao giờ tự khoá tài khoản.' } },
  ]
  return (
    <section className="px-5 py-16 md:py-24 lg:py-28">
      <div className="mx-auto max-w-6xl">
        <SectionHead
          eyebrow={l({ en: '05 · Three decisions', vi: '05 · Ba quyết định' })}
          title={l({ en: 'Not a wall. A graded, human-centred response.', vi: 'Không phải bức tường. Một phản hồi có mức độ, lấy con người làm trung tâm.' })}
          lead={l({
            en: 'Thresholds are configurable per partner. A small change shifts the balance between safety and friction, so it belongs in your hands.',
            vi: 'Ngưỡng do từng đối tác tự chỉnh. Một thay đổi nhỏ dịch chuyển cân bằng giữa an toàn và phiền hà, nên quyền đó thuộc về bạn.',
          })}
        />

        <div className="mt-10 md:mt-14 rounded-[var(--radius-card)] border border-line bg-surface p-6 md:p-8">
          <div className="flex justify-between font-mono text-[12px] text-teal">
            <span>0.00</span>
            <span>{l({ en: 'risk score', vi: 'điểm rủi ro' })}</span>
            <span>1.00</span>
          </div>
          <div className="relative mt-3 flex h-4 overflow-hidden rounded-full">
            <div className="bg-jade" style={{ width: '25%' }} />
            <div className="bg-stepup" style={{ width: '30%' }} />
            <div className="flex-1 bg-hold" />
          </div>
          <div className="relative mt-2 h-5 font-mono text-[12px] text-teal">
            <span className="absolute -translate-x-1/2" style={{ left: '25%' }}>A = 0.25</span>
            <span className="absolute -translate-x-1/2" style={{ left: '55%' }}>B = 0.55</span>
          </div>
        </div>

        <div className="mt-5 grid gap-5 md:grid-cols-3">
          {items.map(({ a, when, body }) => {
            const s = ACTION_STYLE[a]
            return (
              <div key={a} className="rounded-[var(--radius-card)] border border-line bg-surface p-7">
                <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
                  <span className={`h-3 w-3 shrink-0 rounded-full ${s.dot}`} />
                  <h3 className="font-display text-2xl font-semibold text-ink">{l(s.label)}</h3>
                  <span className="ml-auto text-right font-mono text-[12px] text-teal">{l(when)}</span>
                </div>
                <p className="mt-4 leading-relaxed text-teal">{l(body)}</p>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}

/* ───────────── Privacy ───────────── */
export function Privacy() {
  const l = useL()
  const items: [TT, TT][] = [
    [{ en: 'Rhythm, not content', vi: 'Nhịp, không phải nội dung' }, { en: 'The SDK sends touch timing and geometry. No screen recording, no keystrokes from text fields, no pressure readings.', vi: 'SDK chỉ gửi thời điểm và toạ độ chạm. Không quay màn hình, không ghi nội dung ô nhập, không đọc lực nhấn.' }],
    [{ en: 'Consent first', vi: 'Đồng ý trước' }, { en: "Behavioral data is treated as sensitive biometric data under Vietnam's 2025 Personal Data Protection Law, collected only with explicit consent.", vi: 'Dữ liệu hành vi được xem là dữ liệu sinh trắc nhạy cảm theo Luật Bảo vệ dữ liệu cá nhân 2025, chỉ thu khi người dùng đồng ý rõ ràng.' }],
    [{ en: 'Suggests, never locks', vi: 'Đề xuất, không khoá' }, { en: 'Innate recommends allow, step-up or hold. The partner and the person stay in control of the final call.', vi: 'Innate đề xuất cho qua, xác thực thêm hoặc giữ lệnh. Đối tác và người dùng giữ quyền quyết định cuối cùng.' }],
    [{ en: 'AI that shows its work', vi: 'AI có giải trình' }, { en: 'Every score ships with reason codes. Language models write case summaries for analysts; they are never on the decision path.', vi: 'Mỗi điểm số đi kèm mã lý do. Mô hình ngôn ngữ chỉ viết tóm tắt cho chuyên viên, không bao giờ nằm trên đường ra quyết định.' }],
  ]
  return (
    <section id="privacy" className="px-5 py-6">
      <div className="mx-auto max-w-6xl overflow-hidden rounded-[1.75rem] bg-ink px-5 py-14 sm:px-8 md:rounded-[2rem] md:px-14 md:py-20 lg:py-24">
        <div className="grid gap-14 lg:grid-cols-[1fr_1.2fr]">
          <div>
            <SectionHead
              dark
              eyebrow={l({ en: '07 · Privacy by design', vi: '07 · Riêng tư từ thiết kế' })}
              title={l({ en: 'We read the rhythm, never the words.', vi: 'Chúng tôi đọc nhịp, không bao giờ đọc chữ.' })}
              lead={l({
                en: 'Security that recognizes people should also respect them. These are product rules, not settings.',
                vi: 'Bảo mật nhận ra con người thì cũng phải tôn trọng con người. Đây là nguyên tắc sản phẩm, không phải tuỳ chọn.',
              })}
            />
            <AppIcon size={88} className="mt-10 hidden lg:block" />
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            {items.map(([t, b]) => (
              <div key={t.en} className="rounded-2xl border border-canvas/10 bg-canvas/[0.03] p-6">
                <span className="flex h-9 w-9 items-center justify-center rounded-full bg-jade/25">
                  <span className="h-2 w-2 rounded-full bg-mint" />
                </span>
                <h3 className="mt-5 font-display text-lg font-semibold text-canvas">{l(t)}</h3>
                <p className="mt-2 text-[15px] leading-relaxed text-canvas/65">{l(b)}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}

/* ───────────── API & dashboard ───────────── */
const FLAGGED: { id: string; user: string; action: Action; reasons: string; ago: string }[] = [
  { id: 's_8f21a0', user: 'minh.anh', action: 'hold', reasons: 'tap_exact_center · timing_too_regular', ago: '2m' },
  { id: 's_3c9e14', user: 'thu.ha', action: 'step_up', reasons: 'pin_rhythm_slower_40pct · new_recipient', ago: '11m' },
  { id: 's_b7d002', user: 'quoc.bao', action: 'step_up', reasons: 'tap_offset_left · amount_unusual', ago: '26m' },
]

export function Developers() {
  const l = useL()
  return (
    <section id="developers" className="px-5 py-16 md:py-24 lg:py-28">
      <div className="mx-auto max-w-6xl">
        <SectionHead
          eyebrow={l({ en: '08 · API & dashboard', vi: '08 · API & bảng vận hành' })}
          title={l({ en: 'One call for the app. One screen for the risk team.', vi: 'Một lần gọi cho app. Một màn hình cho đội rủi ro.' })}
          lead={l({
            en: 'Score a session at the confirm step, then let analysts review flagged sessions, read the reasons and mark each one right or wrong.',
            vi: 'Chấm điểm phiên ở bước xác nhận, rồi để chuyên viên xem các phiên bị gắn cờ, đọc lý do và đánh dấu đúng hay sai.',
          })}
        />
        <div className="mt-10 md:mt-14 grid gap-5 lg:grid-cols-2">
          <div className="min-w-0 overflow-hidden rounded-[var(--radius-card)] bg-ink">
            <div className="flex items-center gap-2 border-b border-canvas/10 px-5 py-3">
              <span className="h-2.5 w-2.5 rounded-full bg-canvas/15" />
              <span className="h-2.5 w-2.5 rounded-full bg-canvas/15" />
              <span className="h-2.5 w-2.5 rounded-full bg-canvas/15" />
              <span className="ml-3 truncate font-mono text-[12px] text-canvas/50">POST /v1/sessions/s_8f21/score</span>
            </div>
            <pre className="overflow-x-auto whitespace-pre-wrap break-words p-5 font-mono text-[12px] leading-relaxed text-canvas/80 sm:whitespace-pre sm:p-6 sm:text-[13px]">
{`{
  "session_id":  "s_8f21",
  "human_score": `}<span className="text-jade">0.97</span>{`,
  "owner_match": `}<span className="text-stepup">0.31</span>{`,
  "risk":        "medium",
  "action":      `}<span className="text-stepup">{'"step_up"'}</span>{`,
  "reasons": [
    "pin_rhythm_slower_40pct",
    "tap_offset_left",
    "new_recipient"
  ],
  "explanation_vi": "Thao tác giống người thật
    nhưng không khớp thói quen chủ…"
}`}
            </pre>
          </div>

          <div className="rounded-[var(--radius-card)] border border-line bg-surface p-6">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="font-display text-lg font-semibold text-ink">{l({ en: 'Flagged sessions', vi: 'Phiên bị gắn cờ' })}</p>
                <p className="text-[13px] text-teal">{l({ en: 'Step-up and hold · last hour', vi: 'Xác thực thêm và giữ lệnh · 1 giờ qua' })}</p>
              </div>
              <span className="shrink-0 rounded-full bg-mist px-3 py-1 text-[12px] font-bold text-jade-ink">{l({ en: '3 to review', vi: '3 cần xem' })}</span>
            </div>
            <ul className="mt-5 divide-y divide-line">
              {FLAGGED.map((f) => (
                <li key={f.id} className="py-4">
                  <div className="flex items-center gap-3">
                    <span className={`h-2.5 w-2.5 shrink-0 rounded-full ${ACTION_STYLE[f.action].dot}`} />
                    <span className="font-mono text-[13px] text-ink">{f.id}</span>
                    <span className="text-[13px] text-teal">{f.user}</span>
                    <span className="ml-auto text-[12px] text-teal/80">{f.ago}</span>
                  </div>
                  <p className="mt-1.5 break-words pl-5 font-mono text-[11.5px] text-teal">{f.reasons}</p>
                  <div className="mt-3 flex gap-2 pl-5">
                    <span className="rounded-full border border-line px-3 py-1 text-[12px] font-semibold text-teal">{l({ en: 'Legit', vi: 'Hợp lệ' })}</span>
                    <span className="rounded-full border border-hold/40 px-3 py-1 text-[12px] font-semibold text-[#8c3a30]">{l({ en: 'Fraud', vi: 'Gian lận' })}</span>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <dl className="mt-5 grid grid-cols-2 gap-5 md:grid-cols-4">
          {([
            ['16–21 ms', { en: 'server-side scoring', vi: 'chấm điểm phía máy chủ' }],
            ['3', { en: 'PIN entries to enroll', vi: 'lần nhập PIN để đăng ký' }],
            ['~40', { en: 'behavioral features', vi: 'đặc trưng hành vi' }],
            ['0', { en: 'LLM calls on the decision path', vi: 'lần gọi LLM trên đường quyết định' }],
          ] as [string, TT][]).map(([v, k]) => (
            <div key={k.en} className="rounded-[var(--radius-card)] border border-line bg-surface p-6">
              <dt className="sr-only">{l(k)}</dt>
              <dd className="font-display text-3xl font-semibold text-ink md:text-4xl">{v}</dd>
              <p className="mt-1 text-[14px] text-teal">{l(k)}</p>
            </div>
          ))}
        </dl>
      </div>
    </section>
  )
}

/* ───────────── CTA + footer ───────────── */
export function FinalCta() {
  const l = useL()
  return (
    <section className="px-5 pb-6">
      <div className="relative mx-auto max-w-6xl overflow-hidden rounded-[1.75rem] bg-navy px-5 py-14 text-center sm:px-8 md:rounded-[2rem] md:py-20 lg:py-24">
        <div className="absolute inset-0 bg-[radial-gradient(60%_80%_at_50%_120%,rgba(99,230,190,0.35),transparent)]" />
        <div className="relative">
          <Eyebrow dark>{l({ en: '09 · Feel the difference', vi: '09 · Cảm nhận sự khác biệt' })}</Eyebrow>
          <h2 className="mx-auto mt-5 max-w-3xl font-display text-[36px] font-semibold leading-[1.08] tracking-tight text-canvas md:text-[52px]">
            {l({ en: 'Security that recognizes your natural rhythm.', vi: 'Bảo mật nhận ra nhịp tự nhiên của bạn.' })}
          </h2>
          <p className="mx-auto mt-5 max-w-xl text-lg text-canvas/70">
            {l({
              en: 'Enroll in three PIN entries, hand the phone to a friend, and watch Innate tell you apart.',
              vi: 'Đăng ký bằng 3 lần nhập PIN, đưa máy cho một người bạn, và xem Innate phân biệt hai người.',
            })}
          </p>
          <div className="mt-9 flex flex-wrap justify-center gap-3">
            <Button href="#/demo" variant="light">
              {l({ en: 'Try the demo wallet', vi: 'Tự thử ví demo' })} <Arrow />
            </Button>
            <Button href="#/demo?story=1" variant="glass">
              {l({ en: 'Watch the 2-minute demo', vi: 'Xem demo 2 phút' })}
            </Button>
          </div>
        </div>
      </div>
    </section>
  )
}

export function Footer() {
  const l = useL()
  return (
    <footer className="px-5 py-12">
      <div className="mx-auto flex max-w-6xl flex-col gap-6 md:flex-row md:items-center md:justify-between">
        <Logo height={20} />
        <p className="text-[13px] text-teal">
          {l({ en: 'Built for MoMo Tech Contest 2026 · Behavioral risk scoring for e-wallets', vi: 'Dự thi MoMo Tech Contest 2026 · Chấm điểm rủi ro hành vi cho ví điện tử' })}
        </p>
      </div>
    </footer>
  )
}
