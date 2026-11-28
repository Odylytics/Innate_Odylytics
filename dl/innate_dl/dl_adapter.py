"""Runtime of the 4-layer DL model (Innate4LayerNet) in pure NumPy: no torch, no libgomp. RESEARCH CODE (dl/), not used by the product.

Bundle = `manifest.json` + `weights.npz`, produced by `dl/export/to_numpy.py` (the PyTorch model lives in
`dl/models/innate4.py`; `dl/export/verify_parity.py` checks both agree within 1e-5).
This file is the SINGLE SOURCE of the input preprocessing (`seq_tensor`, `ctx_vector`, `tab_vector`): training imports it.

Env vars: NHIP_DL_BUNDLE (bundle dir), NHIP_OWNER_BACKEND / NHIP_HUMAN_BACKEND (`lgbm` default | `dl`),
NHIP_DL_SHADOW (`1`: score with the DL bundle and log it in TouchSession.result["shadow"] without using it).
Any failure (no numpy, no bundle, bad file, missing features) => `predict` returns None and the caller keeps the
lgbm/rule path.
"""

import datetime as dt
import json
import math
import os
from pathlib import Path

try:
    import numpy as np
except ImportError:  # numpy is optional at import time: the lgbm/rule path must keep working without it
    np = None

from app.scoring import bot_features  # the product module (read only); the backend must be on sys.path

# ---- architecture constants (must match training/models/innate4.py) ----
L_MAX, N_CHAN, N_CONT, G = 12, 10, 9, 20
E_DIM, U_DIM, N_CTX, N_BURST = 64, 32, 14, 6
BURST_IDX = (2, 3, 4, 6, 7, 8)  # h_ctx entries describing bursts/retries (attempt index, 10m/1h counts, flagged, retries, dt_prev)
RANGES = ((0, .4), (0, 1.5), (0, 1.5), (-.2, 1.5), (0, 2.5), (-.2, 2.5), (-1, 1), (-1, 1), (0, 4))  # GRE range per continuous channel
N_HEADS, ANCHOR_M, K_MAX = 4, 3, 10
F_NAMES = [n for n in bot_features.FEATURE_NAMES if n not in bot_features.CONTACT_FEATURES]
CHANNELS = ("hold_s", "pp_s", "rr_s", "rp_s", "pp2_s", "rp2_s", "dx_norm", "dy_norm", "jump_dist", "mask")


# ---- preprocessing (shared with training) ----
def seq_tensor(raw: dict) -> "np.ndarray":
    """PIN taps -> (L_MAX, 10) float32: hold, press-press, release-release, release-press, the two lag-2 variants,
    key offset dx/dy (key units), jump distance between key centres, mask. Time in seconds. No w/h/pressure."""
    taps = sorted(raw.get("pin_taps", []), key=lambda t: t["t_down"])[:L_MAX]
    x = np.zeros((L_MAX, N_CHAN), dtype=np.float32)
    for i, t in enumerate(taps):
        x[i, 0] = (t["t_up"] - t["t_down"]) / 1000
        if i >= 1:
            p = taps[i - 1]
            x[i, 1] = (t["t_down"] - p["t_down"]) / 1000
            x[i, 2] = (t["t_up"] - p["t_up"]) / 1000
            x[i, 3] = (t["t_down"] - p["t_up"]) / 1000
            x[i, 8] = math.hypot((t["key_cx"] - p["key_cx"]) / t["key_w"], (t["key_cy"] - p["key_cy"]) / t["key_h"])
        if i >= 2:
            q = taps[i - 2]
            x[i, 4] = (t["t_down"] - q["t_down"]) / 1000
            x[i, 5] = (t["t_down"] - q["t_up"]) / 1000
        x[i, 6] = (t["x"] - t["key_cx"]) / t["key_w"]
        x[i, 7] = (t["y"] - t["key_cy"]) / t["key_h"]
        x[i, 9] = 1.0
    return x


