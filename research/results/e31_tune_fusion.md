# E31 — chỉnh trọng số fusion và ngưỡng A (tune 3 phần, kiểm 2 phần của E29)

Ràng buộc: chủ ngồi allow trên phần tune >= hiện tại (77%). Mục tiêu: trung bình tỉ lệ không-allow của 7 nhóm tấn công thích nghi. Lưới: wo 0,20–0,70, wb 0,20–0,50, A 0,05–0,49; B=0,55; số tiền = 0; trọng số người nhận mới 0,15. Bot ngây thơ và phát lại ≤±10% đã 100% ở mọi cấu hình nên không đưa vào mục tiêu.

Chọn được: wb=0.50, wo=0.30, A=0.26 (hiện tại: wb=0,40, wo=0,35, A=0,25).

| Nhóm | hiện tại (kiểm) | đã chỉnh (kiểm) | hiện tại (tune) | đã chỉnh (tune) |
|---|---|---|---|---|
| chủ, cùng tư thế (ngồi) (allow) | 76% | 76% | 77% | 77% |
| kẻ biết PIN (người khác, máy khác) (không allow) | 81% | 77% | 76% | 71% |
| bot CT4 lấy mẫu dân số (không allow) | 98% | 98% | 96% | 95% |
| bot biết mẫu chuẩn (scale 1.0) (không allow) | 31% | 35% | 26% | 32% |
| bot biết mẫu chuẩn (scale 0.5) (không allow) | 16% | 21% | 12% | 17% |
| phát lại ±15% (không allow) | 52% | 54% | 47% | 51% |
| phát lại ±20% (không allow) | 44% | 47% | 40% | 43% |
| phát lại ±30% (không allow) | 67% | 68% | 69% | 70% |
| **trung bình nhóm tấn công** | 55% | 57% | 52% | 54% |

Chủ đi allow (kiểm): hiện tại 47%, đã chỉnh 52%. Người nhận MỚI, chủ ngồi allow (kiểm): hiện tại 6%, đã chỉnh 5%.

Giới hạn: một lần chia tune/kiểm, 97 người; mục tiêu là lựa chọn của đội (7 nhóm ngang nhau); bot do đội sinh; chưa dữ liệu đội. Không nên áp dụng nếu mức cải thiện trên phần kiểm nhỏ hơn dao động giữa hai phần.
