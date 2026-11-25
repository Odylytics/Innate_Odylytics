# E21 — chuẩn hoá nhịp gõ theo cặp phím, nhận chủ khi câu thử khác câu đăng ký (Aalto, người thật)

Giao thức E13: đăng ký 3 câu, thử các câu khác, kẻ gian = câu của người khác; prior cặp phím và phương sai từ nhóm người riêng. EER và FAR@FRR5%, khoảng tin cậy bootstrap theo người.

| Đặc trưng | n phím | EER | FAR @ FRR 5% |
|---|---|---|---|
| E13 thô (6 đặc trưng log khoảng cách) | 10 | 0.335 [0.326, 0.341] | 0.737 [0.708, 0.758] |
| E13 thô (6 đặc trưng log khoảng cách) | 20 | 0.281 [0.273, 0.290] | 0.594 [0.572, 0.616] |
| E13 thô (6 đặc trưng log khoảng cách) | 30 | 0.249 [0.243, 0.259] | 0.498 [0.473, 0.524] |
| chuẩn hoá theo cặp phím (6 đặc trưng z) | 10 | 0.332 [0.325, 0.340] | 0.705 [0.692, 0.726] |
| chuẩn hoá theo cặp phím (6 đặc trưng z) | 20 | 0.280 [0.272, 0.288] | 0.601 [0.577, 0.622] |
| chuẩn hoá theo cặp phím (6 đặc trưng z) | 30 | 0.245 [0.236, 0.253] | 0.479 [0.456, 0.501] |
| chỉ tốc độ chung (mean z, 1 đặc trưng) | 10 | 0.344 [0.337, 0.352] | 0.683 [0.664, 0.704] |
| chỉ tốc độ chung (mean z, 1 đặc trưng) | 20 | 0.301 [0.291, 0.310] | 0.574 [0.553, 0.592] |
| chỉ tốc độ chung (mean z, 1 đặc trưng) | 30 | 0.266 [0.259, 0.274] | 0.487 [0.472, 0.504] |
| thô + chuẩn hoá (12 đặc trưng) | 10 | 0.326 [0.318, 0.332] | 0.730 [0.699, 0.744] |
| thô + chuẩn hoá (12 đặc trưng) | 20 | 0.274 [0.266, 0.283] | 0.572 [0.552, 0.596] |
| thô + chuẩn hoá (12 đặc trưng) | 30 | 0.238 [0.228, 0.245] | 0.467 [0.446, 0.489] |