def ctx_vector(h: dict | None) -> "np.ndarray":
    """HistoryContext (history.compute) -> 14 floats: counts as log1p, gaps as log1p(seconds), unknown -> 0 (same_device -> 0.5)."""
    h = h or {}
    v = lambda k: h.get(k) or 0  # noqa: E731
    lg = lambda k: math.log1p(max(float(v(k)), 0.0))  # noqa: E731
    same = h.get("same_device_as_enroll")
    return np.array([lg("n_enroll"), lg("n_sessions_total"), lg("attempt_index_in_sitting"), lg("n_attempts_10m"),
                     lg("n_attempts_1h"), lg("n_attempts_24h"), lg("n_recent_flagged"), lg("client_retries"),
                     lg("dt_prev_session_sec"), lg("dt_last_enroll_sec"), lg("dt_mean_recent_sec"),
                     min(max(float(v("dt_cv_recent")), 0.0), 5.0), 0.5 if same is None else float(same),
                     lg("n_distinct_devices")], dtype=np.float32)


def tab_vector(raw: dict, mean: "np.ndarray", std: "np.ndarray") -> "np.ndarray":
    """bot_features of the session, standardised with the training statistics; NaN -> 0, clipped to [-5, 5]."""
    f = bot_features.extract(raw)
    x = (np.array([f[n] for n in F_NAMES], dtype=np.float64) - mean) / std
    return np.clip(np.nan_to_num(x, nan=0.0), -5, 5).astype(np.float32)


# ---- NumPy forward (mirror of training/models/innate4.py) ----
_Z, _NEG = np.float64(0), np.float64(-1e9)
_sig = lambda x: 1 / (1 + np.exp(-x))  # noqa: E731


def _ln(x, w, b, eps=1e-5):
    m = x.mean(-1, keepdims=True)
    return (x - m) / np.sqrt(x.var(-1, keepdims=True) + eps) * w + b


def _lin(x, W, name):
    return x @ W[name + ".weight"].T + W[name + ".bias"]


def _gru(x, m, W, p, reverse):
    """Masked GRU over time (B,L,in): padded steps keep the state, so the backward pass starts at the last real tap."""
    wi, wh, bi, bh = (W[f"{p}.{n}"] for n in ("weight_ih", "weight_hh", "bias_ih", "bias_hh"))
    B, L, _ = x.shape
    H = wh.shape[1]
    h, out = np.zeros((B, H)), np.zeros((B, L, H))
    for t in (range(L - 1, -1, -1) if reverse else range(L)):
        gi, gh = x[:, t] @ wi.T + bi, h @ wh.T + bh
        r, z = _sig(gi[:, :H] + gh[:, :H]), _sig(gi[:, H:2 * H] + gh[:, H:2 * H])
        n = np.tanh(gi[:, 2 * H:] + r * gh[:, 2 * H:])
        new = (1 - z) * n + z * h
        mt = m[:, t, None]
        h = mt * new + (1 - mt) * h
        out[:, t] = h * mt
    return out


