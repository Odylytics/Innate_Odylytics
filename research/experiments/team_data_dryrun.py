"""THỬ ĐƯỜNG ỐNG THU DỮ LIỆU bằng dữ liệu GIẢ (không có ý nghĩa khoa học): backend local -> phiên có `meta` -> /v1/export -> team_analysis.py -> train_human_model.py.

Mục đích: bắt lỗi của đường ống TRƯỚC khi có dữ liệu thật. KHÔNG dùng số in ra làm kết quả.
Cần: fastapi, uvicorn, sqlalchemy, httpx, lightgbm, scikit-learn, numpy (research/ dùng sklearn; không có trong nhóm `ml` của backend). Ví dụ môi trường backend + `uv pip install scikit-learn`; (vd. môi trường của backend: `uv run --extra ml python ../research/experiments/team_data_dryrun.py` trong backend/).
Tạo ở thư mục tạm; không đụng backend/app/models.
"""
import json
import os
import random
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(ROOT / "attacker")]
from nhip_attacker import tactics  # noqa: E402
from tests.synth import Persona, human_session  # noqa: E402
from tests.synth_vi import type_phrase  # noqa: E402

PORT, N_P = 8765, 12
tmp = Path(tempfile.mkdtemp(prefix="innate_dryrun_"))
env = {**os.environ, "DATABASE_URL": f"sqlite:///{tmp}/x.db", "NHIP_API_KEYS": "sdk", "NHIP_ML_KEYS": "ml"}
srv = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--port", str(PORT), "--log-level", "warning"],
                       cwd=ROOT / "backend", env=env)
base, H, HML = f"http://127.0.0.1:{PORT}", {"X-API-Key": "sdk"}, {"X-API-Key": "ml"}
try:
    for _ in range(60):
        try:
            if httpx.get(base + "/health", timeout=1).status_code == 200:
                break
        except httpx.HTTPError:
            time.sleep(0.5)
    else:
        sys.exit("backend không lên")
    c = httpx.Client(base_url=base, headers=H, timeout=20)
    rng = random.Random(1)
    persona = {f"p{i:02d}": Persona(rng.gauss(95, 20), rng.gauss(200, 50), rng.gauss(0, .15), rng.gauss(0, .15), rng.gauss(2, .5), rng.gauss(15, 10)) for i in range(N_P)}
    late = {p: rng.random() for p in persona}  # thói quen đặt dấu thanh GIẢ

    def post(user, who, sitting, role, enrol=False, tactic=None, session=None):
        s = session or human_session(user, persona[who], rng)
        if role != "bot":
            ch = c.get("/v1/challenge").json()
            ev = type_phrase(ch["phrase"], "telex", late[who])
            ev = [{**e, "t": int(e["t"] * rng.gauss(1, 0.08))} for e in ev]
            s["fields"] = [{"name": "challenge", "token": ch["token"], "events": ev}]
        s["meta"] = {"participant_id": who if role != "bot" else "sim", "sitting": sitting, "role": role, **({"tactic": tactic} if tactic else {}), "note": "dryrun"}
        r = c.post("/v1/sessions", json=s); r.raise_for_status()
        sid = r.json()["session_id"]
        if enrol:
            c.post(f"/v1/users/{user}/enroll", json={"session_id": sid}).raise_for_status()

    for p in persona:
        for i in range(8):
            post(p, p, 1, "genuine", enrol=i < 3)
        for _ in range(5):
            post(p, p, 2, "genuine")
    ps = list(persona)
    for i, p in enumerate(ps):
        for _ in range(5):
            post(ps[(i + 1) % N_P], p, 1, "impostor")
    humans = [human_session("x", persona[p], rng) for p in ps for _ in range(3)]
    for t in (1, 2, 3, 4):
        for _ in range(10):
            post(ps[0], "sim", 1, "bot", tactic=t, session=tactics.generate(t, ps[0], "1593", humans, rng))
    # export theo trang
    out, off = [], 0
    while True:
        r = httpx.get(base + "/v1/export", headers=HML, params={"limit": 200, "offset": off}, timeout=30); r.raise_for_status()
        out += r.json()
        if "x-next-offset" not in r.headers:
            break
        off = int(r.headers["x-next-offset"])
    exp = tmp / "export.jsonl"
    exp.write_text("\n".join(json.dumps(x) for x in out), encoding="utf-8")
    print(f"export: {len(out)} phiên -> {exp}")
finally:
    srv.terminate()
py = sys.executable
print("== team_analysis.py ==")
subprocess.run([py, str(ROOT / "research/experiments/team_analysis.py"), str(exp), "--out", str(tmp / "report.md"), "--boot", "50"], check=True)
print("== train_human_model.py (đầu ra vào thư mục tạm, KHÔNG đụng backend/app/models) ==")
subprocess.run([py, str(ROOT / "research/experiments/train_human_model.py"), "--export", str(exp), "--out", str(tmp / "models"), "--no-strokepin", "--no-generated"], check=True)
print("\nXONG. Thư mục tạm:", tmp, "(số liệu trên là GIẢ)")
