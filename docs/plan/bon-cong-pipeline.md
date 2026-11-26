# Innate với 4 kênh bằng chứng: chuyển động, PIN, câu gõ, vùng chạm/vuốt

> 25/11/2026. Trả lời ý "tổng hợp 4 cổng thì AI có bắt được bot không". Số liệu: [`../research/ai-research.md`](../research/ai-research.md) (E19, E22, E23).
> **26/11/2026: thêm mục 7 "Flow mới" ở cuối file** (hai tầng: người/máy rồi người/người; 4 kịch bản iPhone/Android × chiếm từ xa/trộm máy; nghiêng máy khi bấm; PIN nhập trước, chấm điểm ở bước chuyển tiền). Mục 7 là **thiết kế, chưa cài và chưa đo**; các mục 1–6 là bản 25/11.

## Trả lời ngắn
**Có, nên làm, nhưng là hợp nhất 4 kênh bằng chứng, không phải 4 cổng nối tiếp phải qua hết.** Nếu mỗi cổng chặn nhầm chủ 5% mà bắt buộc qua cả 4, chủ bị chặn nhầm ~18,5% (1 − 0,95⁴). Cách đúng: cả 4 kênh cho điểm vào `fusion.py`; chỉ khi chưa chắc mới yêu cầu gõ câu (kênh 3); kết quả vẫn là `allow | step_up | hold`.

```
Chạy ngầm:   (1) chuyển động  +  (2) nhập PIN  +  (4) chạm/vuốt   ->  hợp nhất rủi ro
                                          chắc chắn là chủ/người ──► allow
                                          rõ ràng là máy ─────────► hold
                                          chưa chắc ─► (3) gõ câu ─► hợp nhất lại ─► allow | step_up | hold
```
Điểm mạnh của ý tưởng: kẻ tấn công phải giả **đồng thời** chạm, rung lắc, nhịp PIN, nhịp gõ, kiểu gõ dấu và các tín hiệu đó phải **khớp thời điểm với nhau**. Mỗi kênh riêng lẻ giả được (bài báo ActReal giả cả cảm biến chuyển động); khớp chéo giữa các kênh khó hơn. Chưa có thí nghiệm nào của đội đo sự khó đó.

## Từng kênh: đã có gì, bằng chứng, hạn chế
| Kênh | Dùng để | Bằng chứng của đội | Hạn chế nói thẳng |
|---|---|---|---|
| **1. Chuyển động** (gia tốc, con quay, trọng lực) | Bot: máy nằm yên trên bàn, không có tay cầm; nhận chủ: cách cầm | **E23 (StrokePIN):** chỉ chuyển động cho EER 0,04–0,07 và FAR 3–10% khi cùng tư thế (PIN thời gian + lệch tâm: EER 0,17–0,20, FAR 69–75%). **Đổi tư thế (ngồi → đi): EER 0,44–0,48, ngang đoán mò.** | **Số E23 lạc quan do thiết bị:** mỗi người một điện thoại, cảm biến lệch khác nhau, nên một phần là nhận máy chứ không nhận người. Kẻ cầm chính điện thoại của nạn nhân sẽ không bị bắt như vậy. StrokePIN chỉ lấy gia tốc/con quay ~5 Hz nên **không đo được cú giật khi chạm**. Tài liệu: HMOG 25,7–34,2% (chỉ chạm) → 7–10% (thêm chuyển động); BeCAPTCHA ~60% → 80–90%; **ActReal: tác tử cấp hệ thống giả được cả cảm biến, thành công 71,1% trước bộ dò chạm + chuyển động.** Web: `DeviceMotion` cần HTTPS và hỏi quyền trên iOS Safari, tối đa ~60 Hz. |
| **2. Nhập PIN** | Nhận chủ, người/máy, phát lại | Đã có: EER 0,16, FAR 37,5% (học máy), bot ngây thơ 100%, phát lại ≤ ±10% 100% | Đổi tư thế mất tín hiệu; kẻ biết PIN lọt nhiều. |
| **3. Gõ câu** | Thêm tín hiệu khi chưa chắc; kiểu gõ dấu tiếng Việt | **E22:** FAR 43–52% ở 30 phím (mô hình học 43%); bot gõ đều AUC 0,996 | Kiểu gõ tiếng Việt chưa đo trên người thật (chờ thử trên điện thoại). |
| **4. Vùng chạm / vuốt** | Bot (vuốt vận tốc đều) | **E19:** luật vận tốc đều bắt 100% bot vuốt đều, 0/20.896 nét người thật bị chặn nhầm | Vuốt **không** nhận chủ được (AUC ~0,5); kích thước vùng chạm là nhiễu thiết bị (E12b). Kênh 4 là cổng chống bot, không phải cổng nhận chủ. |

