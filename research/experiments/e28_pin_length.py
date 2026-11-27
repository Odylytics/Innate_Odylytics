"""E28: PIN 4 số (như web demo, PIN 1593) hay 6 số (dữ liệu huấn luyện)? Quyết định `allow/step_up/hold` của chủ và kẻ biết PIN.

Mô hình học nhận chủ được huấn luyện trên PIN 6 số và chỉ chạy khi đủ 6 phím (`owner_model.predict` trả None nếu thiếu đặc trưng), nên với PIN 4 số backend rơi về điểm khoảng cách của `owner.py`.
Mô phỏng PIN 4 số bằng cách CẮT 4 lần chạm đầu của phiên StrokePIN (PIN 6 số thật): chỉ là xấp xỉ (người gõ PIN 4 số thật có thể khác), nhưng cho thấy hướng.
Cùng 10 người chưa từng thấy bởi cả hai mô hình học và cùng giao thức E24 (người nhận quen). Kẻ biết PIN dùng MÁY KHÁC (lẫn nhiễu thiết bị).
Chạy: python research/experiments/e28_pin_length.py
"""
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(Path(__file__).parent)]
from app.scoring import features, fusion, human, human_model, owner, owner_model, replay  # noqa: E402
import strokepin_loader  # noqa: E402

rng = random.Random(0)
S = strokepin_loader.load()
USERS = sorted({e["user"] for e in S})
a = USERS[:]; random.Random(7).shuffle(a); b = USERS[:]; random.Random(21).shuffle(b)
EVAL = sorted(set(a[62:]) & set(b[68:]))


def trunc(sess, k):
    return {**sess, "pin_taps": sess["pin_taps"][:k]}


def decide(raw, tpl, hist):
    f = features.extract(raw)
    h, br = human.score(f)
    p = human_model.predict(raw)
    if p is not None:
        h = p if br == ["insufficient_data"] else min(h, p)
    if replay.is_replay(f, hist[-50:]):
        h = min(h, 0.1)
    o, z = owner.score(f, tpl)
    used_model = False
    if o:
        m = owner_model.predict(z)
        used_model = m is not None
        o = o if m is None else m
    return fusion.fuse(h, o, False, 0.0)[1], used_model


out = ["# E28 — PIN 4 số (demo) và PIN 6 số: quyết định của hệ thống", "",
       "10 người chưa từng thấy bởi cả hai mô hình học; PIN 4 số mô phỏng bằng cách cắt 4 lần chạm đầu của PIN 6 số thật (xấp xỉ). Người nhận quen. Kẻ biết PIN dùng máy khác.", "",
       "| PIN | mô hình học chủ chạy? | chủ: allow / step_up / hold | kẻ biết PIN: allow / step_up / hold |", "|---|---|---|---|"]
for k in (6, 4):
    res = {"chủ": [], "kẻ": []}; used = []
    by = defaultdict(list); by_pin = defaultdict(list)
    for e in S:
        by[(e["user"], e["pin"])].append(e); by_pin[e["pin"]].append(e)
    for (u, pin), ents in by.items():
        if u not in EVAL or len(ents) < 5:
            continue
        es = ents[:]; rng.shuffle(es)
        enr, tests = es[:3], es[3:]
        feats_ = [features.extract(trunc(e["session"], k)) for e in enr]
        tpl = owner.build_template(feats_)
        hist = list(feats_)
        for e in tests:
            act, um = decide(trunc(e["session"], k), tpl, hist); res["chủ"].append(act); used.append(um)
            hist.append(features.extract(trunc(e["session"], k)))
        others = [e for e in by_pin[pin] if e["user"] != u]
        for e in rng.sample(others, min(4, len(others))):
            res["kẻ"].append(decide(trunc({**e["session"], "user_id": u}, k), tpl, hist)[0])
    pc = lambda L, x: f"{100 * np.mean([a == x for a in L]):.0f}%"  # noqa: E731
    row = lambda L: " / ".join(pc(L, x) for x in ("allow", "step_up", "hold"))  # noqa: E731
    out.append(f"| {k} số | {'có' if np.mean(used) > 0.5 else 'KHÔNG (rơi về khoảng cách)'} | {row(res['chủ'])} | {row(res['kẻ'])} |")
    print(out[-1], flush=True)
(ROOT / "research/results/e28_pin_length.md").write_text("\n".join(out) + "\n", encoding="utf-8")
