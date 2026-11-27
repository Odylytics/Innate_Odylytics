// Fictional cast and two stories (remote hijack, stolen phone). Every name and company here is invented for the demo.
// The owner, bot and friend steps replay seeded synthetic sessions (synth.ts) with fixed, illustrative decisions (demoSim.ts): no API calls.
type L = { en: string; vi: string }

export type PersonaId = 'vy' | 'ha' | 'bao' | 'khoa' | 'lananh' | 'an'

export interface Persona { id: PersonaId; name: string; initials: string; tone: 'navy' | 'blue' | 'ice'; role: L; org: L; does: L }

const WALLET: L = { en: 'Demo Wallet (fictional)', vi: 'Ví Demo (giả tưởng)' }

export const PERSONAS: Persona[] = [
  {
    id: 'ha', name: 'Trần Thu Hà', initials: 'TH', tone: 'navy',
    role: { en: 'Wallet owner', vi: 'Chủ ví' }, org: { en: 'Office worker, HCMC', vi: 'Nhân viên văn phòng, TP.HCM' },
    does: { en: 'Pays rent and sends money home with her e-wallet. Types her PIN the same way every day without thinking.', vi: 'Trả tiền nhà, gửi tiền về cho mẹ bằng ví điện tử. Ngày nào cũng gõ PIN theo một nhịp mà không để ý.' },
  },
  {
    id: 'bao', name: 'Phạm Quốc Bảo', initials: 'QB', tone: 'blue',
    role: { en: 'Colleague who saw her PIN', vi: 'Đồng nghiệp từng nhìn lén PIN' }, org: { en: 'Same office', vi: 'Cùng văn phòng' },
    does: { en: 'Watched Hà type 159357 at lunch. Picks up her phone while she is away from her desk.', vi: 'Nhìn thấy Hà gõ 159357 lúc ăn trưa. Cầm điện thoại của Hà khi Hà rời bàn.' },
  },
  {
    id: 'an', name: 'Đỗ Gia An', initials: 'GA', tone: 'ice',
    role: { en: 'Scammer running the malware', vi: 'Kẻ gian điều khiển mã độc' }, org: { en: 'Fake “police officer” on the phone', vi: '“Cán bộ công an” giả qua điện thoại' },
    does: { en: 'Talks Hà into installing a fake app that asks for Accessibility, then taps her PIN remotely at 2 a.m.', vi: 'Dụ Hà cài ứng dụng giả xin quyền Trợ năng, rồi bấm PIN của Hà từ xa lúc 2 giờ sáng.' },
  },
  {
    id: 'vy', name: 'Hoàng Bảo Vy', initials: 'BV', tone: 'ice',
    role: { en: 'Mobile engineer', vi: 'Kỹ sư mobile' }, org: WALLET,
    does: { en: 'Adds the Innate SDK to the wallet’s PIN pad and calls the score API at the confirm step.', vi: 'Gắn SDK Innate vào bàn phím PIN của ví và gọi API chấm điểm ở bước xác nhận.' },
  },
  {
    id: 'khoa', name: 'Lê Minh Khoa', initials: 'MK', tone: 'blue',
    role: { en: 'Fraud operations analyst', vi: 'Chuyên viên vận hành chống gian lận' }, org: WALLET,
    does: { en: 'Reviews flagged transfers with their reasons and marks each one fraud or legitimate.', vi: 'Xem các giao dịch bị gắn cờ kèm lý do, đánh dấu gian lận hay hợp lệ.' },
  },
  {
    id: 'lananh', name: 'Nguyễn Lan Anh', initials: 'LA', tone: 'navy',
    role: { en: 'Head of risk', vi: 'Trưởng bộ phận rủi ro' }, org: WALLET,
    does: { en: 'Sets the thresholds: ask before blocking, and never lock an account automatically.', vi: 'Đặt ngưỡng: xác thực thêm trước khi chặn, không bao giờ tự khoá tài khoản.' },
  },
]

export const persona = (id: PersonaId) => PERSONAS.find((p) => p.id === id)!

export type Cue = 'rates' | 'channels' | 'scan' | 'extract' | 'reconcile' | 'focus' | 'duplicate' | 'send' | 'done'
/** what the workspace does on this step */
export type Act = 'sdk' | 'enroll' | 'owner' | 'malware-setup' | 'bot' | 'steal' | 'friend' | 'ops' | 'policy'
/** the two stories: Android hijacked remotely (malware) / phone stolen (someone who knows the PIN) */
export type StoryCase = 'remote' | 'stolen'

/** who speaks; also lists the cast members the step mentions, so they light up too; id picks the behind-the-scenes vignette */
export interface StoryStep { id: string; who: PersonaId; also: PersonaId[]; title: L; body: L; cue: Cue; act: Act; seconds: number }

