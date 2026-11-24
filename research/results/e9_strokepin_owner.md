# E9 — xác minh chủ trên PIN điện thoại thật (StrokePIN, 97 người, PIN 6 số)

Dùng `features.py` + `owner.py` của backend. Kẻ gian **biết PIN** (người khác nhập cùng PIN). Đăng ký k lượt ngồi; điểm gộp mọi cặp (người, PIN), CI 95% bootstrap theo người (100 lần). Thấp hơn là tốt hơn. Dữ liệu người thật; mỗi người một điện thoại, nên khác thiết bị giữa người cũng góp vào độ tách.

## k = 3 lượt đăng ký, kiểm thử cùng tư thế (ngồi)

| Bộ đặc trưng | Bộ phát hiện | EER | FAR @ FRR 5% |
|---|---|---|---|
| thời gian | backend (owner.py: sd có sàn) | 0.201 [0.192, 0.211] | 0.710 [0.669, 0.746] |
| thời gian | Manhattan scaled | 0.264 [0.257, 0.273] | 0.799 [0.778, 0.816] |
| thời gian | E2 co rút về dân số (nu=5) | 0.200 [0.190, 0.209] | 0.570 [0.535, 0.606] |
| thời gian + lệch tâm | backend (owner.py: sd có sàn) | 0.166 [0.156, 0.175] | 0.752 [0.661, 0.832] |
| thời gian + lệch tâm | Manhattan scaled | 0.235 [0.228, 0.244] | 0.870 [0.841, 0.894] |
| thời gian + lệch tâm | E2 co rút về dân số (nu=5) | 0.197 [0.186, 0.209] | 0.692 [0.634, 0.750] |
| thời gian + lệch tâm + kích thước chạm | backend (owner.py: sd có sàn) | 0.157 [0.148, 0.167] | 0.740 [0.645, 0.837] |
| thời gian + lệch tâm + kích thước chạm | Manhattan scaled | 0.229 [0.220, 0.238] | 0.915 [0.903, 0.925] |
| thời gian + lệch tâm + kích thước chạm | E2 co rút về dân số (nu=5) | 0.161 [0.150, 0.170] | 0.581 [0.512, 0.650] |

## k = 3 lượt đăng ký, kiểm thử đổi tư thế (đi)

| Bộ đặc trưng | Bộ phát hiện | EER | FAR @ FRR 5% |
|---|---|---|---|
| thời gian | backend (owner.py: sd có sàn) | 0.323 [0.309, 0.336] | 0.839 [0.817, 0.861] |
| thời gian | Manhattan scaled | 0.365 [0.355, 0.377] | 0.890 [0.879, 0.902] |
| thời gian | E2 co rút về dân số (nu=5) | 0.318 [0.305, 0.333] | 0.763 [0.731, 0.790] |
| thời gian + lệch tâm | backend (owner.py: sd có sàn) | 0.362 [0.344, 0.381] | 0.943 [0.931, 0.952] |
| thời gian + lệch tâm | Manhattan scaled | 0.399 [0.384, 0.413] | 0.935 [0.926, 0.944] |
| thời gian + lệch tâm | E2 co rút về dân số (nu=5) | 0.374 [0.351, 0.389] | 0.936 [0.921, 0.951] |
| thời gian + lệch tâm + kích thước chạm | backend (owner.py: sd có sàn) | 0.353 [0.335, 0.378] | 0.942 [0.930, 0.953] |
| thời gian + lệch tâm + kích thước chạm | Manhattan scaled | 0.390 [0.375, 0.408] | 0.944 [0.939, 0.947] |
| thời gian + lệch tâm + kích thước chạm | E2 co rút về dân số (nu=5) | 0.342 [0.319, 0.363] | 0.925 [0.905, 0.944] |

## k = 5 lượt đăng ký, kiểm thử cùng tư thế (ngồi)

| Bộ đặc trưng | Bộ phát hiện | EER | FAR @ FRR 5% |
|---|---|---|---|

## k = 5 lượt đăng ký, kiểm thử đổi tư thế (đi)

| Bộ đặc trưng | Bộ phát hiện | EER | FAR @ FRR 5% |
|---|---|---|---|
| thời gian | backend (owner.py: sd có sàn) | 0.315 [0.299, 0.332] | 0.826 [0.795, 0.856] |
| thời gian | Manhattan scaled | 0.328 [0.314, 0.346] | 0.846 [0.811, 0.873] |
| thời gian | E2 co rút về dân số (nu=5) | 0.309 [0.293, 0.327] | 0.752 [0.706, 0.786] |
| thời gian + lệch tâm | backend (owner.py: sd có sàn) | 0.354 [0.338, 0.374] | 0.935 [0.918, 0.950] |
| thời gian + lệch tâm | Manhattan scaled | 0.372 [0.354, 0.386] | 0.935 [0.920, 0.949] |
| thời gian + lệch tâm | E2 co rút về dân số (nu=5) | 0.364 [0.347, 0.382] | 0.932 [0.921, 0.943] |
| thời gian + lệch tâm + kích thước chạm | backend (owner.py: sd có sàn) | 0.344 [0.321, 0.365] | 0.935 [0.920, 0.948] |
| thời gian + lệch tâm + kích thước chạm | Manhattan scaled | 0.353 [0.334, 0.370] | 0.937 [0.921, 0.946] |
| thời gian + lệch tâm + kích thước chạm | E2 co rút về dân số (nu=5) | 0.332 [0.313, 0.354] | 0.922 [0.909, 0.940] |

## So sánh ghép cặp: E2 (co rút về dân số) trừ backend hiện tại, âm = E2 tốt hơn

| k | Kiểm thử | Bộ đặc trưng | dEER | dFAR @ FRR 5% |
|---|---|---|---|---|
| 3 | cùng tư thế (ngồi) | thời gian | -0.001 [-0.005, +0.004] | -0.140 [-0.161, -0.107] |
| 3 | cùng tư thế (ngồi) | thời gian + lệch tâm | +0.031 [+0.026, +0.037] | -0.060 [-0.095, -0.017] |
| 3 | cùng tư thế (ngồi) | thời gian + lệch tâm + kích thước chạm | +0.005 [+0.000, +0.009] | -0.159 [-0.198, -0.117] |
| 3 | đổi tư thế (đi) | thời gian | -0.004 [-0.010, +0.001] | -0.076 [-0.097, -0.055] |
| 3 | đổi tư thế (đi) | thời gian + lệch tâm | +0.012 [+0.007, +0.018] | -0.007 [-0.015, +0.007] |
| 3 | đổi tư thế (đi) | thời gian + lệch tâm + kích thước chạm | -0.011 [-0.020, -0.003] | -0.018 [-0.031, -0.004] |
| 5 | đổi tư thế (đi) | thời gian | -0.006 [-0.014, +0.002] | -0.074 [-0.100, -0.051] |
| 5 | đổi tư thế (đi) | thời gian + lệch tâm | +0.009 [+0.003, +0.016] | -0.003 [-0.015, +0.009] |
| 5 | đổi tư thế (đi) | thời gian + lệch tâm + kích thước chạm | -0.012 [-0.024, -0.002] | -0.012 [-0.027, -0.000] |
