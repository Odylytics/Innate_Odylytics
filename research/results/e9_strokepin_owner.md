# E9 — xác minh chủ trên PIN điện thoại thật (StrokePIN, 97 người, PIN 6 số)

Dùng `features.py` + `owner.py` của backend. Kẻ gian **biết PIN** (người khác nhập cùng PIN). Đăng ký k lượt; điểm gộp mọi cặp (người, PIN), CI 95% bootstrap theo người (100 lần). Thấp hơn là tốt hơn. Dữ liệu người thật; mỗi người một điện thoại, nên khác thiết bị giữa người cũng góp vào độ tách.

## k = 3 lượt đăng ký

| Bộ đặc trưng | Bộ phát hiện | EER | FAR @ FRR 5% |
|---|---|---|---|
| thời gian | backend (owner.py: sd có sàn) | 0.201 [0.193, 0.209] | 0.686 [0.647, 0.719] |
| thời gian | Manhattan scaled | 0.265 [0.256, 0.272] | 0.784 [0.760, 0.803] |
| thời gian | E2 co rút về dân số (nu=5) | 0.199 [0.190, 0.207] | 0.565 [0.531, 0.588] |
| thời gian + lệch tâm | backend (owner.py: sd có sàn) | 0.166 [0.157, 0.174] | 0.671 [0.601, 0.757] |
| thời gian + lệch tâm | Manhattan scaled | 0.236 [0.225, 0.246] | 0.847 [0.798, 0.879] |
| thời gian + lệch tâm | E2 co rút về dân số (nu=5) | 0.196 [0.185, 0.206] | 0.658 [0.607, 0.705] |
| thời gian + lệch tâm + kích thước chạm | backend (owner.py: sd có sàn) | 0.155 [0.145, 0.164] | 0.656 [0.575, 0.747] |
| thời gian + lệch tâm + kích thước chạm | Manhattan scaled | 0.230 [0.221, 0.239] | 0.914 [0.896, 0.926] |
| thời gian + lệch tâm + kích thước chạm | E2 co rút về dân số (nu=5) | 0.159 [0.150, 0.169] | 0.538 [0.484, 0.610] |

## k = 5 lượt đăng ký

| Bộ đặc trưng | Bộ phát hiện | EER | FAR @ FRR 5% |
|---|---|---|---|

## So sánh ghép cặp: E2 (co rút về dân số) trừ backend hiện tại, âm = E2 tốt hơn

| k | Bộ đặc trưng | dEER | dFAR @ FRR 5% |
|---|---|---|---|
| 3 | thời gian | -0.002 [-0.007, +0.003] | -0.121 [-0.145, -0.095] |
| 3 | thời gian + lệch tâm | +0.031 [+0.025, +0.036] | -0.013 [-0.058, +0.031] |
| 3 | thời gian + lệch tâm + kích thước chạm | +0.003 [-0.001, +0.008] | -0.118 [-0.160, -0.072] |
