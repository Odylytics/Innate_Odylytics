# Transfer flow: account number → bank → PIN

> Research note, 25/11/2026. Demo goal: score not only when the PIN is entered but also when the **account number is entered** and the **bank is chosen**. There is no name-typing step: once the account number and bank are known, the wallet looks up the recipient's name itself.
> There are no measurements in this note. The figures quoted come from other studies or from the experiments E1–E13 in the repo.

## 1. The flow and the attacker

| Step | What the user does | Other ways in (no typing) |
|---|---|---|
| 1. Account number | Types 8–19 digits | Pastes from a message, scans a VietQR, picks a saved recipient |
| 2. Bank | Scrolls a list and taps, or types a few letters to search (`VCB`, `MB`) | Filled in automatically when scanning a VietQR |
| 3. Amount | Types a number | Filled in automatically when scanning a VietQR that has an amount |
| 4. PIN | Types 6 digits on the custom-drawn PIN keypad | None |
| 5. Confirm | Swipes or taps | None |

Three kinds of attacker, each leaving different traces:

| Attacker | Account number | Bank | PIN | Check layer that catches it |
|---|---|---|---|---|
| **A. Accessibility malware** (RedHook, Gigabud targeting Vietnam; see [`notes/bot_detection.md`](notes/bot_detection.md)) | Puts text straight into the field (`ACTION_SET_TEXT`), no keys at all | Clicks the list element with `ACTION_CLICK`, no real touch; or `dispatchGesture` | `dispatchGesture` or element click | Human or machine |
| **B. PIN-knowing impostor** (holding the victim's phone) | Types the account number by hand | Taps by hand | Types by hand | Is it the owner |
| **C. Scammed victim transferring on their own** (fake police, fake bank staff) | Usually **pastes** the number sent by the scammer | Taps by hand | The owner types it | Hardest: right person, right phone |

Type C is outside Innate's main scope ([`../plan/positioning.md`](../plan/positioning.md)): the touch rhythm really is the owner's. Commercial vendors mention signs such as hesitation when entering an unfamiliar recipient, or an ongoing phone call during the transfer, but those are marketing claims not independently verified, and analysts doubt that behavior can stop this kind of scam ([American Banker](https://www.americanbanker.com/payments/news/biometrics-role-in-stopping-peer-to-peer-payment-scams), [BioCatch](https://www.biocatch.com/blog/authorized-push-payment-fraud-how-digital-behavior-can-uncover-social-engineering-scams), [Outseer](https://www.outseer.com/solutions/scam-prevention)). For the demo, "pasted account number + new recipient" should only be used as **context** to suggest extra authentication, not treated as evidence of fraud.

## 2. Signals by step

### Step 1: account number

If the account number is typed on a **custom-drawn numeric keypad** (like the PIN keypad), each entry gives exactly what the PIN gives: key hold, gap between two keys, offset from the key center. The big difference is that the **content changes with every transaction**. The current PIN rhythm template compares by digit position (`pin_hold_0..5`), so it cannot be reused. We need **content-independent** features:

- distribution of key hold time (mean, deviation, quartiles);
- the gap between two keys by the **geometric distance between the two keys** (same key, adjacent, far apart), not by digit pair;
- offset from the center **per key** (key 1 is often tapped off to the left...), pooled when the key appears;
- delete and retype actions.

Advantage: 8–19 keys each time, more than a 6-digit PIN. E13 shows that typing more keys helps recognize the person better (EER 0.364 with 6 keys, 0.245 with 30 keys, on Aalto letters). No study has measured **free digit** typing on phones. One review noted that numeric keypads are studied less than letter keyboards, and a one-time-PIN experiment reached only EER 26% ([Springer, 2018](https://link.springer.com/content/pdf/10.1186/s42400-018-0009-4.pdf)). So expectations should be low.

Human or machine signals:
- `set_text` (text changes with no keys): only the native SDK sees it. This is the clearest malware sign: malware uses Accessibility to set text or click elements in another app ([MITRE ATT&CK T1516](https://attack.mitre.org/techniques/T1516/)); Gustuff set input field values in banking apps this way (per Group-IB, original not read).
- Typing too evenly, exactly at the key center: like bot tactics 1–2 on the PIN.
- Paste: real people paste often too, so it is only context.

**Privacy:** the recipient's account number is personal data. The PIN session currently sends the key label (`key`). For the account number, **the key label must not be sent**, because putting them together gives exactly the account number. Send only time, the normalized offset from the key center, and the gap between two consecutive keys. This must be stated clearly in the consent form.

### Step 2: choosing the bank

This is a tap and scroll step, not typing. Signals:
- **Selection with no real touch** (the native SDK sees the select event but there is no preceding `MotionEvent`): the `ACTION_CLICK` sign of malware. Same type as `set_text`, so use it as a **rule**, no machine learning needed.
- Scroll gesture: speed, curvature, how it stops. Similar to the existing swipe part (`swipe_*`), with the public Touchalytics data (41 people, swipe/scroll).
- Time from opening the list to the selection, number of back-and-forth scrolls.
- Typing in the search box: too short to recognize a person, only used to catch `set_text` or paste.

There is no public dataset for choosing a bank from a list. Person recognition at this step can only be measured with the team's own data.

### Steps 3–5: amount, PIN, confirm

Already in the API: the `set_text` rule on the amount field, the PIN model (human or machine, is it the owner), replay, the confirmation swipe.

## 3. What the API has now, what is missing

| Item | Current state | To do |
|---|---|---|
| Account number field | Temporarily uses `fields[name="recipient"]`: only time, event type, character count; **no touch coordinates** | Add a touch list for the account number field (like `pin_taps` but with no key label), or compute features on the device itself |
| Bank selection | None | Add a selection event: time, whether a real touch came first, the scrolls |
| `set_text` / selection-without-touch rule | Only for the amount field | Extend to the account number and the bank |
| Human or machine model for text fields (E11) | Only in `research/`, not wired into `/score` | Wire it in, then retrain for digits |
| Owner recognition through account number typing rhythm | None | Content-independent features (section 2), run E14 first |

## 4. Proposed experiments

**E14. Owner recognition when typing new digits (doable now, StrokePIN data).** StrokePIN has 20 6-digit PINs shared by 97 people. Enroll on one group of PINs and then test on **unseen PINs**, using content-independent features. This is the closest simulation of typing a new account number. Question: when the content changes, how much owner-account signal remains compared with E12b (FAR 0.316 at FRR 5% on the same PIN)? Limits: 6 digits is shorter than an account number, and the keypad in StrokePIN may differ from the app's keypad.

**E14 result (25/11, [`../../research/results/e14_unseen_digits.md`](../../research/results/e14_unseen_digits.md)).** Enrollment 3 PINs x 3 rounds, 20 content-independent features, no touch size used, the impostor types the same digit string:

| Test | LightGBM: EER | LightGBM: FAR @ FRR 5% |
|---|---|---|
| same digit string as enrolled | 0.245 | 0.500 |
| new digit string, 6 digits | 0.328 | 0.697 |
| new digit string, 12 digits | 0.284 | 0.607 |

- With a new digit string the signal clearly weakens: at the level where the owner is bothered only 5% of the time, **~70% of impostors still get through** with 6 digits, **~61%** with 12 digits. Longer typing helps, in line with E13.
- LightGBM is better than simple distance on every row; simple distance is nearly useless at FRR 5% (FAR ~0.92).
- **Conclusion:** account number typing rhythm is **not enough to stand alone**. It should only be additional evidence on top of the PIN score, and only means something when the account number is long enough. The next thing to measure: does combining the PIN score (E12b) with the account number score reduce FAR.
- Limits: StrokePIN has no real account numbers; 12 digits is 2 separate typing rounds put together, not one continuous entry; one phone per person.

**E15. Bots typing the account number.** Add tactics to the simulator (`attacker/`): `set_text` of the account number, paste, even typing at exactly the key center, sampling from the human distribution. Measure the rules and the model across the whole account number → bank → PIN flow. The bot is still a fake bot, used only to test the data path.

**E16. Choosing the bank (needs the team's data).** Once the phone app has a bank selection screen: collect real sessions with consent, and run real `ACTION_CLICK` / `dispatchGesture` bots on an Android phone. Measure the "selection without touch" rule and scroll features.

Order: E14 first (needs no app, answers the question "does typing the account number help recognize the owner"), then change the schema + E15, and finally E16 once the app exists.

## 5. Vietnam context and arguments for Innate

> Looked up 25/11/2026. Most sources are news and blogs, not the original texts of banks or the State Bank of Vietnam (NHNN); the sources disagree in a few places (noted below). Check the original sources before putting figures on slides.

### 5.1. How long account numbers are

| Bank | Number of digits (per the sources found) |
|---|---|
| ACB | 8 (one source says 8–9) |
| VPBank | 8–9 |
| VIB | 9 (previously 15) |
| TPBank | 11 |
| VietinBank | 12 |
| Sacombank | 12 |
| Vietcombank | 13 |
| Agribank | 13 |
| MB | 13 (one source says 10–13) |
| BIDV | 14 |
| Techcombank | 14 |
| Card number (transfer via Napas by card number) | 16–19 |

Sources: [Timo](https://timo.vn/blogs/so-tai-khoan-ngan-hang-la-gi-nhung-dieu-ban-can-biet-ve-so-tai-khoan-ngan-hang/), [QuanTriMang](https://quantrimang.com/cong-nghe/so-tai-khoan-ngan-hang-ghi-o-dau-co-bao-nhieu-so-152869), [TheBank](https://m.thebank.vn/blog/16614-tong-hop-dau-so-tai-khoan-cua-cac-ngan-hang-vietcombank-agribank-bidv-hien-nay.html), [VietnamBiz](https://vietnambiz.vn/cap-nhat-danh-sach-dau-so-tai-khoan-cac-ngan-hang-moi-nhat--2022530154256452.htm), [Chanhtuoi](https://chanhtuoi.com/dau-so-tai-khoan-cac-ngan-hang-p8902.html). In addition, many banks let customers choose a "vanity number" or use a phone number as the account number; the length is then different from the table above. For this part we **did not find a confirming source**.

**Meaning:** the largest banks (Vietcombank, BIDV, VietinBank, Agribank, Techcombank, MB) use **12–14 digits**. By E14, 12 unseen digits give EER 0.28 and FAR 0.61 (FRR 5%), compared with 0.33 / 0.70 for only 6 digits. That means for most recipients at these banks, the account number step **adds roughly twice as many keys** as the PIN, which is the range where the signal starts to be useful. For ACB and VPBank (8–9 digits) the benefit is smaller.

### 5.2. How transfers happen

- **Napas 247**: fast interbank transfer by account number or card number; the wallet looks up the recipient's name itself once it has the account number and bank. In 2025 the Napas system processed on average over 32 million transactions a day ([VNBA](https://vnba.org.vn/vi/napas-to-chuc-hoi-nghi-thuong-nien-thanh-vien-nam-2025-19723.htm)).
- **VietQR takes nearly half**: in early 11/2025 about 15 million VietQR transactions a day out of about 35 million in total ([VnEconomy](https://vneconomy.vn/tu-chuyen-khoan-ca-nhan-den-thanh-toan-thuong-mai-chuan-quoc-gia.htm)); in the first 10 months of 2025 about 3.6 billion VietQR transactions, up more than 52% ([Diễn đàn Doanh nghiệp](https://diendandoanhnghiep.vn/print/10165115.html)).
- **Biometrics under Decision 2345/QĐ-NHNN** (effective 01/7/2024): face authentication when transferring **from 10 million VND** in one go (sources disagree on "from" or "over") or when the daily total **exceeds 20 million**; below that only PIN/OTP is needed ([LuatVietnam](https://luatvietnam.vn/tin-van-ban-moi/tu-2024-chuyen-khoan-tren-10-trieu-dong-phai-xac-thuc-sinh-trac-hoc-186-96491-article.html), [Thị trường Tài chính Tiền tệ](https://thitruongtaichinhtiente.vn/phan-loai-giao-dich-ngan-hang-phai-xac-thuc-sinh-trac-hoc-theo-quyet-dinh-2345-qd-nhnn-58169.html)). The original text and amendments after 2024 were not checked.
- **NHNN's SIMO**: when transferring, the app checks the **recipient account** against a list of suspected fraud and warns. By 28/9/2026 more than 5.6 million warnings, more than 1.9 million transactions stopped or canceled ([CafeF](https://cafef.vn/hon-19-trieu-luot-khach-hang-dung-giao-dich-sau-canh-bao-gian-lan-18826100811053583.chn)). Legal framework: Circular 50/2024 and 77/2025/TT-NHNN (per the press, original text not read).

### 5.3. Supporting arguments

1. **Innate stands exactly in the gap in the regulation.** Below 10 million per transfer and 20 million per day, a transaction needs only PIN/OTP, exactly the two things that malware and shoulder surfers can obtain. Innate adds scoring on these very transactions without making the user do anything extra. Above the threshold, the face proves the owner is present **at authentication time**, but remote-controlled malware still performs the earlier steps (entering the account number, choosing the bank), and banks have noted criminals using deepfakes to get past biometrics ([Tạp chí Kinh tế Tài chính](https://tapchikinhtetaichinh.vn/dam-bao-an-ninh-tai-chinh-ca-nhan-truoc-lan-song-lua-dao-cong-nghe-cao-138286.html)). Innate does not replace the face; it scores the steps the face does not see.
2. **The three layers complement each other and do not overlap.** SIMO asks "**is the receiving account** suspicious", biometrics asks "**is the owner** present at authentication", Innate asks "**who or what** is touching the screen throughout the transfer flow". A newly opened receiving account (not yet on the SIMO list) or malware transferring below the threshold is where Innate has its own value.
3. **Adding friction in the right place reduces fraud.** VPBank reported that after applying biometrics on transfers, the number of personal accounts defrauded fell by about 59% and the amount defrauded fell by 52% (per the press, figures published by the bank itself) ([Tạp chí Kinh tế Tài chính](https://tapchikinhtetaichinh.vn/dam-bao-an-ninh-tai-chinh-ca-nhan-truoc-lan-song-lua-dao-cong-nghe-cao-138286.html)). Innate proposes friction (`step_up`) **only when behavior is abnormal**, instead of for every transaction.
4. **Long account numbers are an advantage in Vietnam.** Large banks use 12–14 digits; E14 shows 12 digits are clearly better than 6. Combining the 6-digit PIN + a 12–14 digit account number gives about 18–20 keys per transaction. Combining these two scores has not been measured directly (next work).
5. **Scale of the threat.** Online fraud losses in 2025 are estimated at over 6,000 billion VND according to the National Cybersecurity Association, with another source reporting over 8,000 billion ([SGGP](https://www.sggp.org.vn/nam-2025-thiet-hai-do-lua-dao-truc-tuyen-o-viet-nam-uoc-tinh-tren-6000-ty-dong-post832336.html), [Báo Pháp luật](https://doanhnhan.baophapluat.vn/hon-8-000-ty-dong-boc-hoi-vi-lua-dao-truc-tuyen-bo-cong-an-canh-bao-thu-doan-dau-hieu-nhan-biet-va-cach-phong-tranh-9b93d880.html)); NCA recorded 62,952 new mobile malware samples in Vietnam in 2025 (per the articles above). The two figures disagree; only use the one with the clearest origin.

**Weak points that must be stated plainly:**
- **Nearly half of transactions are VietQR**, with no account number typing. For these transactions Innate only has the PIN and the confirmation action. A missing typing step must be treated as neutral, not suspicious.
- **The most common scam in 2025 is impersonating the police** (per the articles above): the victim transfers on their own, right person on the right phone. Innate cannot catch this by behavior; that is the job of SIMO and content warnings.

## 6. Suggested demo script

1. Wallet owner transfers: types the account number, chooses the bank, types the PIN → `allow`.
2. Malware: the account number is set directly, the bank is selected with no touch, the PIN is tapped evenly → `hold`, with Vietnamese reasons for each step.
3. PIN-knowing impostor: types every step by hand → the account number and PIN typing rhythm do not match the owner → `step_up`.
4. (Optional) Scammed victim: pastes an unfamiliar account number, new recipient, large amount → `step_up` because of context, with a warning. State clearly on stage that this is context, not recognizing the scammer.

Steps 2 and 3 of the script need a **native app**: the web cannot see `set_text` and selection without touch.
