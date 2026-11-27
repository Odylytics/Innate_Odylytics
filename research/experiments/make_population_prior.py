"""Sinh backend/app/scoring/population_prior.json từ StrokePIN: phương sai TRONG-người của các đặc trưng thời gian.

Với mỗi (người, PIN) có >= 2 lượt: phương sai từng đặc trưng; prior = trung bình trên mọi nhóm.
Dùng cho co rút trong owner.build_template (E2/E10): CHỈ thời gian; lệch tâm giữ sd có sàn vì độ dao động
lệch tâm khác nhau quá nhiều giữa người/thiết bị (E10: co rút cho lệch tâm làm tệ hơn).
Prior là thống kê tổng hợp từ dữ liệu CC BY-NC-SA 4.0 (ghi nguồn trong file).
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(Path(__file__).parent)]
from app.scoring import features  # noqa: E402
import strokepin_loader  # noqa: E402

S = strokepin_loader.load()
grp = defaultdict(list)
for e in S:
    grp[(e["user"], e["pin"])].append(features.extract(e["session"]))
keys = sorted(k for k in S and features.extract(S[0]["session"]) if k.startswith(("pin_hold_", "pin_flight_")) or k == "pin_total")
vs = [np.var(np.array([[f[k] for k in keys] for f in fs]), axis=0, ddof=1) for fs in grp.values() if len(fs) >= 2]
prior = dict(zip(keys, np.mean(vs, axis=0).round(2).tolist()))
out = {"within_var": prior, "n_taps": 6, "nu": 5,
       "source": "StrokePIN (Yao & Wang 2026, CC BY-NC-SA 4.0), 97 người, PIN 6 số; thống kê tổng hợp trên mọi PIN",
       "n_groups": len(vs), "note": "pin_total chỉ dùng khi PIN có đúng 6 phím"}
(ROOT / "backend/app/scoring/population_prior.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: round(v ** 0.5, 1) for k, v in prior.items()}, indent=1), len(vs), "nhóm")
