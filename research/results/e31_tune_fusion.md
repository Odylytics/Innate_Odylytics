# E31 — chỉnh trọng số fusion và ngưỡng A (tune 3 phần, kiểm 2 phần của E29)

Ràng buộc: chủ allow trên phần tune >= hiện tại (76%). Mục tiêu: trung bình tỉ lệ không-allow của 7 nhóm tấn công thích nghi. Lưới: wo 0,20–0,70, wb 0,20–0,50, A 0,05–0,49; B=0,55; số tiền = 0; trọng số người nhận mới 0,15. Bot ngây thơ và phát lại ≤±10% đã 100% ở mọi cấu hình nên không đưa vào mục tiêu.

Chọn được: wb=0.50, wo=0.30, A=0.26 (hiện tại: wb=0,40, wo=0,35, A=0,25).

| Nhóm | hiện tại (kiểm) | đã chỉnh (kiểm) | hiện tại (tune) | đã chỉnh (tune) |
|---|---|---|---|---|
| chủ (allow) | 79% | 79% | 76% | 76% |
| kẻ biết PIN (người khác, máy khác) (không allow) | 86% | 81% | 81% | 75% |
| bot CT4 lấy mẫu dân số (không allow) | 98% | 97% | 97% | 97% |
| bot biết mẫu chuẩn (scale 1.0) (không allow) | 25% | 30% | 22% | 28% |
| bot biết mẫu chuẩn (scale 0.5) (không allow) | 9% | 12% | 12% | 16% |
| phát lại ±15% (không allow) | 50% | 51% | 53% | 55% |
| phát lại ±20% (không allow) | 41% | 43% | 46% | 47% |
| phát lại ±30% (không allow) | 71% | 67% | 74% | 72% |
| **trung bình nhóm tấn công** | 54% | 54% | 55% | 56% |

Người nhận MỚI, chủ allow (kiểm): hiện tại 16%, đã chỉnh 15%.

Giới hạn: một lần chia tune/kiểm, 97 người; mục tiêu là lựa chọn của đội (7 nhóm ngang nhau); bot do đội sinh; chưa dữ liệu đội. Không nên áp dụng nếu mức cải thiện trên phần kiểm nhỏ hơn dao động giữa hai phần.
