"""Câu thử thách tiếng Việt: máy chủ chọn câu, ký token (HMAC) chứa chỉ số câu + hạn; app gửi lại token để máy chủ biết câu mà KHÔNG lưu nội dung gõ.
Câu viết thường, không dấu câu, chỉ chữ cái và khoảng trắng: trên điện thoại không phải đổi lớp phím/Shift (đỡ nhiễu nhịp) và Telex/VNI đều gõ được.
Câu chọn có nhiều âm tiết "dấu thanh không ở cuối" để có nhiều chỗ đặt dấu thanh (E18). Token dùng một lần: `main._consume_challenge_tokens` ghi nonce vào DB; dùng lại, hết hạn hoặc giả chữ ký thì cờ `challenge_token_replayed`."""

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
TTL_S = 300


def _secret() -> bytes:
    return os.environ.get("NHIP_CHALLENGE_SECRET", "dev-only-secret").encode()


def _sig(body: str) -> str:
    return hmac.new(_secret(), body.encode(), hashlib.sha256).hexdigest()[:20]


def issue(now: float | None = None) -> dict:
    i = secrets.randbelow(len(PHRASES))
    payload = [i, int((now or time.time()) + TTL_S), secrets.token_hex(8)]
    body = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    return {"token": f"{body}.{_sig(body)}", "phrase": PHRASES[i], "expected_len": len(PHRASES[i]), "ttl_s": TTL_S}


def parse(token: str | None) -> tuple[str, int, str] | None:
    """(câu, hạn unix, nonce) nếu chữ ký đúng và có nonce, ngược lại None."""
    try:
        body, sig = token.split(".")
        if not hmac.compare_digest(sig, _sig(body)):
            return None
        i, exp, nonce = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
        return PHRASES[i], int(exp), str(nonce)
    except Exception:
        return None


def verify(token: str | None) -> str | None:
    """Trả về câu nếu chữ ký đúng, ngược lại None. Không kiểm hạn và dùng lại ở đây (xem main._consume_challenge_tokens)."""
    p = parse(token)
    return p[0] if p else None
