import { useEffect, useRef, useState } from 'react'
import { SectionHead, useL, type TT } from './ui'

const STEPS: { k: TT; title: TT; body: TT }[] = [
  {
    k: { en: 'Capture', vi: 'Thu' },
    title: { en: 'A tiny SDK listens to touch, not content', vi: 'SDK nhỏ chỉ nghe cách chạm, không đọc nội dung' },
    body: {
      en: 'Pointer Events on a self-drawn PIN pad record when each finger goes down and up, and where it lands. Swipes and screen pauses add context.',
      vi: 'Pointer Events trên bàn phím PIN tự vẽ ghi lại lúc ngón tay chạm xuống, nhấc lên và vị trí chạm. Thao tác vuốt và khoảng dừng trên màn hình bổ sung ngữ cảnh.',
    },
  },
  {
    k: { en: 'Extract', vi: 'Trích' },
    title: { en: '~40 features describe how you move', vi: '~40 đặc trưng mô tả cách bạn thao tác' },
    body: {
      en: "Hold time per key, pauses between keys, offset from each key's centre, swipe speed and straightness, time to first touch.",
      vi: 'Thời gian giữ từng phím, khoảng nghỉ giữa các phím, độ lệch khỏi tâm phím, tốc độ và độ thẳng khi vuốt, thời gian đến lần chạm đầu.',
    },
  },
  {
    k: { en: 'Score', vi: 'Chấm' },
    title: { en: 'Two questions, one risk score', vi: 'Hai câu hỏi, một điểm rủi ro' },
    body: {
      en: "Is this a human finger? Is it the owner's rhythm? Both are fused with transaction context (new recipient, unusual amount) in under 25 ms.",
      vi: 'Có phải ngón tay người? Có phải nhịp của chủ ví? Hai câu trả lời được gộp với ngữ cảnh giao dịch (người nhận mới, số tiền lạ) trong chưa tới 25 ms.',
    },
  },
  {
    k: { en: 'Explain', vi: 'Giải thích' },
    title: { en: 'Every decision says why', vi: 'Mỗi quyết định đều có lý do' },
    body: {
      en: 'The top deviations become a plain-language reason for the user and a case note for the risk team. Language models explain; they never decide.',
      vi: 'Các điểm lệch lớn nhất thành lý do dễ hiểu cho người dùng và ghi chú cho đội rủi ro. Mô hình ngôn ngữ chỉ giải thích, không bao giờ quyết định.',
    },
  },
]

function Panel({ step }: { step: number }) {
  const l = useL()
  if (step === 0)
    return (
      <pre className="overflow-x-auto whitespace-pre-wrap break-words font-mono text-[12px] leading-relaxed text-canvas/80 sm:whitespace-pre sm:text-[12.5px]">
        <span className="text-mint">{l({ en: '// one PIN tap, as the SDK sends it', vi: '// một lần chạm PIN, như SDK gửi đi' })}</span>
        {`
{
  "key": "5",
  "t_down": 280, "t_up": 408,     `}
        <span className="text-canvas/40">{'// ms'}</span>
        {`
  "x": 192, "y": 474,             `}
        <span className="text-canvas/40">{'// px'}</span>
        {`
  "w": 42,  "h": 41,              `}
        <span className="text-canvas/40">{l({ en: '// contact size', vi: '// cỡ vùng chạm' })}</span>
        {`
  "key_cx": 180, "key_cy": 480,
  "key_w": 100,  "key_h": 70
}`}
      </pre>
    )
  if (step === 1)
    return (
      <div className="grid grid-cols-2 gap-2 font-mono text-[12px]">
        {[
          ['pin_hold_1', '128 ms'],
          ['pin_flight_1', '232 ms'],
          ['pin_dx_1', '+0.12'],
          ['pin_dy_1', '−0.09'],
          ['pin_total', '1120 ms'],
          ['tap_w_mean', '40.5 px'],
          ['swipe_v_mean', '2.4 px/ms'],
          ['swipe_straight', '0.987'],
          ['screen_first_touch', '1.2 s'],
          ['…', l({ en: '+31 more', vi: '+31 nữa' })],
        ].map(([k, v]) => (
          <div key={k} className="flex justify-between gap-2 rounded-lg bg-canvas/5 px-3 py-2">
            <span className="truncate text-canvas/55">{k}</span>
            <span className="text-mint">{v}</span>
          </div>
        ))}
      </div>
    )
  if (step === 2)
    return (
      <div className="space-y-4">
        {([
          [l({ en: 'Human signal', vi: 'Tín hiệu người' }), 0.97, 'bg-jade'],
          [l({ en: 'Owner match', vi: 'Khớp chủ ví' }), 0.31, 'bg-stepup'],
          [l({ en: 'New recipient', vi: 'Người nhận mới' }), 1, 'bg-canvas/40'],
          [l({ en: 'Amount vs history', vi: 'Số tiền so với lịch sử' }), 0.2, 'bg-canvas/40'],
        ] as const).map(([k, v, c]) => (
          <div key={k}>
            <div className="flex justify-between text-[13px]">
              <span className="text-canvas/70">{k}</span>
              <span className="font-mono text-canvas">{v.toFixed(2)}</span>
            </div>
            <div className="mt-1.5 h-1.5 rounded-full bg-canvas/10">
              <div className={`h-full rounded-full ${c}`} style={{ width: `${v * 100}%` }} />
            </div>
          </div>
        ))}
        <div className="flex items-center justify-between rounded-xl border border-stepup/40 bg-stepup/10 px-4 py-3">
          <span className="text-sm text-canvas/80">{l({ en: 'risk', vi: 'rủi ro' })} 0.47 →</span>
          <span className="font-mono text-sm font-semibold text-stepup">step_up</span>
        </div>
      </div>
    )
  return (
    <div className="space-y-4">
      <div className="rounded-xl bg-canvas/5 p-4">
        <p className="font-mono text-[11px] uppercase tracking-wider text-mint">{l({ en: 'For the user', vi: 'Cho người dùng' })}</p>
        <p className="mt-2 text-[15px] leading-relaxed text-canvas">
          Looks like a real person, but not the account owner's habits (PIN rhythm 40% slower, taps land to the left). Please confirm with a face check before this transfer.
        </p>
      </div>
      <div className="rounded-xl bg-canvas/5 p-4">
        <p className="font-mono text-[11px] uppercase tracking-wider text-mint">{l({ en: 'Reason codes', vi: 'Mã lý do' })}</p>
        <div className="mt-2 flex flex-wrap gap-2">
          {['pin_rhythm_slower_40pct', 'tap_offset_left', 'new_recipient'].map((r) => (
            <span key={r} className="rounded-full bg-canvas/10 px-3 py-1 font-mono text-[12px] text-canvas/80">{r}</span>
          ))}
        </div>
      </div>
    </div>
  )
}

