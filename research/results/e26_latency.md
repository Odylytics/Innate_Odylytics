# E26 — độ trễ API local

300 lượt (gửi phiên rồi chấm điểm), tài khoản đã đăng ký, lịch sử tăng dần; mô hình người/máy: True, mô hình chủ: True. TestClient, SQLite, một tiến trình, máy phát triển; KHÔNG gồm mạng, khởi động nguội Vercel, Neon.

| Lệnh | p50 | p95 | p99 | max |
|---|---|---|---|---|
| POST /v1/sessions | 2.2 ms | 2.9 ms | 4.3 ms | 6.1 ms |
| POST /v1/sessions/{id}/score | 3.8 ms | 4.7 ms | 6.2 ms | 1005.3 ms |
