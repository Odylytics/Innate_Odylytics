// Client for the Innate scoring API (backend/). The SDK key is meant to ship in the app: it can only create
// sessions, enroll and score. Dashboard (ops) and export (ML) keys are never bundled; the operator types the ops key.
export const API_URL = (import.meta.env.VITE_API_URL ?? 'https://nhip-api-taupe.vercel.app').replace(/\/$/, '')
const SDK_KEY: string = import.meta.env.VITE_SDK_KEY ?? ''

export interface Tap {
  key: string; t_down: number; t_up: number; x: number; y: number; w: number; h: number
  key_cx: number; key_cy: number; key_w: number; key_h: number
}
export interface Swipe { points: { t: number; x: number; y: number }[] }
export interface ScreenVisit { name: string; t_enter: number; t_first_touch: number | null }
// A field typed outside the PIN pad. Only time, kind and character count: never the digits themselves.
export interface FieldEvent { t: number; kind: 'key' | 'paste' | 'delete' | 'set_text'; n?: number; cls?: 'digit' | 'letter' | 'space' | 'symbol' }
// `challenge` = the random Vietnamese phrase from GET /v1/challenge: the server knows the phrase from the signed token, so only times, kinds and lengths are sent.
// A key event with n = 0 is an IME mark/tone key (Telex/VNI) that changed the text without adding a character.
export interface TextField { name: 'recipient' | 'amount' | 'challenge'; events: FieldEvent[]; token?: string; expected_len?: number }
export interface Challenge { token: string; phrase: string; expected_len: number; ttl_s: number }
// Collection label (backend CollectionMeta): who really held the phone, which sitting, genuine owner or someone who saw the PIN.
export type Posture = 'sit' | 'stand' | 'walk'
export interface CollectionMeta { participant_id: string; sitting: number; role: 'genuine' | 'impostor' | 'bot'; posture?: Posture; note?: string; full_name?: string; email?: string }
export interface SessionIn { user_id: string; device_id: string; pin_taps: Tap[]; swipes: Swipe[]; screens: ScreenVisit[]; fields?: TextField[]; meta?: CollectionMeta }

export type Action = 'allow' | 'step_up' | 'hold'
export interface Score {
  session_id: string; human_score: number; owner_match: number | null; risk: 'low' | 'medium' | 'high'
  risk_score: number; action: Action; reasons: string[]; explanation_vi: string
}
export interface AccountStatus extends UserStatus { email: string; full_name?: string | null }
export interface UserStatus { user_id: string; enrolled_sessions: number; template_ready: boolean; template_updates?: number; enroll_open?: boolean; consistency?: number | null }
export interface Flagged {
  session_id: string; user_id: string; created_at: string; action: Action | null; risk_score: number | null
  reasons: string[]; explanation_vi: string | null; label: string | null
}

export class ApiError extends Error {
  constructor(public status: number, message: string) { super(message) }
}

async function call<T>(path: string, { method = 'GET', body, key = SDK_KEY }: { method?: string; body?: unknown; key?: string } = {}): Promise<T> {
  let res: Response
  try {
    res = await fetch(`${API_URL}${path}`, {
      method,
      headers: { 'X-API-Key': key, ...(body ? { 'Content-Type': 'application/json' } : {}) },
      body: body ? JSON.stringify(body) : undefined,
    })
  } catch {
    throw new ApiError(0, 'network')
  }
  if (!res.ok) {
    let detail = res.statusText
    try { const j = await res.json(); detail = typeof j.detail === 'string' ? j.detail : JSON.stringify(j.detail) } catch { /* not JSON */ }
    throw new ApiError(res.status, detail)
  }
  return res.json() as Promise<T>
}

export const api = {
  hasSdkKey: () => SDK_KEY.length > 0,
  registerParticipant: (p: { participant_id: string; email: string; full_name: string }) =>
    call<{ participant_id: string }>('/v1/participants', { method: 'POST', body: p }),
  challenge: () => call<Challenge>('/v1/challenge'),
  createSession: (s: SessionIn) => call<{ session_id: string; n_features: number }>('/v1/sessions', { method: 'POST', body: s }),
  enroll: (userId: string, sessionId: string, keepOpen = false) =>
    call<UserStatus>(`/v1/users/${encodeURIComponent(userId)}/enroll`, { method: 'POST', body: { session_id: sessionId, keep_open: keepOpen } }),
  signup: (b: { email: string; password: string; full_name?: string }) =>
    call<AccountStatus>('/v1/accounts/signup', { method: 'POST', body: b }),
  login: (b: { email: string; password: string }) =>
    call<AccountStatus>('/v1/accounts/login', { method: 'POST', body: b }),
  finishEnroll: (userId: string) =>
    call<UserStatus>(`/v1/users/${encodeURIComponent(userId)}/enroll/finish`, { method: 'POST' }),
  user: (userId: string) => call<UserStatus>(`/v1/users/${encodeURIComponent(userId)}`),
  score: (sessionId: string, ctx: { recipient_is_new: boolean; amount: number }) =>
    call<Score>(`/v1/sessions/${sessionId}/score`, { method: 'POST', body: ctx }),
  flagged: (opsKey: string, flagged = true, limit = 100) =>
    call<Flagged[]>(`/v1/sessions?flagged=${flagged}&limit=${limit}`, { key: opsKey }),
  label: (opsKey: string, sessionId: string, label: 'fraud' | 'legit') =>
    call<{ session_id: string; label: string }>(`/v1/sessions/${sessionId}/label`, { method: 'POST', body: { label }, key: opsKey }),
}

