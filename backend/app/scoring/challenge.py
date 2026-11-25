"""Câu thử thách tiếng Việt: máy chủ chọn câu, ký token (HMAC) chứa chỉ số câu + hạn; app gửi lại token để máy chủ biết câu mà KHÔNG lưu nội dung gõ.
Câu viết thường, không dấu câu, chỉ chữ cái và khoảng trắng: trên điện thoại không phải đổi lớp phím/Shift (đỡ nhiễu nhịp) và Telex/VNI đều gõ được.
Câu chọn có nhiều âm tiết "dấu thanh không ở cuối" để có nhiều chỗ đặt dấu thanh (E18). Chưa chống dùng lại token (không có kho nonce): chỉ chống giả câu."""

import base64
import hashlib
import hmac
import json
import os
import secrets
import time

PHRASES = [  # >= 4 âm tiết có chỗ chọn dấu thanh (E20: AUC mô phỏng 0.78 ở 4, 0.66 ở 1); kiểm bằng test
    "tuần này trời nắng đẹp quá",
    "tháng này tiền điện nước hơi nhiều",
    "hẹn gặp lại bạn vào tuần sau",
    "chuyển khoản tiền ăn tuần trước nhé",
    "những buổi chiều mưa nhớ người xưa",
    "cuối tuần mình ra biển chơi nhé",
    "trời trong gió mát lòng người vui",
    "hôm nay trời đẹp quá mình đi uống cà phê nhé",
]
TTL_S = 120


def _secret() -> bytes:
    return os.environ.get("NHIP_CHALLENGE_SECRET", "dev-only-secret").encode()


def _sig(body: str) -> str:
    return hmac.new(_secret(), body.encode(), hashlib.sha256).hexdigest()[:20]


def issue(now: float | None = None) -> dict:
    i = secrets.randbelow(len(PHRASES))
    body = base64.urlsafe_b64encode(json.dumps([i, int((now or time.time()) + TTL_S)]).encode()).decode().rstrip("=")
    return {"token": f"{body}.{_sig(body)}", "phrase": PHRASES[i], "expected_len": len(PHRASES[i]), "ttl_s": TTL_S}


def verify(token: str | None) -> str | None:
    """Trả về câu nếu chữ ký đúng, ngược lại None. Không kiểm hạn ở đây: phiên có thể được chấm sau vài phút; hạn chỉ dùng khi cấp token mới."""
    try:
        body, sig = token.split(".")
        if not hmac.compare_digest(sig, _sig(body)):
            return None
        return PHRASES[json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))[0]]
    except Exception:
        return None
