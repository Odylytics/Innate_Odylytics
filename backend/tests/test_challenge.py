import random

from app.scoring import challenge, features, human, vi_ime
from tests.synth import human_session
from tests.synth_vi import type_phrase


def test_token_roundtrip_and_tamper():
    c = challenge.issue()
    assert challenge.verify(c["token"]) == c["phrase"] and c["expected_len"] == len(c["phrase"])
    body, sig = c["token"].split(".")
    assert challenge.verify(body + "." + "0" * len(sig)) is None and challenge.verify("rác") is None and challenge.verify(None) is None


def test_every_phrase_is_phone_friendly_and_has_enough_marks():
    for p in challenge.PHRASES:
        assert p == p.lower() and all(ch.isalpha() or ch == " " for ch in p), p
        assert vi_ime.expected_transforms(p) >= 5, p
        assert sum(vi_ime.tone_choices(w) >= 2 for w in p.split()) >= 4, p


def _raw(events, token):
    s = human_session("u", __import__("tests.synth", fromlist=["OWNER"]).OWNER, random.Random(1))
    s["fields"] = [{"name": "challenge", "token": token, "events": events}]
    return s


def test_extract_uses_server_phrase_and_flags_no_ime():
    c = challenge.issue(); ph = c["phrase"]
    f = features.extract(_raw(type_phrase(ph, "telex", 1.0), c["token"]))
    assert f["vi_ime_coverage"] == 1.0 and "challenge_no_ime" not in human.score(f)[1]
    plain = [{"t": 120 * i, "kind": "key", "n": 1, "cls": "letter"} for i in range(len(ph))]  # đặt từng chữ không qua bộ gõ
    g = features.extract(_raw(plain, c["token"]))
    assert g["vi_ime_coverage"] == 0.0 and "challenge_no_ime" in human.score(g)[1]
    assert "vi_ime_coverage" not in features.extract(_raw(plain, "token-gia"))  # token giả: không tin