## Câu "tôi tên là nguyễn minh quân" hay câu ngẫu nhiên?
| | Câu cố định của người dùng | Câu ngẫu nhiên do máy chủ cấp (đang làm) |
|---|---|---|
| Ưu | Đăng ký và thử cùng câu: so cùng nội dung, tín hiệu tốt hơn; nhiều dấu (ô, ê, ễ, â) cho kênh kiểu gõ tiếng Việt | Chống phát lại **nội dung**; máy chủ biết câu mà không lưu nội dung; không phải dữ liệu cá nhân |
| Nhược | **Là tên người dùng: dữ liệu cá nhân**; kẻ nhìn trộm biết câu; kẻ ghi lại nhịp gõ phát lại nguyên văn; máy chủ không biết câu để kiểm "gõ đúng" (chỉ so băm có muối) | Câu đổi mỗi lần nên nhịp theo cặp phím khó so (E21b) |
Gợi ý: giữ câu ngẫu nhiên làm cổng chống bot/phát lại; câu cố định chỉ là phương án bổ sung về sau (người dùng tự chọn, có đồng ý riêng), chưa làm.

## Bot có bị bắt không?
- **Bot ngây thơ** (script, `adb`, mã độc cơ bản): có, kênh chạm/vuốt và PIN đã bắt ~100%; kênh chuyển động thêm "không có tay cầm".
- **Bot khôn** (lấy mẫu từ dân số, giả cảm biến): **không đảm bảo**. Đây là giới hạn đã biết (E4b: 20–73%; ActReal). Lợi thế duy nhất của hợp nhất là buộc kẻ tấn công giả nhất quán nhiều kênh.
- **Độc lập thì nhân, tương quan thì không:** nếu 4 kênh độc lập, FAR có thể nhân (vd. 37,5% × 43% ≈ 16%), nhưng cùng một tư thế, cùng một máy, cùng một phiên thì chúng **tương quan**, đừng nhân khi chưa đo.

## Việc nên làm tiếp (theo giá trị)
1. **Thử bot `adb` trên điện thoại nằm yên trên bàn vs người cầm máy:** đo độ rung chuyển động. Rẻ, quyết định xem kênh 1 có thật sự là cổng chống bot. Cần ≥ 100 Hz (gốc Android) hoặc ≥ 50 Hz (web, nếu máy cho).
2. **Thu dữ liệu đội có chuyển động**, mỗi người nhập PIN + gõ câu, cùng máy cho cả chủ và "kẻ gian" (người thứ hai cầm máy của chủ) để tách nhiễu thiết bị.
3. **Kiểm tra khớp thời điểm chạm và cú giật IMU** (cần tốc độ lấy mẫu cao).
4. Đặc trưng `imu_*` trong `features.py`: **chưa viết**; viết khi có dữ liệu cùng máy.

## 7. Flow mới (26/11/2026, thiết kế, chưa cài, chưa đo)

### 7.1 Hai tầng chấm điểm
1. **Tầng 1, người hay máy** (không cần đăng ký): luật + LightGBM tuỳ chọn + kiểm tra phát lại (`human.py`, `human_model.py`, `replay.py`). Đã có. Bản online có mô hình học bật từ 26/11 (`/health`: `human:true, owner:true`; trước đó rơi về luật vì lightgbm không nạp được trên Vercel).
2. **Tầng 2, người với người** (cần đăng ký): so thao tác với mẫu của chủ (`owner.py`, `owner_model.py` tuỳ chọn). Đã có; chỉ là **tín hiệu rủi ro, không phải cổng** (kẻ biết PIN lọt 38–57% ở FRR 5%).
3. Hợp nhất trong `fusion.py` rồi `allow | step_up | hold`. Tầng 2 chỉ dẫn tới `step_up`, không bao giờ tự chặn.