def encode(W: dict, x: "np.ndarray") -> tuple["np.ndarray", "np.ndarray"]:
    """(B, L_MAX, 10) -> e (B,64) L2-normalised identity embedding, u (B,32) naturalness vector. Layers 1 and 2."""
    x = x.astype(np.float64)  # float64 runtime: tiny model, and it matches PyTorch's float64 forward to ~1e-12
    m = x[..., 9]
    lo, hi = (np.array(c, dtype=np.float64) for c in zip(*RANGES))
    sig = (hi - lo) / G
    centers = lo[:, None] + (hi - lo)[:, None] * (np.arange(G, dtype=np.float64) + 0.5) / G
    gre = np.exp(-0.5 * ((x[..., :N_CONT, None] - centers) / sig[:, None]) ** 2).reshape(*x.shape[:2], -1) * m[..., None]
    B, L, _ = gre.shape
    outs = []
    for k in (1, 3, 5):  # multi-scale masked Conv1D
        w, pad = W[f"conv{k}.weight"], k // 2
        xp = np.pad(gre, ((0, 0), (pad, pad), (0, 0)))
        outs.append(sum(xp[:, j:j + L] @ w[:, :, j].T for j in range(k)) + W[f"conv{k}.bias"])
    h = np.maximum(np.concatenate(outs, -1), 0) * m[..., None]
    h = _ln(_lin(h, W, "proj"), W["ln1.weight"], W["ln1.bias"]) * m[..., None]
    f = _gru(h, m, W, "gru_f", False)
    b = _gru(h, m, W, "gru_b", True)
    h = np.concatenate([f, b], -1)  # BiGRU
    d = h.shape[-1]
    q, k_, v = (_lin(h, W, n).reshape(B, L, N_HEADS, d // N_HEADS).transpose(0, 2, 1, 3) for n in ("wq", "wk", "wv"))
    s = q @ k_.transpose(0, 1, 3, 2) / math.sqrt(d // N_HEADS) + np.where(m[:, None, None, :] > 0, _Z, _NEG)
    a = np.exp(s - s.max(-1, keepdims=True))
    a /= a.sum(-1, keepdims=True)
    h = _ln(h + _lin((a @ v).transpose(0, 2, 1, 3).reshape(B, L, d), W, "wo"), W["ln2.weight"], W["ln2.bias"]) * m[..., None]
    sc = _lin(np.tanh(_lin(h, W, "att1")), W, "att2")[..., 0] + np.where(m > 0, _Z, _NEG)  # attentive statistics pooling
    al = np.exp(sc - sc.max(-1, keepdims=True))
    al /= al.sum(-1, keepdims=True)
    mu = (al[..., None] * h).sum(1)
    sd = np.sqrt(np.maximum((al[..., None] * h * h).sum(1) - mu * mu, 0) + 1e-6)
    pooled = np.concatenate([mu, sd], -1)
    e = _lin(pooled, W, "e_head")
    return e / np.maximum(np.linalg.norm(e, axis=-1, keepdims=True), 1e-8), _lin(pooled, W, "u_head")


def match(W: dict, e_q, gal_e, gal_dt_h, gal_mask):
    """Layer 3. e_q (B,64); gal_e (B,K,64) in enrolment order; gal_dt_h (B,K) hours since each enrolment; gal_mask (B,K).
    -> v_match (B,8): cos to mu_0, cos to mu_decay, max/mean/min/std of cos to the gallery, drift_cos, drift_mag."""
    eps = 1e-8
    k = gal_mask.sum(1)
    nrm = lambda a: a / np.maximum(np.linalg.norm(a, axis=-1, keepdims=True), eps)  # noqa: E731
    first = (np.cumsum(gal_mask, 1) <= ANCHOR_M) * gal_mask  # hybrid anchor: the first ANCHOR_M enrolments
    mu0 = nrm((gal_e * first[..., None]).sum(1) / np.maximum(first.sum(1, keepdims=True), 1))
    cos = (gal_e * e_q[:, None]).sum(-1)
    sp = lambda x: np.log1p(np.exp(-abs(x))) + np.maximum(x, 0)  # noqa: E731
    temp = sp(W["att_c"][0] + W["att_c"][1] * np.log1p(k))
    logit = np.where(gal_mask > 0, temp[:, None] * cos + W["att_t"][0] * np.log1p(np.maximum(gal_dt_h, 0)), _NEG)
    al = np.exp(logit - logit.max(1, keepdims=True))
    al /= al.sum(1, keepdims=True)
    mud = nrm((al[..., None] * gal_e).sum(1))  # time-decayed prototype
    n = np.maximum(k, 1)
    cm = (cos * gal_mask).sum(1) / n
    std = np.sqrt(np.maximum((((cos - cm[:, None]) * gal_mask) ** 2).sum(1) / n, 0) + 1e-8)
    dv, qv = mud - mu0, e_q - mu0
    drift_cos = (dv * qv).sum(-1) / (np.linalg.norm(dv, axis=-1) * np.linalg.norm(qv, axis=-1) + eps)
    return np.stack([(e_q * mu0).sum(-1), (e_q * mud).sum(-1), np.where(gal_mask > 0, cos, np.float64(-9)).max(1), cm,
                     np.where(gal_mask > 0, cos, np.float64(9)).min(1), std, drift_cos, np.linalg.norm(dv, axis=-1)], -1)


def _mlp(x, W, p):
    return (np.maximum(_lin(x, W, p + "1"), 0) @ W[p + "2.weight"].T + W[p + "2.bias"])[..., 0]


def owner_logit(W, v, k, dt_last_h):
    """Layer 4, owner stream. v (B,8), k (B,), dt_last_h (B,) -> logit of P(owner)."""
    return _mlp(np.concatenate([v, np.log1p(k)[:, None], np.log1p(np.maximum(dt_last_h, 0))[:, None]], -1), W, "own")


def human_logit(W, u, f_tab, h_ctx):
    """Layer 4, human stream: u_q + f_tab + h_burst -> logit of P(human)."""
    return _mlp(np.concatenate([u, f_tab, h_ctx[:, list(BURST_IDX)]], -1), W, "hum")


# ---- bundle + public API ----
class Bundle:
    def __init__(self, path: Path):
        self.manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
        z = np.load(path / "weights.npz")
        self.W = {k: z[k].astype(np.float64) for k in z.files}
        self.f_mean, self.f_std = self.W.pop("f_mean"), self.W.pop("f_std")
        if self.manifest["f_names"] != F_NAMES:
            raise ValueError("bundle f_names differ from bot_features")


_state: dict = {}


def bundle_dir() -> Path:
    return Path(os.environ.get("NHIP_DL_BUNDLE", Path(__file__).parent.parent / "models" / "dl"))


def load() -> "Bundle | None":
    """Cached bundle, or None if numpy/bundle is missing or broken (never raises)."""
    key = str(bundle_dir())
    if _state.get("key") != key:
        try:
            _state.update(key=key, b=Bundle(bundle_dir()) if np is not None else None)
        except Exception:
            _state.update(key=key, b=None)
    return _state["b"]


def reset() -> None:
    _state.clear()


def owner_backend() -> str:
    return os.environ.get("NHIP_OWNER_BACKEND", "lgbm")


def human_backend() -> str:
    return os.environ.get("NHIP_HUMAN_BACKEND", "lgbm")


def shadow() -> bool:
    return os.environ.get("NHIP_DL_SHADOW", "0") == "1"


def wanted() -> bool:
    return shadow() or "dl" in (owner_backend(), human_backend())


def status() -> dict:
    b = load()
    return {"bundle": b is not None, "version": b.manifest.get("version") if b else None, "owner_backend": owner_backend(),
            "human_backend": human_backend(), "shadow": shadow()}


def _calibrate(p: float, thr: float) -> float:
    """Probability -> score in [0,1] with the FRR-5% threshold mapped to 0.5 (same convention as human_model/owner_model)."""
    thr = min(max(thr, 1e-6), 1 - 1e-6)
    return 0.5 * p / thr if p < thr else 0.5 + 0.5 * (p - thr) / (1 - thr)


def tau(manifest: dict, k: int, dt_last_h: float) -> float:
    """Dynamic owner threshold tau(k, dt): k bucket 2,3,4,5+ and a coarse dt bucket (<=1 h / >1 h), falling back to the k bucket."""
    t = manifest["owner"]["tau"][str(min(max(k, 2), 5))]
    return t["le1h" if dt_last_h <= 1 else "gt1h"] or t["all"]


def _t(x) -> float:
    return x.timestamp() if isinstance(x, dt.datetime) else float(x)


def predict(raw: dict, hist: dict | None, gallery: list[tuple[dict, float]], t_query: "dt.datetime | float") -> dict | None:
    """Score one session. gallery = [(raw, created_at)] of the user's enrolment sessions (oldest first).
    -> {"human": score|None, "owner": score|None, "k": int, "human_p", "owner_p", "tau"} or None when there is no usable bundle."""
    b = load()
    if b is None or not raw.get("pin_taps"):
        return None
    try:
        W, tq = b.W, _t(t_query)
        x = seq_tensor(raw)[None]
        _, u = encode(W, x)
        out = {"human": None, "owner": None, "k": len(gallery)}
        p_h = float(_sig(human_logit(W, u, tab_vector(raw, b.f_mean, b.f_std)[None], ctx_vector(hist)[None])[0]))
        out.update(human_p=round(p_h, 4), human=_calibrate(p_h, b.manifest["human"]["threshold"]))
        gallery = [g for g in gallery if g[0].get("pin_taps")][-K_MAX:]
        if len(gallery) >= 2:
            e_q = encode(W, x)[0]
            ge = encode(W, np.stack([seq_tensor(g) for g, _ in gallery]))[0]
            dts = np.array([max(tq - _t(t), 0) / 3600 for _, t in gallery], dtype=np.float32)
            k, dl = len(gallery), float(dts.min())
            v = match(W, e_q, ge[None], dts[None], np.ones((1, k), dtype=np.float32))
            p_o = float(_sig(owner_logit(W, v, np.array([k], dtype=np.float32), np.array([dl], dtype=np.float32))[0]))
            th = tau(b.manifest, k, dl)
            out.update(owner_p=round(p_o, 4), owner=_calibrate(p_o, th), tau=th, k=k, dt_last_h=round(dl, 3))
        return out
    except Exception:
        return None
