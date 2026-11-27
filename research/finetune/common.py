"""Dùng chung cho fine-tune TypeFormer trên StrokePIN: nạp mô hình (vá CUDA cứng), dựng đặc trưng, đánh giá kiểu E9.

Đặc trưng mỗi phím đúng như TypeFormer/Aalto: [hold, press-press, release-release, release(prev)-press, mã phím/255]
(thời gian đổi ra giây), đệm 0 tới 50 phím. PIN 6 số = 6 hàng thật + 44 hàng đệm.
"""

import random
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
TF = HERE.parent / "external" / "TypeFormer"
PRETRAINED = TF / "pretrained" / "TypeFormer_pretrained.pt"
sys.path[:0] = [str(HERE.parent / "experiments")]

SEQ, DIM = 50, 5


class Cfg:  # = utils/train_config.py của TypeFormer
    sequence_length, dimensionality, output_dim = SEQ, DIM, 64
    K, hlayers, hlayers_rec, hlayers_pos, hheads, vlayers, vheads = 20, 9, 2, 1, 10, 1, 5


def build_model(device, pretrained=True):
    """TypeFormer (HARTrans) float32. Mã gốc gắn cứng .to('cuda'): vá trên bản sao ở finetune/_tf (external/ không đụng)."""
    import torch

    patched = HERE / "_tf"
    if not patched.exists():
        import shutil
        shutil.copytree(TF / "model", patched / "model")
        shutil.copytree(TF / "utils", patched / "utils")
        for f in (patched / "model").glob("*.py"):
            s = f.read_text()
            s = re.sub(r"\.to\('cuda'\)", "", s)
            s = s.replace("torch.float64", "torch.float32")
            s = s.replace('torch.device("cuda:0" if torch.cuda.is_available() else "cpu")', "x.device")
            s = re.sub(r"self\.positions = (torch\.tensor\(.*?\.repeat\(1, K\))\.to\(device\)",
                       r"self.register_buffer('positions', \1, persistent=False)", s)
            f.write_text(s)
    sys.path.insert(0, str(patched))
    from model.Model import HARTrans

    m = HARTrans(Cfg)
    if pretrained:
        m.load_state_dict(torch.load(PRETRAINED, map_location="cpu"))
    return m.float().to(device)


def feats(taps):
    """taps: list dict {key,t_down,t_up} (ms) -> (50,5) float32."""
    p = np.array([t["t_down"] for t in taps]); r = np.array([t["t_up"] for t in taps])
    code = np.array([ord(t["key"]) for t in taps]) / 255
    hold = (r - p) / 1e3
    pp = np.append(0, np.diff(p)) / 1e3
    rr = np.append(0, np.diff(r)) / 1e3
    rp = np.append(0, r[:-1] - p[1:]) / 1e3
    x = np.stack([hold, pp, rr, rp, code], 1).astype(np.float32)
    out = np.zeros((SEQ, DIM), np.float32)
    out[: len(x)] = x[:SEQ]
    return out


def load_sessions():
    import strokepin_loader
    S = strokepin_loader.load()
    for e in S:
        e["x"] = feats(e["session"]["pin_taps"])
    return S


def split_users(users, seed=0, n_val=7, n_test=30):
    u = sorted(users, key=lambda s: int(s[4:]))
    random.Random(seed).shuffle(u)
    return u[n_val + n_test:], u[:n_val], u[n_val: n_val + n_test]


def embed(model, X, device, bs=256):
    import torch
    model.eval()
    out = []
    with torch.no_grad():
        for i in range(0, len(X), bs):
            out.append(model(torch.from_numpy(np.stack(X[i:i + bs])).to(device)).cpu().numpy())
    return np.concatenate(out)


def eer_far(gen, imp, frr=0.05):
    """Khoảng cách thấp = giống chủ. Trả (EER, FAR@FRR=frr)."""
    gen, imp = np.asarray(gen), np.asarray(imp)
    ths = np.sort(np.unique(np.concatenate([gen, imp])))
    frrs = np.array([(gen > t).mean() for t in ths]); fars = np.array([(imp <= t).mean() for t in ths])
    i = np.argmin(np.abs(frrs - fars))
    t = np.quantile(gen, 1 - frr)
    return float((frrs[i] + fars[i]) / 2), float((imp <= t).mean())


def evaluate(model, S, users, device, ks=(3,), n_draw=5, n_imp=20, seed=0):
    """Kiểu E9: mỗi (người, PIN) đăng ký k lượt NGỒI; chủ kiểm thử cùng tư thế (ngồi) hoặc đổi tư thế (đi);
    kẻ gian BIẾT PIN = người khác nhập cùng PIN, cùng tư thế. Điểm = khoảng cách Euclid trung bình tới embedding đăng ký."""
    rng = random.Random(seed)
    uset = set(users)
    E = embed(model, [e["x"] for e in S], device)
    grp = defaultdict(list)
    for i, e in enumerate(S):
        grp[(e["user"], e["pin"], e["posture"])].append(i)
    postures = sorted({e["posture"] for e in S})
    sit = next(p for p in postures if "it" in p.lower() or "sit" in p.lower()) if any("it" in p.lower() for p in postures) else postures[0]
    walk = [p for p in postures if p != sit][0]
    res = {}
    for k in ks:
        gs, gw, imp = [], [], []
        for (u, pin, ps), idx in grp.items():
            if u not in uset or ps != sit or len(idx) <= k:
                continue
            for _ in range(n_draw):
                enr = rng.sample(idx, k)
                te = [j for j in idx if j not in enr]
                en = E[enr]
                d = lambda j: float(np.linalg.norm(en - E[j], axis=1).mean())
                gs += [d(j) for j in te]
                gw += [d(j) for j in grp.get((u, pin, walk), [])]
                others = [j for (u2, p2, q2), js in grp.items() if p2 == pin and u2 != u and u2 in uset and q2 == sit for j in js]
                imp += [d(j) for j in rng.sample(others, min(n_imp, len(others)))]
        res[k] = {"same_posture": eer_far(gs, imp), "walk": eer_far(gw, imp) if gw else None, "n": (len(gs), len(gw), len(imp))}
    return res
