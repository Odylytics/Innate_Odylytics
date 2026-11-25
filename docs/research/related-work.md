# Công trình liên quan và bài học áp dụng (cập nhật 25/11/2026)

Bổ sung cho [`paper-report.md`](paper-report.md) (52 PDF trong `papers/`). Phần này ghi **điều gì đã làm ở lĩnh vực gần Innate Challenge tiếng Việt, đội học được gì, và đã thử/áp dụng gì**. Tìm kiếm ngày 25/11/2026; kết quả tìm kiếm chỉ là tóm tắt, **chưa đọc toàn văn** trừ khi ghi khác.

## 1. Khoảng trống: không thấy công trình về nhịp gõ tiếng Việt (Telex/VNI) hay Pinyin IME

Hai lượt tìm ("keystroke dynamics Vietnamese Telex VNI", "keystroke dynamics Chinese Pinyin IME") **không ra bài nào** nghiên cứu sinh trắc học từ cách gõ qua bộ gõ (IME). Chỉ có các khảo sát chung ([Keystroke Dynamics: Concepts, Techniques, and Applications](https://arxiv.org/pdf/2303.04605), [A Review of Several Keystroke Dynamics Methods](https://arxiv.org/pdf/2502.16177)) và một bằng sáng chế gõ tự do không phụ thuộc ngôn ngữ ([US 10970573](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10970573)). **Cách nói an toàn:** "chúng tôi không tìm thấy công trình công bố nào về kiểu gõ Telex/VNI làm tín hiệu sinh trắc"; không nói "chưa ai làm". Hướng của đội (phím biến đổi, vị trí dấu thanh) vì vậy là **giả thuyết mới, chưa có tiền lệ để so sánh**, và phải tự đo (xem `innate-challenge-vi.md`).

## 2. Nhận chủ bằng gõ tự do trên điện thoại

| Công trình | Điều đã làm | Bài học cho Innate |
|---|---|---|
| Stragapede et al., [TypeFormer](https://arxiv.org/abs/2212.13075) (Neural Comput. Appl. 2024) | Transformer cho gõ tự do trên Aalto, EER 3,25% với 5 buổi đăng ký × 50 phím | Số này cần mô hình huấn luyện trên hàng chục nghìn người và 50 phím; **E13 của đội: EER 0,245 ở 30 phím, 3 câu đăng ký, chỉ 6 đặc trưng**. Khoảng cách lớn: số phím và mô hình đều quan trọng. Đội chưa có dữ liệu để huấn luyện mạng sâu. |
| Acien et al., TypeNet (T-BIOM 2021) | EER di động 10,7% (G=1) xuống 6,3% (G=10) theo số lượt đăng ký | Xác nhận hướng "đăng ký nhiều lượt hơn thì tốt hơn" (E9, E13). |
| Gunetti & Picardi, [Keystroke Analysis of Free Text](https://dblp.uni-trier.de/rec/journals/tissec/GunettiP05.html) (TISSEC 2005) | So hai mẫu gõ tự do bằng thứ hạng tốc độ của các cặp phím chung (R) và tốc độ tuyệt đối (A) | Đội thử hai ý tưởng cùng họ trong E21 và E21b (xem mục 5). |
| Killourhy & Maxion (DSN 2009) | Scaled Manhattan là bộ dò tốt nhất trong 14 bộ | Đã dùng trong `owner.py`. |

## 3. Tấn công vào sinh trắc hành vi (giới hạn của Innate)

| Công trình | Nội dung | Ảnh hưởng tới Innate |
|---|---|---|
| Serwadda & Phoha, [Examining a Large Keystroke Biometrics Dataset for Statistical-Attack Openings](https://api.crossref.org/works/10.1145%2F2516951.2516960) (TISSEC 2013) | Tấn công thống kê dùng dữ liệu dân số làm tăng lỗi của 3 bộ xác minh 28,6–84,4%, mạnh hơn với chuỗi ngắn | Đúng chiến thuật 4 của đội (lấy mẫu từ dân số); xác nhận chuỗi ngắn (PIN) yếu hơn chuỗi dài (câu). |
| Serwadda & Phoha, "Robotic Robbery on the Touch Screen" (TISSEC 2016) | Robot Lego vuốt theo thống kê dân số vượt xác thực cảm ứng | Cùng hướng: thành phần "nhịp" không phải rào chắn tuyệt đối. |
| [Conditional GAN cho tấn công trình diễn gõ phím](https://arxiv.org/pdf/2212.08445) | GAN sinh nhịp gõ tự do để lừa bộ xác thực | Bot học từ dữ liệu người (chiến thuật 4) là mối đe doạ thật; bot lạ chưa thấy là điểm yếu của Innate (E4b, E11). |
| Wang et al., [ActReal](https://arxiv.org/pdf/2608.30038) (preprint 2026) | Tác tử cấp hệ thống giả tương tác, thành công 77,5% trước 6 bộ phát hiện (HMOG, TToS, BehaveFormer, AuthConFormer) | Đã nằm trong `paper-report.md`; giữ giới hạn "nhịp không đủ một mình". |
| Bimodal user verification vs synthetic data, [SECRYPT 2025](https://www.scitepress.org/PublishedPapers/2025/134501) | Dữ liệu GAN đe doạ khuôn mặt hơn cử chỉ nhấc máy | Gợi ý: kết hợp nhiều kênh cứng hơn một kênh. |
| Schneier blog 2005 + [patent US 11222101](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11222101) | Đòi gõ câu/chuỗi mới mỗi lần để chặn phát lại | Cùng ý Innate Challenge; ý kiến phản biện: kẻ gian vẫn phát lại **timing** của nạn nhân lên câu mới. **Chưa thấy đánh giá nghiêm túc** cho thiết kế này; đội chưa chặn được phát lại timing trên câu mới (mục 5, hướng việc tiếp). |

## 4. Điều Innate làm khác

1. **Kênh "kiểu gõ" độc lập với nhịp** (vị trí dấu thanh, sửa lỗi, có dùng bộ gõ): phát lại timing lên câu mới **không** tái tạo được kênh này nếu bot không giả lập bộ gõ. Đây là lý do chính để làm tiếng Việt (chưa đo).
2. **Phiên mô phỏng dưới ràng buộc riêng tư:** chỉ thời gian, loại sự kiện, độ dài, lớp ký tự; nội dung câu do máy chủ biết (token ký).
3. **Báo cáo trung thực theo FETA:** tách theo thời gian, một máy, FAR@FRR 5%.

## 5. Đã thử học theo (kết quả đo)

- **E19 (Touchalytics, 41 người):** sửa luật vuốt (xem `ai-research.md`).
- **E21 (Aalto, 1.000 người đánh giá):** chuẩn hoá nhịp theo **cặp phím** (cách TypeNet/TypeFormer học nội dung, và R/A của Gunetti–Picardi). **Kết quả gần như không đổi**: ở 30 phím EER 0,249 (thô) → 0,245 (chuẩn hoá) → 0,238 (thô + chuẩn hoá); FAR@FRR 5% 0,498 → 0,467. Khoảng tin cậy chồng nhau, nên **cải thiện nhỏ, chưa chắc có**.
- **E21b:** so hồ sơ từng cặp phím phổ biến giữa câu đăng ký và câu thử **làm tệ hơn** (EER 0,326 một mình; ghép thêm vẫn không hơn), vì hai câu ngẫu nhiên chỉ chung trung bình 6,5 cặp phổ biến ở 30 phím.
- **Kết luận:** với câu ngẫu nhiên mỗi lần, **bước nhảy không đến từ chuẩn hoá nội dung**. Hai hướng còn lại: (a) đặc trưng không phụ thuộc câu như kiểu gõ tiếng Việt (E20, mô phỏng); (b) dùng bộ câu nhỏ cố định để có câu trùng giữa đăng ký và thử (chưa đo, đánh đổi: dễ phát lại hơn).

## 6. Việc đọc tiếp (chưa làm)

Đọc toàn văn Gunetti & Picardi 2005 (công thức R), Serwadda & Phoha 2013, TypeFormer (số liệu theo độ dài chuỗi) trước khi trích dẫn số liệu trong slide. Tìm thêm: IME/Pinyin biometrics bằng tiếng Trung, HuMIdb, nhịp gõ trên bàn phím gợi ý từ.
