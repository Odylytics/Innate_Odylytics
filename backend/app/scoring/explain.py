"""Lớp giải thích: mã lý do + câu tiếng Việt theo mẫu (không dùng LLM trên đường quyết định)."""

from statistics import fmean

from . import owner as owner_model

_BOT_VI = {
    "timing_too_regular": "nhịp bấm đều bất thường",
    "tap_exact_center": "chạm đúng tâm nút",
    "swipe_perfectly_straight": "vuốt thẳng tuyệt đối",
}
_ACTION_VI = {
    "allow": "Cho phép giao dịch.",
    "step_up": "Đề nghị xác thực khuôn mặt trước khi chuyển.",
    "hold": "Đề nghị tạm giữ lệnh và báo cho người dùng.",
}
Z_MIN = 1.5  # nhóm đặc trưng lệch ít hơn mức này không được nêu làm lý do


def _owner_reasons(features: dict, tpl: dict, z: dict) -> list[tuple[float, str, str]]:
    """-> [(độ lệch, mã, câu tiếng Việt)] theo nhóm đặc trưng."""
    out = []

    def keys(*prefixes):
        return [k for k in z if k.startswith(prefixes)]

    rhythm = keys("pin_hold_", "pin_flight_", "pin_total")
    if rhythm:
        pct = round(100 * (sum(features[k] for k in rhythm) / sum(tpl["mu"][k] for k in rhythm) - 1))
        word, code = ("chậm", "slower") if pct > 0 else ("nhanh", "faster")
        out.append((fmean(abs(z[k]) for k in rhythm), f"pin_rhythm_{code}_{abs(pct)}pct",
                    f"nhịp PIN {word} hơn {abs(pct)}%"))

    for axis, (pos, neg) in {"dx": (("right", "phải"), ("left", "trái")),
                             "dy": (("down", "xuống dưới"), ("up", "lên trên"))}.items():
        ks = keys(f"pin_{axis}_")
        if ks:
            shift = fmean(features[k] - tpl["mu"][k] for k in ks)
            code, vi = pos if shift > 0 else neg
            out.append((fmean(abs(z[k]) for k in ks), f"tap_offset_{code}", f"chạm lệch {vi}"))

    if "swipe_v_mean_mean" in z:
        pct = round(100 * (features["swipe_v_mean_mean"] / tpl["mu"]["swipe_v_mean_mean"] - 1))
        word, code = ("nhanh", "faster") if pct > 0 else ("chậm", "slower")
        out.append((abs(z["swipe_v_mean_mean"]), f"swipe_{code}_{abs(pct)}pct", f"vuốt {word} hơn {abs(pct)}%"))

    if "swipe_straight_mean" in z:
        straighter = z["swipe_straight_mean"] > 0
        out.append((abs(z["swipe_straight_mean"]), "swipe_straighter" if straighter else "swipe_curvier",
                    "vuốt thẳng hơn" if straighter else "vuốt cong hơn"))

    return sorted((r for r in out if r[0] >= Z_MIN), reverse=True)[:3]


def explain(human: float, bot_reasons: list[str], owner: float | None, features: dict, tpl: dict | None,
            z: dict, new_recipient: bool, amount_anom: float, action: str) -> tuple[list[str], str]:
    reasons: list[str] = []
    parts: list[str] = []

    if human < 0.5:
        bots = [r for r in bot_reasons if r in _BOT_VI]
        reasons += bots
        parts.append("Thao tác có dấu hiệu do máy thực hiện"
                     + (f" ({', '.join(_BOT_VI[r] for r in bots)})" if bots else "") + ".")
    elif owner is None:
        reasons.append("not_enrolled")
        parts.append("Tài khoản chưa đăng ký nhịp thao tác.")
    elif owner_model.missing_pin_evidence(features, tpl):
        reasons.append("missing_pin_evidence")
        parts.append("Phiên không có đủ thao tác nhập PIN để đối chiếu với chủ tài khoản.")
    else:
        owner_rs = _owner_reasons(features, tpl, z)
        reasons += [code for _, code, _ in owner_rs]
        if owner < 0.5:
            detail = f" ({', '.join(vi for *_, vi in owner_rs)})" if owner_rs else ""
            parts.append(f"Thao tác giống người thật nhưng không khớp thói quen của chủ tài khoản{detail}.")
        else:
            parts.append("Thao tác khớp thói quen của chủ tài khoản.")

    ctx = []
    if new_recipient:
        reasons.append("new_recipient")
        ctx.append("người nhận mới")
    if amount_anom >= 0.5:
        reasons.append("amount_unusual")
        ctx.append("số tiền lớn bất thường")
    if ctx:
        parts.append(f"Giao dịch: {', '.join(ctx)}.")

    parts.append(_ACTION_VI[action])
    return reasons, " ".join(parts)
