# Ghi chú nghiên cứu công nghệ

> Cập nhật 24/11/2026. Mỗi mục ghi độ tin cậy: **đã kiểm chứng** (đọc nguồn gốc hoặc chạy thí nghiệm), **một phần** (nguồn thứ cấp), **chưa biết**.

## 1. Mối đe doạ có thật và đang tiến hoá (đã kiểm chứng, nguồn thứ cấp)

| Mã độc | Khả năng | Nguồn |
|---|---|---|
| RemControl | Lạm dụng Trợ năng: lớp phủ giả, phát màn hình trực tiếp, ghi phím, điều khiển từ xa. Dropper chặn Play Protect qua VPN cục bộ và tạo chứng chỉ ký riêng mỗi lần cài nên né phát hiện theo hash | [Group-IB](https://www.group-ib.com/blog/remcontrol/), [Infosecurity](https://www.infosecurity-magazine.com/news/banking-trojan-remote-control/) |
| ToxicPanda 2.0 (08/2026) | Lớp phủ ngân hàng, điều khiển từ xa, lấy PIN, lạm dụng Trợ năng, thử Wireless Debugging. Mục tiêu là gian lận ngay trên máy nạn nhân (on-device fraud) | [Malwarebytes](https://www.malwarebytes.com/blog/mobile/2026/08/toxicpanda-2-0-can-take-over-your-android-phone-and-banking-apps) |
| Trojan do Cyfirma báo (11/2025) | Đọc màn hình, bấm nút, điền form "như người dùng" | [Malwarebytes](https://www.malwarebytes.com/blog/news/2025/11/sneaky-new-android-malware-takes-over-your-phone-hiding-in-fake-news-and-id-apps) |

Ý nghĩa: kịch bản A của Innate có nền thực tế. Các báo cáo nói kẻ tấn công thao tác trong phiên đang mở nên né được kiểm soát theo thiết bị lạ/vị trí lạ, đúng khe hở mà lớp hành vi muốn lấp. Các nguồn này **không** bàn về phát hiện chạm do máy.

## 2. R1: phân biệt chạm thật và chạm bơm (chưa biết)

Tìm kiếm công khai không trả lời được. Những gì tìm thấy:
- Framework Android có cờ cho sự kiện được bơm từ dịch vụ Trợ năng (AOSP có hằng `INJECTED_FROM_ACCESSIBILITY_TOOL` trong bộ cờ đầu vào; xem [commit mirror](https://gitlab.e.foundation/e/os/android_frameworks_native/-/commit/8a1be9125beb41e22d59e55ce64627be1a2c2880)). **Chưa kiểm chứng** cờ này có tới được `MotionEvent` mà app/WebView nhìn thấy hay chỉ nằm ở tầng hệ thống.
- `dispatchGesture` nhận `GestureDescription` và framework tự dựng chuỗi `MotionEvent`, nên dịch vụ độc hại kiểm soát quỹ đạo và thời gian ([AOSP](https://android.googlesource.com/platform/frameworks/base/+/5f256310187b4ff2f13a7abb9afed9126facd7bc)).
- Web SDK chỉ thấy Pointer Events, không đọc được cờ hệ thống. Đây có thể là lý do thực tế cần SDK native. Cần thí nghiệm để biết trường nào lộ ra.

**Việc cần làm:** thí nghiệm R1 trong [`research-plan.md`](research-plan.md).

## 3. R2: hình học chạm trên web (một phần)

- Pointer Events được MDN xếp "Baseline widely available" từ 07/2020 ([MDN](https://developer.mozilla.org/en-US/docs/Web/API/PointerEvent)).
- `width`/`height` là vùng tiếp xúc tính bằng CSS pixel, **mặc định 1 khi phần cứng không báo được** ([MDN width](https://developer.mozilla.org/Web/API/PointerEvent/width)).
- Chưa xác nhận máy demo của đội trả giá trị thật hay luôn là 1. Nếu là 1 thì `tap_w_*`/`tap_h_*` vô dụng và Zheng 2014 (dùng kích thước chạm) không áp dụng được.
- Backend hiện không dựa vào `pressure`: đúng, vì chuẩn trả 0,5 khi máy không đo.

## 4. Kẻ tấn công thích nghi (đã kiểm chứng, preprint)

ActReal (Wang 2026): tác nhân cấp hệ thống sinh đồng thời chạm và IMU khớp thời gian, thành công trung bình 77,5%, còn 71,1% khi bộ phát hiện dùng cả chạm lẫn IMU. Hệ quả: lớp "người hay máy" chắc nhất với bot ngây thơ. Pitch cần nói thẳng và đo bằng nguồn bot độc lập. Chi tiết: [`../plan/mo-ta-du-an-va-kiem-chung.md`](../plan/mo-ta-du-an-va-kiem-chung.md) mục 4.

## 5. Mô hình và đánh giá (đã kiểm chứng bằng paper)

Xem bảng đối chiếu ở [`../plan/mo-ta-du-an-va-kiem-chung.md`](../plan/mo-ta-du-an-va-kiem-chung.md) mục 3. Tóm tắt: kỳ vọng EER thực tế 10–15% với ~25 người, một máy, 3–5 lượt; imitation attack 10–15% (BioTouchPass2); báo FAR@FRR kèm khoảng tin cậy.

## Câu hỏi còn mở

1. Cờ "injected" có lộ ra cho app/WebView không? (R1)
2. `width`/`height` trên máy demo? (R2)
3. Cách vào được bản dùng thử của giám khảo: key công khai hay nhúng? (R6)
4. Có cần SDK native để thành sản phẩm thật, hay web đủ cho cuộc thi? (quyết định sau R1)
