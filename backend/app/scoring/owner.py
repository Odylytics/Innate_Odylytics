"""Mô hình 2 bản 1: so với mẫu chuẩn bằng scaled Manhattan (Killourhy & Maxion 2009)."""

import math
from statistics import fmean, stdev

# Sàn độ lệch chuẩn: 3–5 lượt đăng ký cho sd rất nhiễu, sàn giữ một đặc trưng "quá ổn định" không chi phối điểm.
_SD_FLOOR = {"pin_hold": 15.0, "pin_flight": 25.0, "pin_total": 80.0, "pin_dx": 0.05, "pin_dy": 0.05}

ALPHA = 0.1  # tốc độ cập nhật mẫu chuẩn
DRIFT_CAP = 1.0  # mẫu chuẩn không được trôi quá 1 sd so với lúc đăng ký (chống "dạy dần")


def is_identity_feature(k: str) -> bool:
    return not k.startswith("screen_") and k not in ("swipe_count", "swipe_straight_max", "tap_w_std")


def _floor(k: str, mu: float) -> float:
    base = next((v for p, v in _SD_FLOOR.items() if k.startswith(p)), 0.0)
    return max(base, 0.1 * abs(mu), 1e-6)


def build_template(feature_list: list[dict[str, float]]) -> dict:
    keys = set.intersection(*({k for k in f if is_identity_feature(k)} for f in feature_list))
    mu = {k: fmean(f[k] for f in feature_list) for k in keys}
    sd = {k: max(stdev([f[k] for f in feature_list]), _floor(k, mu[k])) for k in keys}
    return {"mu": mu, "sd": sd, "mu0": dict(mu), "n": len(feature_list), "updates": 0}


def missing_pin_evidence(features: dict[str, float], tpl: dict) -> bool:
    """Phiên thiếu nhịp PIN mà mẫu chuẩn được dựng từ đó (bỏ PIN, PIN khác độ dài)."""
    return any(k.startswith("pin_") and k not in features for k in tpl["mu"])


def score(features: dict[str, float], tpl: dict) -> tuple[float | None, dict[str, float]]:
    z = {k: (features[k] - tpl["mu"][k]) / tpl["sd"][k] for k in tpl["mu"] if k in features}
    if missing_pin_evidence(features, tpl):
        return 0.0, z  # đã đăng ký mà không có bằng chứng PIN: coi là không khớp, không phải "trung tính"
    if not z:
        return None, z
    d = fmean(abs(v) for v in z.values())
    # shortcut: ánh xạ khoảng cách -> [0,1] chưa hiệu chỉnh (d=2 -> 0.5); Người 1 thay bằng ngưỡng fit trên dữ liệu thật
    return 1 / (1 + math.exp(2 * (d - 2))), z


def update(tpl: dict, features: dict[str, float]) -> dict:
    mu = dict(tpl["mu"])
    for k in mu:
        if k in features:
            moved = mu[k] + ALPHA * (features[k] - mu[k])
            lo = tpl["mu0"][k] - DRIFT_CAP * tpl["sd"][k]
            hi = tpl["mu0"][k] + DRIFT_CAP * tpl["sd"][k]
            mu[k] = min(max(moved, lo), hi)
    return {**tpl, "mu": mu, "updates": tpl["updates"] + 1}
