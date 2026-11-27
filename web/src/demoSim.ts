// Static wallet demo (#/demo): no API calls, nothing stored. Enrollment counts locally and each case gets a fixed,
// illustrative decision. The real scoring runs on the data-collection app (#/collect) against the API.
import type { Score, UserStatus } from './api'

export type SimWho = 'you' | 'owner' | 'friend' | 'bot'
const ENROLL = 3

export function simEnroll(st: UserStatus): UserStatus {
  const n = Math.min(st.enrolled_sessions + 1, ENROLL)
  return { ...st, enrolled_sessions: n, template_ready: n >= ENROLL }
}

const CASES: Record<SimWho, Omit<Score, 'session_id' | 'reasons' | 'explanation_vi'> & { reasons: (newTo: boolean) => string[]; vi: string }> = {
  you: { human_score: 0.93, owner_match: 0.86, risk: 'low', risk_score: 0.12, action: 'allow', reasons: () => [], vi: 'Nhịp chạm giống chủ tài khoản. Cho phép chuyển tiền.' },
  owner: { human_score: 0.93, owner_match: 0.86, risk: 'low', risk_score: 0.12, action: 'allow', reasons: () => [], vi: 'Nhịp chạm giống chủ tài khoản. Cho phép chuyển tiền.' },
  friend: { human_score: 0.88, owner_match: 0.18, risk: 'medium', risk_score: 0.47, action: 'step_up',
    reasons: (n) => ['pin_rhythm_slower_35pct', 'tap_offset_down', ...(n ? ['new_recipient'] : [])],
    vi: 'Người thật nhưng nhịp PIN chậm hơn 35% và chạm lệch xuống so với chủ tài khoản. Yêu cầu gõ một câu ngắn trước khi chuyển.' },
  bot: { human_score: 0.06, owner_match: 0.31, risk: 'high', risk_score: 0.91, action: 'hold',
    reasons: (n) => ['timing_too_regular', 'tap_exact_center', 'text_set_without_keys', ...(n ? ['new_recipient'] : [])],
    vi: 'Nhịp gõ đều bất thường, chạm đúng tâm phím và số tài khoản được điền thẳng không qua bàn phím. Tạm giữ lệnh và báo chủ tài khoản.' },
}

export function simScore(who: SimWho, recipientIsNew: boolean): Score {
  const c = CASES[who]
  return { ...c, session_id: `sim_${Math.random().toString(36).slice(2, 10)}`, reasons: c.reasons(recipientIsNew), explanation_vi: c.vi }
}