const SDK: StoryStep = {
  id: 'sdk', who: 'vy', also: [], cue: 'channels', act: 'sdk', seconds: 12,
  title: { en: 'Vy adds Innate to the PIN pad', vi: 'Vy gắn Innate vào bàn phím PIN' },
  body: {
    en: 'The SDK records when each key goes down and up, where the finger lands on the key, touch size and swipes. It sends the session to the score API when the transfer is confirmed; the wallet keeps its own PIN check.',
    vi: 'SDK ghi lúc mỗi phím được nhấn và nhả, ngón tay chạm lệch đâu trên phím, kích thước vùng chạm và các lần vuốt. Khi xác nhận chuyển tiền, SDK gửi phiên lên API chấm điểm; ví vẫn tự kiểm tra PIN như cũ.',
  },
}
const ENROLL: StoryStep = {
  id: 'enroll', who: 'ha', also: [], cue: 'extract', act: 'enroll', seconds: 13,
  title: { en: 'Hà enrolls her rhythm in three entries', vi: 'Hà đăng ký nhịp bằng ba lần nhập' },
  body: {
    en: 'Hà types her PIN three times. Innate learns her hold times, the gaps between keys and that she taps a little right of centre. After the third entry enrollment locks, so nobody can add their own rhythm later.',
    vi: 'Hà gõ PIN ba lần. Innate học thời gian giữ phím, khoảng nghỉ giữa các phím và thói quen chạm hơi lệch phải. Sau lần thứ ba, việc đăng ký khoá lại để không ai chèn nhịp của mình vào sau.',
  },
}
const OWNER: StoryStep = {
  id: 'owner', who: 'ha', also: [], cue: 'reconcile', act: 'owner', seconds: 11,
  title: { en: 'Hà sends 500,000 to her mum', vi: 'Hà chuyển 500.000 cho mẹ' },
  body: {
    en: 'Hà unlocks the wallet with her PIN; Innate only records it, it never blocks there. At the transfer confirmation it scores everything together: a known recipient, a usual amount and her own rhythm. The transfer goes through with no extra step.',
    vi: 'Hà mở ví bằng PIN; Innate chỉ ghi lại, không chặn ở bước này. Khi xác nhận chuyển tiền, Innate chấm điểm tất cả cùng lúc: người nhận quen, số tiền bình thường và đúng nhịp của Hà. Giao dịch được qua, không thêm bước nào.',
  },
}

const OPS_REMOTE: StoryStep = {
  id: 'ops', who: 'khoa', also: ['ha'], cue: 'send', act: 'ops', seconds: 11,
  title: { en: 'Khoa reviews the held transfer', vi: 'Khoa xem lệnh bị tạm hoãn' },
  body: {
    en: 'The held session reaches the ops dashboard with plain-language reasons. Khoa confirms with Hà and marks it as fraud; the label becomes training data for the next model.',
    vi: 'Phiên bị tạm hoãn hiện trên bảng vận hành kèm lý do dễ hiểu. Khoa xác nhận với Hà và đánh dấu là gian lận; nhãn trở thành dữ liệu huấn luyện cho mô hình sau.',
  },
}
const OPS_STOLEN: StoryStep = {
  id: 'ops', who: 'khoa', also: ['ha'], cue: 'send', act: 'ops', seconds: 11,
  title: { en: 'Khoa reviews the flagged transfer', vi: 'Khoa xem giao dịch bị gắn cờ' },
  body: {
    en: 'The flagged session reaches the ops dashboard with plain-language reasons. Khoa checks with Hà that she did not send it and marks it as fraud; the label becomes training data for the next model.',
    vi: 'Phiên bị gắn cờ hiện trên bảng vận hành kèm lý do dễ hiểu. Khoa hỏi Hà xác nhận cô không chuyển khoản này rồi đánh dấu là gian lận; nhãn trở thành dữ liệu huấn luyện cho mô hình sau.',
  },
}

