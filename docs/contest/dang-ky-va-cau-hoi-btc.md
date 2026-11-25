# Đăng ký thi, câu hỏi gửi BTC, và các quyết định đội cần chốt

> Soạn 25/11/2026. **Hạn đăng ký và gửi câu hỏi: 23:59:59 27/11/2026.** Email BTC: techday@mservice.com.vn. Mình (Claude) chưa gửi gì; việc đăng ký và gửi email do trưởng nhóm làm.

## 1. Đăng ký (trưởng nhóm, tại https://techday.momo.vn)
- [ ] Đội 2–3 người; thành viên sinh viên ĐH/CĐ Việt Nam, quốc tịch Việt Nam, **18–23 tuổi**; không ai đang làm hoặc thực tập tại MoMo.
- [ ] Chốt **tên đội** và danh sách thành viên (điền vào README nộp bài, slide, PDF sản phẩm).
- [ ] Chụp màn hình xác nhận đăng ký, lưu lại.
- [ ] Người ngoài đội không được tham gia xây dựng sản phẩm: kiểm lại ai đã đóng góp vào repo (xem `git log`).

## 2. Câu hỏi làm rõ (bản nháp để gửi trước 27/11)

> **Tiêu đề:** [MoMo Tech Contest 2026] Câu hỏi làm rõ thể lệ — đội <TÊN ĐỘI>
>
> Kính gửi Ban tổ chức, đội <TÊN ĐỘI> xin hỏi một số điểm để nộp bài đúng thể lệ:
>
> 1. **Dữ liệu công khai có giấy phép chia sẻ cùng điều kiện.** Chúng tôi huấn luyện mô hình phát hiện bot và nhận chủ trên bộ dữ liệu công khai CC BY-NC-SA 4.0 (StrokePIN, DOI 10.21227/thft-4721), đã khai báo nguồn và giấy phép trong README. Mô hình phái sinh phải phát hành cùng giấy phép đó. Việc này có được chấp nhận trong bài nộp không, và Ban tổ chức có yêu cầu gì thêm về nguồn dữ liệu không?
> 2. **Hình thức sản phẩm.** Sản phẩm của chúng tôi là một dịch vụ API chấm điểm rủi ro hành vi (có Swagger) kèm một web demo mô phỏng luồng chuyển tiền, không phải ứng dụng di động. Hình thức này có đáp ứng yêu cầu "sản phẩm dùng được trực tuyến" không?
> 3. **Mã nguồn.** Mã nguồn của đội hiện lưu trên GitHub. Nếu để chế độ công khai trước hạn nộp thì có bị xem là chia sẻ mã giữa các đội không? Chúng tôi dự định chuyển sang riêng tư cho đến khi nộp.
> 4. **Dữ liệu do đội thu.** Chúng tôi thu nhịp chạm/gõ (chỉ thời gian, toạ độ, loại sự kiện, không lưu nội dung) từ bạn bè tự nguyện, có phiếu đồng ý bằng văn bản. Như vậy có đủ "căn cứ sử dụng dữ liệu" theo thể lệ không, và Ban tổ chức có yêu cầu mẫu phiếu cụ thể không?
> 5. **Công cụ AI hỗ trợ lập trình.** Chúng tôi dùng trợ lý lập trình AI (Claude Code) để viết mã, thí nghiệm và tài liệu, và sẽ khai trong README mục "công cụ AI đã dùng". Có giới hạn nào về mức độ sử dụng không?
> 6. **Số liệu trong slide.** Slide nộp ngày 03/12 không sửa được. Nếu có thêm kết quả đo sau hạn thì có được trình bày bổ sung ở vòng chung kết không?
>
> Xin cảm ơn Ban tổ chức. Trưởng nhóm: <TÊN>, <SĐT>.

## 3. Quyết định đội cần chốt (mình không quyết thay)

| Quyết định | Gợi ý | Lý do |
|---|---|---|
| **Giấy phép bài nộp** | Phát hành toàn bộ gói theo **CC BY-NC-SA 4.0** (hoặc ít nhất mô hình + `population_prior.json`), ghi rõ trong README | Mô hình huấn luyện trên StrokePIN là phái sinh; trộn giấy phép khác dễ vi phạm. Đây không phải tư vấn pháp lý: hỏi BTC (câu 1). |
| **Repo GitHub đang công khai** | Chuyển sang **private** trước khi nộp, mở lại sau chung kết nếu muốn | Thể lệ loại bài "chia sẻ code giữa các đội". Chủ repo (`tuannghia2457`) đổi được trong Settings; mình chỉ có quyền ghi. |
| **Dữ liệu đội thu** | Thu 10–20 bạn tự nguyện, 2 buổi, có phiếu đồng ý, không lưu nội dung; hoặc ghi rõ trong README "chưa có dữ liệu đội, chỉ dùng dữ liệu công khai" | Thể lệ loại bài dùng dữ liệu cá nhân không rõ nguồn. |
| **Bộ ảnh đại diện DiceBear (web)** | Kiểm giấy phép từng kiểu ảnh dùng trong `web/` rồi khai báo | Tài sản có sẵn phải khai đủ. |

## 4. Đã làm giúp
- README nộp bài (`docs/submission/README.submission.md`) đã điền: URL API và Swagger (`/health` và `/docs` trả 200 ngày 25/11), thư viện web, công cụ AI, dữ liệu Touchalytics và Aalto dùng ở đâu, số liệu E19 và các kết quả âm tính. **Còn `TODO`:** tên đội, thành viên, URL web, key demo, giấy phép Touchalytics/Aalto, giấy phép gói DiceBear, dữ liệu đội, mẫu phiếu đồng ý.
