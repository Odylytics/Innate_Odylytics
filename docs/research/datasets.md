# Dữ liệu để thử nghiệm

> Kiểm tra link ngày 24/11/2026 (gọi HTTP thật từ máy làm việc). **Giấy phép phải đọc lại ở trang gốc trước khi dùng cho bài nộp**, và mọi bộ dùng đều phải ghi vào README nộp bài (nguồn + giấy phép + trích dẫn).
> Dữ liệu tải về đặt ở `research/data/` (gitignored, không commit).

## Dùng được ngay, không cần xin phép

| Bộ dữ liệu | Nội dung | Kích thước | Link tải trực tiếp | Giấy phép |
|---|---|---|---|---|
| **StrokePIN** (Nankai, 2026) ⭐ | **PIN 6 số trên điện thoại**: 97 người, 18.935 lượt nhập, 20 PIN chung cho mọi người; toạ độ chạm X/Y, kích thước, áp lực, cảm biến chuyển động | repo ~68 MB | `git clone https://github.com/Litraveler/StrokePIN.git` · trang: https://ieee-dataport.org/documents/strokepin-0 (DOI 10.21227/thft-4721) | **CC BY-NC-SA 4.0** theo README repo và mô tả trang (phi thương mại, ghi nguồn, **chia sẻ phái sinh cùng giấy phép**). Trang IEEE DataPort ghi tiêu đề "Creative Commons Attribution", mâu thuẫn nhẹ: dùng điều khoản chặt hơn |
| **CMU DSL-StrongPassword** | 51 người × 400 lần gõ một mật khẩu, 31 đặc trưng thời gian (máy tính) | 4,6 MB | https://www.cs.cmu.edu/~keystroke/DSL-StrongPasswordData.csv | Kiểm 25/11: trang không nêu giấy phép; yêu cầu trích dẫn Killourhy & Maxion 2009 |
| **Touchalytics** (Frank 2013) | 41 người, vuốt/cuộn: toạ độ, áp lực, vùng chạm | **dữ liệu thô 5,2 MB** · đặc trưng 1,6 MB | http://www.mariofrank.net/touchalytics/data.zip · http://www.mariofrank.net/touchalytics/features.zip · [readme](http://www.mariofrank.net/touchalytics/readme_data.txt) | **Kiểm 25/11: trang và readme không nêu giấy phép**; trích dẫn bài TIFS 2013. Đã dùng ở E19 |
| **MOBIKEY** (Sapientia) | 54 người, 3 mật khẩu văn bản trên máy tính bảng Nexus 7, có áp lực và diện tích ngón tay | nhỏ | https://www.ms.sapientia.ro/~manyi/mobikey/data/rawdata.zip · trang: https://www.ms.sapientia.ro/~manyi/mobikey.html | Chưa kiểm |

## Nặng, link tải trực tiếp

| Bộ dữ liệu | Nội dung | Kích thước | Link tải trực tiếp (đã kiểm tra: HTTP 200) |
|---|---|---|---|
| **Aalto typing37k, bản đã xử lý** | 37.370 người gõ trên điện thoại (dạng SQL) | **0,84 GB** | https://userinterfaces.aalto.fi/typing37k/data/processed_typing_data.zip |
| **Aalto typing37k, CSV thô + đã xử lý** | Như trên, dạng CSV (dễ dùng với Python) | **5,63 GB** | https://userinterfaces.aalto.fi/typing37k/data/csv_raw_and_processed.zip |
| **Aalto typing37k, SQL thô** | Dữ liệu gốc | **4,89 GB** (giải nén 43,4 GB) | https://userinterfaces.aalto.fi/typing37k/data/raw_typing_data.zip |
| Mã thu dữ liệu của Aalto | Công cụ thu keystroke trên web | nhỏ | https://userinterfaces.aalto.fi/typing37k/resources/source_code.zip |

Trang gốc: https://userinterfaces.aalto.fi/typing37k/. **Kiểm 25/11:** trang và bài báo nói "openly available" nhưng không nêu giấy phép dữ liệu (chỉ phần mềm thu dữ liệu là MIT); trích dẫn MobileHCI 2019, hỏi tác giả nếu phát hành lại dữ liệu phái sinh. Máy làm việc hiện còn ~70 GB trống. **Bản CSV đã xử lý 0,84 GB là điểm bắt đầu hợp lý** trước khi lấy bản 5,6 GB.

## Cần thỏa thuận cấp phép (email cho nhóm tác giả)

| Bộ dữ liệu | Nội dung | Quy trình |
|---|---|---|
| **HuMIdb** | 600 người, 14 cảm biến, benchmark bot BeCAPTCHA (phục vụ bài người/máy) | https://github.com/BiDAlab/HuMIdb: ký thỏa thuận, gửi email cho `atvs@uam.es`, nhận tài khoản tải |
| **MobileTouchDB** | 217 người, 94 mẫu điện thoại, chữ số/PIN vẽ bằng tay | https://github.com/BiDAlab/MobileTouchDB: cùng quy trình, cùng email |
| **TypeNet benchmark** | Embedding keystroke | https://github.com/BiDAlab/TypeNet: cùng quy trình |
| **BB-MAS** | 117 người, nhiều thiết bị | DOI https://doi.org/10.21227/rpaz-0h66 (IEEE DataPort, cần tài khoản miễn phí; curl bị 403) |

## Không tìm được link xác nhận

HMOG, BehavePassDB, KVC, FETA: các địa chỉ tôi thử đều 404 hoặc không truy cập được, nên không liệt kê. Tìm trên trang bài báo gốc trong `papers/`.

## Ghi chú về dữ liệu bot

Không có bộ dữ liệu công khai nào chứa **mã độc điều khiển chạm thật** trên PIN. Bot phải tự sinh bằng công cụ thật (`adb input`, app `dispatchGesture`), xem R1 trong [`research-plan.md`](research-plan.md).