export const STORIES: Record<StoryCase, { title: L; steps: StoryStep[] }> = {
  remote: {
    title: { en: 'Case 1 · Android hijacked remotely', vi: 'Trường hợp 1 · Android bị chiếm từ xa' },
    steps: [
      SDK, ENROLL, OWNER,
      {
        id: 'officer', who: 'an', also: ['ha'], cue: 'scan', act: 'malware-setup', seconds: 11,
        title: { en: 'A fake officer calls Hà', vi: 'Một “cán bộ” giả gọi cho Hà' },
        body: {
          en: 'An says Hà’s ID must be updated and sends a link to a fake government app. It asks for Accessibility permission, which lets it read the screen and tap anywhere. PIN and OTP no longer protect her.',
          vi: 'An nói căn cước của Hà cần cập nhật và gửi link ứng dụng dịch vụ công giả. Ứng dụng xin quyền Trợ năng, quyền cho phép đọc màn hình và bấm ở bất kỳ đâu. Từ đây PIN và OTP không còn bảo vệ được Hà.',
        },
      },
      {
        id: 'bot', who: 'an', also: ['ha'], cue: 'duplicate', act: 'bot', seconds: 12,
        title: { en: '2 a.m.: the malware unlocks and pays', vi: '2 giờ sáng: mã độc mở ví và chuyển tiền' },
        body: {
          en: 'The malware taps 159357 to unlock, fills a new account straight into the field and sends 20,000,000. The PIN is right, but every tap lands on the exact centre of the key at a machine-steady rhythm, and the field was filled without a key press. Innate holds the transfer and the owner is told.',
          vi: 'Mã độc bấm 159357 để mở ví, điền thẳng tài khoản lạ vào ô nhập và chuyển 20.000.000. PIN đúng, nhưng mọi cú chạm rơi đúng tâm phím với nhịp đều như máy, và ô nhập được điền mà không có phím nào. Innate tạm hoãn lệnh và báo cho chủ ví.',
        },
      },
      OPS_REMOTE,
      {
        id: 'policy', who: 'lananh', also: ['ha'], cue: 'done', act: 'policy', seconds: 12,
        title: { en: 'Lan Anh: hold what looks like a machine', vi: 'Lan Anh: tạm hoãn khi giống máy' },
        body: {
          en: 'Innate only recommends. Input that looks like a machine is held and the owner is told; Hà’s account is never locked by an algorithm. Thresholds stay with the risk team.',
          vi: 'Innate chỉ đề xuất. Thao tác giống máy thì tạm hoãn và báo chủ ví; tài khoản của Hà không bao giờ bị thuật toán khoá. Ngưỡng do bộ phận rủi ro quyết định.',
        },
      },
    ],
  },
  stolen: {
    title: { en: 'Case 2 · Phone stolen', vi: 'Trường hợp 2 · Bị trộm điện thoại' },
    steps: [
      SDK, ENROLL, OWNER,
      {
        id: 'steal', who: 'bao', also: ['ha'], cue: 'scan', act: 'steal', seconds: 11,
        title: { en: 'Bảo picks up Hà’s phone', vi: 'Bảo cầm điện thoại của Hà' },
        body: {
          en: 'Bảo watched Hà type 159357 at lunch. While she is away from her desk he picks up her phone and unlocks it. The PIN is right, so nothing stops him here: Innate only records how he types and decides at the transfer.',
          vi: 'Bảo đã nhìn thấy Hà gõ 159357 lúc ăn trưa. Khi Hà rời bàn, Bảo cầm điện thoại và mở khoá. PIN đúng nên chưa gì chặn được Bảo ở đây: Innate chỉ ghi cách Bảo gõ và quyết định ở bước chuyển tiền.',
        },
      },
      {
        id: 'friend', who: 'bao', also: ['ha'], cue: 'focus', act: 'friend', seconds: 12,
        title: { en: 'Bảo sends 2,000,000 to his own account', vi: 'Bảo chuyển 2.000.000 vào tài khoản của mình' },
        body: {
          en: 'Bảo is human, so the bot check passes. But his rhythm is not Hà’s: slower keys, taps left and low. Instead of sending the money, Innate asks him to type a short sentence (then a face or OTP check if it is still unsure).',
          vi: 'Bảo là người thật nên vượt qua kiểm tra người hay máy. Nhưng nhịp của Bảo không phải của Hà: bấm chậm hơn, chạm lệch trái và xuống dưới. Thay vì chuyển tiền, Innate yêu cầu Bảo gõ một câu ngắn (vẫn chưa chắc thì mới đến khuôn mặt hoặc OTP).',
        },
      },
      OPS_STOLEN,
      {
        id: 'policy', who: 'lananh', also: ['ha'], cue: 'done', act: 'policy', seconds: 12,
        title: { en: 'Lan Anh: ask before blocking', vi: 'Lan Anh: hỏi trước khi chặn' },
        body: {
          en: 'Innate only recommends. A human who is not the owner is asked to type a sentence, not blocked: it is a risk signal, not a gate. Hà’s account is never locked by an algorithm, and thresholds stay with the risk team.',
          vi: 'Innate chỉ đề xuất. Người thật nhưng không phải chủ thì được yêu cầu gõ một câu, không bị chặn: đây là tín hiệu rủi ro, không phải cổng. Tài khoản của Hà không bao giờ bị thuật toán khoá, ngưỡng do bộ phận rủi ro quyết định.',
        },
      },
    ],
  },
}

export const stepsOf = (c: StoryCase) => STORIES[c].steps
/** the cast members that appear in a story */
export const castOf = (c: StoryCase) => PERSONAS.filter((p) => stepsOf(c).some((s) => s.who === p.id || s.also.includes(p.id)))