export function HowItWorks() {
  const l = useL()
  const [active, setActive] = useState(0)
  const refs = useRef<(HTMLLIElement | null)[]>([])

  useEffect(() => {
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) if (e.isIntersecting) setActive(Number((e.target as HTMLElement).dataset.i))
      },
      { rootMargin: '-45% 0px -45% 0px' },
    )
    refs.current.forEach((el) => el && io.observe(el))
    return () => io.disconnect()
  }, [])

  return (
    <section id="how" className="px-5 py-16 md:py-24 lg:py-28">
      <div className="mx-auto max-w-6xl">
        <SectionHead
          eyebrow={l({ en: '06 · How Innate works', vi: '06 · Innate hoạt động thế nào' })}
          title={l({ en: 'From a fingertip to a decision in four quiet steps', vi: 'Từ đầu ngón tay đến quyết định qua bốn bước lặng lẽ' })}
          lead={l({
            en: 'Innate drops into the confirm-transfer step of any wallet or banking app. One SDK, one API call.',
            vi: 'Innate gắn vào bước xác nhận chuyển tiền của bất kỳ ví hay app ngân hàng nào. Một SDK, một lần gọi API.',
          })}
        />
        <div className="mt-10 grid gap-8 md:mt-14 lg:gap-16 lg:grid-cols-2 lg:gap-16">
          <ol className="min-w-0 space-y-6 lg:space-y-[14vh] lg:pb-[20vh]">
            {STEPS.map((s, i) => (
              <li
                key={s.k.en}
                ref={(el) => { refs.current[i] = el }}
                data-i={i}
                className={`rounded-[var(--radius-card)] border p-6 md:p-7 transition-all duration-500 ${active === i ? 'border-jade bg-surface shadow-[0_14px_32px_-20px_rgba(13,27,42,0.25)]' : 'border-line bg-surface/50'}`}
              >
                <p className="font-mono text-[12px] text-teal">0{i + 1} / {l(s.k)}</p>
                <h3 className="mt-3 font-display text-2xl font-semibold text-ink">{l(s.title)}</h3>
                <p className="mt-3 leading-relaxed text-teal">{l(s.body)}</p>
                <div className="mt-6 rounded-2xl bg-ink p-5 lg:hidden">
                  <Panel step={i} />
                </div>
              </li>
            ))}
          </ol>
          <div className="hidden lg:block">
            <div className="sticky top-32 rounded-[var(--radius-card)] bg-ink p-8">
              <div className="mb-6 flex gap-2">
                {STEPS.map((s, i) => (
                  <span key={s.k.en} className={`rounded-full px-3 py-1 text-[12px] font-semibold transition-colors ${active === i ? 'bg-mint text-ink' : 'bg-canvas/5 text-canvas/55'}`}>
                    {l(s.k)}
                  </span>
                ))}
              </div>
              <div key={active} className="min-h-[300px] animate-float-up">
                <Panel step={active} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
