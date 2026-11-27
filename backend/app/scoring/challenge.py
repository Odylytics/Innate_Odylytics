"""Vietnamese challenge phrases: the server picks a phrase and signs a token (HMAC) holding the phrase index + expiry; the app sends the token back so the server knows the phrase WITHOUT storing the typed content.
Phrases are lowercase, no punctuation, letters and spaces only: on a phone there is no keyboard-layer/Shift switch (less rhythm noise) and both Telex and VNI can type them.
Phrases are chosen with many syllables whose tone mark is not at the end, to give many places to put the tone mark (E18). Tokens are single use: `main._consume_challenge_tokens` writes the nonce to the DB; reuse, expiry or a forged signature raises the flag `challenge_token_replayed`."""

import base64
import hashlib
import hmac
import json
import os
import secrets
import time

PHRASES = [  # >= 4 syllables with a choice of tone-mark position (E20: simulated AUC 0.78 at 4, 0.66 at 1); checked by a test
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
    """(phrase, unix expiry, nonce) if the signature is valid and has a nonce, otherwise None."""
    try:
        body, sig = token.split(".")
        if not hmac.compare_digest(sig, _sig(body)):
            return None
        i, exp, nonce = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
        return PHRASES[i], int(exp), str(nonce)
    except Exception:
        return None


def verify(token: str | None) -> str | None:
    """Return the phrase if the signature is valid, otherwise None. Expiry and reuse are not checked here (see main._consume_challenge_tokens)."""
    p = parse(token)
    return p[0] if p else None
