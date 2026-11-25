"""Mô hình 2 bản 1: so với mẫu chuẩn bằng scaled Manhattan (Killourhy & Maxion 2009)."""

import json
import math
import os
from pathlib import Path
from statistics import fmean, stdev, variance

# Sàn độ lệch chuẩn: 3–5 lượt đăng ký cho sd rất nhiễu, sàn giữ một đặc trưng "quá ổn định" không chi phối điểm.
_SD_FLOOR = {"pin_hold": 15.0, "pin_flight": 25.0, "pin_total": 80.0, "pin_dx": 0.05, "pin_dy": 0.05}

ALPHA = 0.1  # tốc độ cập nhật mẫu chuẩn
DRIFT_CAP = 1.0  # mẫu chuẩn không được trôi quá 1 sd so với lúc đăng ký (chống "dạy dần")


def is_identity_feature(k: str) -> bool:
    # swipe_*: E19 (Touchalytics) cho AUC ~0.5 khi nhận chủ bằng 5 đặc trưng vuốt (kể cả cùng ngày, cùng tác vụ): chỉ thêm nhiễu
    return not k.startswith(("screen_", "swipe_", "vi_")) and k not in (
        "tap_w_std", "fld_set_text_frac", "fld_amount_set_text",
        "fld_challenge_set_text", "fld_challenge_paste", "fld_challenge_token_bad")


def _floor(k: str, mu: float) -> float:
    base = next((v for p, v in _SD_FLOOR.items() if k.startswith(p)), 0.0)
    return max(base, 0.1 * abs(mu), 1e-6)


def _load_prior() -> dict:
    """Phương sai trong-người của dân số cho đặc trưng THỜI GIAN (research/experiments/make_population_prior.py)."""
    try:
        if os.environ.get("NHIP_POP_PRIOR", "on") == "off":
            return {}
        return json.loads((Path(__file__).parent / "population_prior.json").read_text(encoding="utf-8"))
    except Exception:  # thiếu file: dùng sd có sàn như trước
        return {}


_PRIOR = _load_prior()


def _sd(k: str, xs: list[float], mu: float, prior_var: dict[str, float]) -> float:
    """Co rút (E2/E10): với đặc trưng thời gian có prior, kéo phương sai ước lượng từ vài mẫu về phương sai dân số.
    Đặc trưng khác (lệch tâm...) giữ sd có sàn: co rút cho lệch tâm làm tệ hơn (E10).
    """
    pv = prior_var.get(k)
    if pv is None or len(xs) < 2:
        return max(stdev(xs), _floor(k, mu))
    nu, n = _PRIOR.get("nu", 5), len(xs)
    return math.sqrt(((n - 1) * variance(xs) + nu * pv) / (n - 1 + nu))


def build_template(feature_list: list[dict[str, float]]) -> dict:
    keys = set.intersection(*({k for k in f if is_identity_feature(k)} for f in feature_list))
    mu = {k: fmean(f[k] for f in feature_list) for k in keys}
    prior_var = dict(_PRIOR.get("within_var", {}))
    # tổng thời gian nhập phụ thuộc độ dài PIN: chỉ dùng prior khi PIN có đúng số phím của dữ liệu nguồn
    n = _PRIOR.get("n_taps", 6)
    if f"pin_hold_{n - 1}" not in keys or f"pin_hold_{n}" in keys:
        prior_var.pop("pin_total", None)
    sd = {k: _sd(k, [f[k] for f in feature_list], mu[k], prior_var) for k in keys}
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
    return 1 / (1 + math.exp(min(2 * (d - 2), 700.0))), z  # chặn tràn số khi phiên lệch rất xa (trước đây OverflowError => 500)


def update(tpl: dict, features: dict[str, float]) -> dict:
    mu = dict(tpl["mu"])
    for k in mu:
        if k in features:
            moved = mu[k] + ALPHA * (features[k] - mu[k])
            lo = tpl["mu0"][k] - DRIFT_CAP * tpl["sd"][k]
            hi = tpl["mu0"][k] + DRIFT_CAP * tpl["sd"][k]
            mu[k] = min(max(moved, lo), hi)
    return {**tpl, "mu": mu, "updates": tpl["updates"] + 1}