/** The API explains in Vietnamese only (explanation_vi); in English the sentence is rebuilt from the reason codes. */
export function explanationText(s: { reasons: string[]; action: Action | null; explanation_vi: string | null }, lang: 'en' | 'vi'): string {
  if (lang === 'vi') return s.explanation_vi ?? ''
  const why = s.reasons.map((r) => reasonText(r, 'en')).join('; ')
  const act = s.action === 'allow' ? 'Allow the transfer.' : s.action === 'step_up' ? 'Ask for a short typed sentence before sending.' : s.action === 'hold' ? 'Hold the transfer and tell the owner.' : ''
  return `${why ? `${why}. ` : ''}${act}`
}

/** Vietnamese/English text for each reason code the API returns (backend/app/scoring/explain.py). */
export function reasonText(code: string, lang: 'en' | 'vi'): string {
  const pct = code.match(/_(\d+)pct$/)?.[1]
  const table: [RegExp, string, string][] = [
    [/^pin_rhythm_slower/, `PIN rhythm ${pct}% slower`, `Nhịp PIN chậm hơn ${pct}%`],
    [/^pin_rhythm_faster/, `PIN rhythm ${pct}% faster`, `Nhịp PIN nhanh hơn ${pct}%`],
    [/^tap_offset_right$/, 'Taps land further right', 'Chạm lệch phải'],
    [/^tap_offset_left$/, 'Taps land further left', 'Chạm lệch trái'],
    [/^tap_offset_down$/, 'Taps land lower', 'Chạm lệch xuống dưới'],
    [/^tap_offset_up$/, 'Taps land higher', 'Chạm lệch lên trên'],
    [/^swipe_faster/, `Swipes ${pct}% faster`, `Vuốt nhanh hơn ${pct}%`],
    [/^swipe_slower/, `Swipes ${pct}% slower`, `Vuốt chậm hơn ${pct}%`],
    [/^swipe_straighter$/, 'Swipes straighter', 'Vuốt thẳng hơn'],
    [/^swipe_curvier$/, 'Swipes curvier', 'Vuốt cong hơn'],
    [/^timing_too_regular$/, 'Machine-regular timing', 'Nhịp bấm đều bất thường'],
    [/^tap_exact_center$/, 'Taps hit the exact key centre', 'Chạm đúng tâm nút'],
    [/^swipe_perfectly_straight$/, 'Perfectly straight swipe', 'Vuốt thẳng tuyệt đối'],
    [/^swipe_uniform_speed$/, 'Swipe at machine-uniform speed', 'Vận tốc vuốt đều bất thường'],
    [/^challenge_no_ime$/, 'Vietnamese phrase typed without any accent keys', 'Câu có dấu nhưng không có thao tác gõ dấu tiếng Việt'],
    [/^challenge_token_replayed$/, 'Challenge phrase already used, expired or invalid', 'Câu thử thách đã dùng, hết hạn hoặc không hợp lệ'],
    [/^challenge_pasted$/, 'Challenge phrase pasted instead of typed', 'Câu thử thách được dán thay vì gõ'],
    [/^text_set_without_keys$/, 'Field filled without any key press', 'Ô nhập được điền thẳng, không có phím nào'],
    [/^replayed_session$/, 'Copy of an earlier session', 'Lặp lại y hệt một phiên trước'],
    [/^ml_bot_pattern$/, 'AI model: machine-like pattern', 'Mô hình AI: dấu hiệu máy'],
    [/^not_enrolled$/, 'Rhythm not enrolled yet', 'Chưa đăng ký nhịp'],
    [/^missing_pin_evidence$/, 'No full PIN entry to compare', 'Thiếu thao tác nhập PIN để đối chiếu'],
    [/^new_recipient$/, 'New recipient', 'Người nhận mới'],
    [/^amount_unusual$/, 'Unusually large amount', 'Số tiền lớn bất thường'],
    [/^insufficient_data$/, 'Not enough touch data', 'Chưa đủ dữ liệu chạm'],
  ]
  const hit = table.find(([re]) => re.test(code))
  return hit ? (lang === 'en' ? hit[1] : hit[2]) : code
}
