# E26 — local API latency

300 rounds (submit a session, then score it), enrolled account, growing history; human/bot model: True, owner model: True. TestClient, SQLite, single process, development machine; does NOT include network, Vercel cold start, Neon.

| Command | p50 | p95 | p99 | max |
|---|---|---|---|---|
| POST /v1/sessions | 2.1 ms | 3.2 ms | 8.7 ms | 15.9 ms |
| POST /v1/sessions/{id}/score | 3.7 ms | 5.2 ms | 14.2 ms | 36.5 ms |
