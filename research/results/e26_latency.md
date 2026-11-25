# E26 — độ trễ API local

300 lượt (gửi phiên rồi chấm điểm), tài khoản đã đăng ký, lịch sử tăng dần; mô hình người/máy: True, mô hình chủ: True. TestClient, SQLite, một tiến trình, máy phát triển; KHÔNG gồm mạng, khởi động nguội Vercel, Neon.

| Lệnh | p50 | p95 | p99 | max |
|---|---|---|---|---|
| POST /v1/sessions | 2.1 ms | 3.2 ms | 8.7 ms | 15.9 ms |
| POST /v1/sessions/{id}/score | 3.7 ms | 5.2 ms | 14.2 ms | 36.5 ms |