### 7.2 Bốn kịch bản
| | Chiếm từ xa | Trộm điện thoại |
|---|---|---|
| **Android** | Mã độc Trợ năng tiêm cú chạm. **Tầng 1 là lớp chính**; thêm kênh nghiêng máy (7.3). | Kẻ trộm là người, có thể biết PIN. **Tầng 2 là lớp chính**; kẻ gian dùng đúng máy của chủ (không còn nhiễu thiết bị như dữ liệu StrokePIN). |
| **iPhone** | **Ngoài phạm vi.** Nhận định của đội: iOS không có tương đương Trợ năng để tiêm cú chạm; kiểu "nạn nhân tự gõ theo lời kẻ lừa" thì người gõ là chủ thật, Innate không bắt được, chỉ còn ngữ cảnh (người nhận mới, số tiền). Chưa kiểm chứng bằng tài liệu. | Như Android; web SDK chưa kiểm kích thước chạm trên iOS. |

Mẫu chủ gắn theo từng máy: đổi máy hoặc đổi tư thế phải đăng ký lại có kiểm soát (`dang-ky-lai.md`, chưa cài). Chưa có số đo nào tách theo iPhone/Android.

### 7.3 Nghiêng máy khi bấm (bảo vệ Android bị chiếm từ xa)
- **Ý:** mã độc tiêm cú chạm bằng phần mềm, máy thường nằm yên (vd. 2 giờ sáng trên bàn); người cầm máy thì góc nghiêng nằm trong khoảng quen thuộc và có rung nhẹ trùng thời điểm mỗi cú chạm.
- **Đặc trưng đề xuất:** góc nghiêng trung bình lúc nhập PIN (vector trọng lực), độ lệch của góc trong lúc nhập, biên độ gia tốc quanh mỗi `t_down`/`t_up`, tương quan giữa đỉnh gia tốc và thời điểm chạm.
- **Đặt vào tầng 1 (chống bot), không đưa vào nhận chủ.** E23 cho EER 0,04 nhưng là nhiễu thiết bị và mất hết khi đổi tư thế; quy ước repo: không tuyên bố IMU nhận chủ.
- **Giới hạn nói trước:** nạn nhân đang cầm máy lúc mã độc bấm thì tín hiệu yếu đi; mã độc có Trợ năng đọc và phát lại được cảm biến (ActReal 71–77%), nên chỉ là bằng chứng cộng thêm; web `DeviceMotion` hạn chế tần số và quyền, bản chính thức cần SDK native Android; dữ liệu cảm biến cần thêm đồng ý (Luật BVDLCN 2025); StrokePIN chỉ ~5 Hz nên **chưa có dữ liệu nào để đo ý này**.
- **Việc làm:** (1) thêm đọc cảm biến ≥ 50 Hz vào `#/collect` trên Android, hai điều kiện cầm máy và đặt trên bàn, cập nhật phiếu đồng ý; (2) chạy bot `adb`/`dispatchGesture` trên máy Android thật để có mẫu "máy đứng yên bị tiêm cú chạm"; (3) đo hai nhóm có tách được không rồi mới viết `imu_*` vào `features.py`.

### 7.4 Nhập PIN trước, chấm điểm ở bước chuyển tiền
**Ý của đội:** PIN nhập lúc mở ví/đăng nhập, **không chặn ở đó**; kẻ trộm cứ nhập PIN, và chỉ đến bước chuyển tiền Innate mới bắt đầu phân biệt bot, kẻ trộm, người thật. Hợp với quy tắc "không tự khoá tài khoản".

