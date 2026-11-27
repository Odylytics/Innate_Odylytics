# E23 — PIN + chuyển động. Xác minh chủ trên PIN điện thoại thật (StrokePIN, 97 người, PIN 6 số)

Dùng `features.py` + `owner.py` của backend. Kẻ gian **biết PIN** (người khác nhập cùng PIN). Đăng ký k lượt; điểm gộp mọi cặp (người, PIN), CI 95% bootstrap theo người (100 lần). Thấp hơn là tốt hơn. Dữ liệu người thật; mỗi người một điện thoại, nên khác thiết bị giữa người cũng góp vào độ tách.

## k = 3 lượt đăng ký

| Bộ đặc trưng | Bộ phát hiện | EER | FAR @ FRR 5% |
|---|---|---|---|
| PIN (thời gian + lệch tâm) | backend (owner.py: sd có sàn) | 0.166 [0.156, 0.174] | 0.671 [0.587, 0.749] |
| PIN (thời gian + lệch tâm) | Manhattan scaled | 0.236 [0.227, 0.246] | 0.847 [0.790, 0.873] |
| PIN (thời gian + lệch tâm) | E2 co rút về dân số (nu=5) | 0.196 [0.189, 0.204] | 0.658 [0.612, 0.703] |
| chỉ chuyển động (IMU) | backend (owner.py: sd có sàn) | 0.068 [0.063, 0.074] | 0.091 [0.080, 0.109] |
| chỉ chuyển động (IMU) | Manhattan scaled | 0.063 [0.058, 0.070] | 0.083 [0.068, 0.100] |
| chỉ chuyển động (IMU) | E2 co rút về dân số (nu=5) | 0.038 [0.034, 0.045] | 0.029 [0.024, 0.039] |
| PIN + chuyển động (IMU) | backend (owner.py: sd có sàn) | 0.077 [0.067, 0.083] | 0.230 [0.151, 0.343] |
| PIN + chuyển động (IMU) | Manhattan scaled | 0.099 [0.093, 0.107] | 0.396 [0.329, 0.464] |
| PIN + chuyển động (IMU) | E2 co rút về dân số (nu=5) | 0.054 [0.049, 0.059] | 0.061 [0.046, 0.089] |

## k = 5 lượt đăng ký

| Bộ đặc trưng | Bộ phát hiện | EER | FAR @ FRR 5% |
|---|---|---|---|

## So sánh ghép cặp: E2 (co rút về dân số) trừ backend hiện tại, âm = E2 tốt hơn

| k | Bộ đặc trưng | dEER | dFAR @ FRR 5% |
|---|---|---|---|
| 3 | PIN (thời gian + lệch tâm) | +0.031 [+0.025, +0.036] | -0.013 [-0.065, +0.032] |
| 3 | chỉ chuyển động (IMU) | -0.030 [-0.038, -0.024] | -0.062 [-0.085, -0.050] |
| 3 | PIN + chuyển động (IMU) | -0.022 [-0.028, -0.017] | -0.170 [-0.271, -0.105] |
