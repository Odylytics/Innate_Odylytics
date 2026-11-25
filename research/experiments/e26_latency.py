"""E26: độ trễ của API chấm điểm khi chạy LOCAL (TestClient, SQLite, một tiến trình). KHÔNG gồm mạng, khởi động nguội Vercel hay độ trễ Neon.

Đo p50/p95/p99 của POST /v1/sessions và POST /v1/sessions/{id}/score cho một tài khoản đã đăng ký (có mô hình học bật).
Chạy: python research/experiments/e26_latency.py   (cần fastapi, httpx, lightgbm, numpy)
"""
import os
import random
import statistics
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parents[2]
os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/lat.db"
os.environ["NHIP_API_KEYS"] = "k"
sys.path[:0] = [str(ROOT / "backend")]
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.scoring import human_model, owner_model  # noqa: E402
from tests.synth import OWNER, human_session  # noqa: E402

H = {"X-API-Key": "k"}
rng = random.Random(0)
with TestClient(app) as c:
    for _ in range(3):
        sid = c.post("/v1/sessions", json=human_session("u", OWNER, rng), headers=H).json()["session_id"]
        c.post("/v1/users/u/enroll", json={"session_id": sid}, headers=H)
    t_post, t_score = [], []
    for _ in range(300):
        s = human_session("u", OWNER, rng)
        t0 = time.perf_counter(); sid = c.post("/v1/sessions", json=s, headers=H).json()["session_id"]; t1 = time.perf_counter()
        r = c.post(f"/v1/sessions/{sid}/score", json={"amount": 500000, "recipient_is_new": False}, headers=H); t2 = time.perf_counter()
        assert r.status_code == 200, r.text
        t_post.append((t1 - t0) * 1e3); t_score.append((t2 - t1) * 1e3)
q = lambda v, p: float(np.percentile(v, p))  # noqa: E731
L = ["# E26 — độ trễ API local", "", f"300 lượt (gửi phiên rồi chấm điểm), tài khoản đã đăng ký, lịch sử tăng dần; mô hình người/máy: {human_model.loaded()}, mô hình chủ: {owner_model.loaded()}. "
     "TestClient, SQLite, một tiến trình, máy phát triển; KHÔNG gồm mạng, khởi động nguội Vercel, Neon.", "",
     "| Lệnh | p50 | p95 | p99 | max |", "|---|---|---|---|---|"]
for name, v in (("POST /v1/sessions", t_post), ("POST /v1/sessions/{id}/score", t_score)):
    L.append(f"| {name} | {q(v, 50):.1f} ms | {q(v, 95):.1f} ms | {q(v, 99):.1f} ms | {max(v):.1f} ms |")
(ROOT / "research/results/e26_latency.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