Thiết kế đề xuất:
- **Vẫn ghi PIN lúc đăng nhập, nhưng ở chế độ thụ động** (chỉ thời gian, toạ độ, nhãn phím như hiện nay), gắn với phiên giao dịch sau đó. Không chấm điểm để chặn ở bước này.
- **Chấm điểm một lần ở xác nhận chuyển tiền**, gộp: nhịp PIN đã ghi + thao tác ở bước chuyển (gõ số tài khoản, chọn ngân hàng, nhập số tiền, vuốt xác nhận) + chuyển động (7.3) + ngữ cảnh (người nhận mới, số tiền bất thường). Khi chưa chắc mới yêu cầu gõ câu (kênh 3).

Điều phải tính trước, vì đổi chỗ nhập PIN làm đổi bằng chứng:
1. **Mất bằng chứng mạnh nhất tại điểm quyết định.** Nhận chủ hiện dựa gần hết vào nhịp PIN (lặp đúng 6 số mỗi lần). Số tài khoản đổi theo từng người nhận nên yếu (E14: chỉ là bằng chứng cộng thêm), vuốt không nhận chủ được (AUC ~0,5). Vì vậy bằng chứng người/người ở bước chuyển chủ yếu vẫn là PIN đã ghi trước đó.
2. **Kẽ hở "chủ mở khoá rồi đưa máy" (hoặc bị giật máy sau khi mở khoá):** PIN đúng nhịp chủ, nhưng người chuyển tiền là kẻ khác. Cần kiểm tra **cùng một người xuyên suốt phiên**, so nhịp bấm ở bước chuyển với nhịp PIN trong cùng phiên. Đây là giả thuyết, chưa có thí nghiệm.
3. **Mã độc có thể không cần nhập PIN** nếu chiếm phiên đang mở; khi đó phần bằng chứng PIN trống và chỉ còn bước chuyển tiền + chuyển động, nên cần luật `missing_pin_evidence` được cân nhắc lại (hiện chỉ là lý do, xem `api.ts`).
4. **Số liệu cũ (E24–E28) đo với PIN nằm ngay lúc xác nhận.** Khi tách PIN ra khỏi bước xác nhận, các số này không còn áp dụng nguyên vẹn và phải đo lại.
5. **Tác động lên code và demo:** schema `SessionIn` hiện gom `pin_taps`, `fields`, `swipes` vào một phiên; cần liên kết hai phiên (đăng nhập và chuyển tiền) hoặc thêm trường. **Cập nhật 26/11: ví demo (`Wallet.tsx`) đã đổi sang PIN-trước** (mở ví bằng PIN chỉ ghi, chấm điểm ở xác nhận chuyển tiền, một phiên mang cả hai); video script và PDF hướng dẫn cần khớp thứ tự này. Phần chưa làm là đo lại E24–E29 theo thứ tự mới và liên kết hai phiên ở API.

### 7.5 Việc nên làm tiếp (theo giá trị)
1. Chốt với đội: PIN-trước có thay flow demo và video hay chỉ là mô tả thiết kế (tác động ở 7.4 mục 5).
2. Thu dữ liệu Android có chuyển động (7.3), người thứ hai cầm máy của chủ làm "kẻ gian".
3. Thí nghiệm kiểm tra cùng một người xuyên suốt phiên (7.4 mục 2) trên dữ liệu đội khi có.

### 7.6 Quyết định sau khi chấm điểm (đề xuất cho ví; ngưỡng do ví quyết định)
Innate chỉ **đề xuất**, không bao giờ tự khoá tài khoản.

| Mức | Khi nào | Hành động gợi ý |
|---|---|---|
| **allow** | Chắc là người, khớp chủ, ngữ cảnh bình thường | Cho qua, không thêm bước. Cập nhật mẫu chủ chỉ khi chắc chắn (giữ giới hạn trôi). |
| **step_up** | Là người nhưng không khớp chủ, hoặc ngữ cảnh lạ (người nhận mới, số tiền lớn) | **Gõ một câu** (Innate Challenge, ~10 giây); chưa chắc nữa thì khuôn mặt hoặc OTP. Có thể thêm trì hoãn ngắn kèm thông báo cho chủ. |
| **hold** | Rõ ràng là máy, hoặc rủi ro rất cao | **Tạm hoãn lệnh**, báo chủ qua kênh khác, chủ có thể giải phóng lệnh, có **thời hạn giữ** để lệnh không treo mãi, đẩy sang đội vận hành xem lý do. Tài khoản không bị khoá. |

Hành động đi kèm (người dùng không thấy): đóng băng mẫu chủ khi nghi ngờ (`owner.update`, chưa hiện ra API); đội vận hành gắn nhãn fraud/legit làm dữ liệu huấn luyện.

Theo kịch bản: Android bị chiếm từ xa nghiêng về `hold` (tầng người/máy bắt được); trộm máy nghiêng về `step_up` (tầng người/người chỉ là tín hiệu rủi ro, đừng `hold` chỉ vì điểm chủ thấp). Ngưỡng `NHIP_THRESHOLD_A/B` chưa hiệu chỉnh trên dữ liệu thật; đánh đổi giữa làm phiền chủ và chặn kẻ gian không có điểm tối ưu miễn phí (E24).

**Câu ở bước `step_up`:**

| | Câu cố định (vd. "tôi là Nghĩa") | Câu ngẫu nhiên do máy chủ cấp |
|---|---|---|
| So người với người | Tốt hơn: đăng ký và thử cùng câu | Khó so hơn: câu đổi mỗi lần (E21b) |
| Chống phát lại | Yếu: kẻ ghi nhịp gõ phát lại nguyên văn | Tốt |
| Dữ liệu cá nhân | Có nếu dùng tên thật | Không |
| Kẻ trộm đoán được câu | Có thể (biết tên chủ) | Không |

Quyết định: **mặc định câu ngẫu nhiên** (cổng chống bot và phát lại). **Câu cố định chỉ là bổ sung về sau**, người dùng tự chọn một cụm bất kỳ (không phải tên) và có đồng ý riêng; chưa làm. Gõ câu **không phải cổng**: ở 30 phím kẻ gian vẫn lọt 43–52% (E22); kết quả quay lại `fusion` làm thêm bằng chứng, chỉ khi gõ sai hoặc không có thao tác gõ dấu mới leo lên khuôn mặt/OTP. Chưa đo câu cố định.

### 7.7 Dùng cho pitch: thu gì để phân tích người với người
**Thu** (chỉ siêu dữ liệu hành vi): thời điểm nhấn/nhả từng phím (thời gian giữ, khoảng nghỉ); vị trí chạm và độ lệch so với tâm phím; nhịp nhập số tài khoản và câu thử thách (chỉ thời gian, loại phím, độ dài); ngữ cảnh (người nhận mới, số tiền). Dự kiến, chưa làm: góc nghiêng và rung máy lúc bấm (cần đồng ý riêng).

**Không thu:** nội dung PIN thật, số tiền, số tài khoản, nội dung câu gõ, danh bạ, ảnh, giọng nói, vị trí. Ngoại lệ: trang thu dữ liệu nghiên cứu `#/collect` lưu PIN thử do tình nguyện viên tự đặt (kèm cảnh báo không dùng PIN thật), không đưa vào SDK sản phẩm.

**Cố ý không dùng:** kích thước vùng chạm (nhiễu thiết bị, E12b) và vuốt để nhận chủ (AUC ~0,5, E19). Nên nói chủ động như một điểm trung thực.

**Cách kể:** mỗi người có nhịp bấm và thói quen chạm riêng; đăng ký 3 lần, so thao tác hiện tại với mẫu đó; kết quả là tín hiệu rủi ro, không phải chìa khoá.

**Giới hạn nói trước** (số trên StrokePIN, 97 người, chưa phải dữ liệu của đội): kẻ biết PIN lọt 38–57% ở FRR 5%; đổi tư thế gần như mất tín hiệu; dữ liệu chạm là dữ liệu nhạy cảm (Luật BVDLCN 2025), chỉ thu khi có đồng ý. Chưa có số đo riêng iPhone/Android, chưa có bot thật; PIN-trước, nghiêng máy và câu cố định chưa được đo.
