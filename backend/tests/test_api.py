import os
import random
import tempfile

os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(tempfile.mkdtemp(), "test.db")
os.environ["NHIP_API_KEYS"] = "test-key"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.scoring import owner  # noqa: E402
from tests.synth import IMPOSTOR, OWNER, bot_session, human_session  # noqa: E402

H = {"X-API-Key": "test-key"}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def _post_session(client, body) -> str:
    r = client.post("/v1/sessions", json=body, headers=H)
    assert r.status_code == 200, r.text
    return r.json()["session_id"]


def _score(client, sid, **ctx) -> dict:
    r = client.post(f"/v1/sessions/{sid}/score", json=ctx, headers=H)
    assert r.status_code == 200, r.text
    return r.json()


def test_health_and_auth(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.post("/v1/sessions", json={"user_id": "x"}).status_code == 401
    assert client.post("/v1/sessions", json={"user_id": "x"}, headers={"X-API-Key": "sai"}).status_code == 401


def test_rejects_bad_input(client):
    body = bot_session("bad")
    body["pin_taps"][0]["t_up"] = -1 + body["pin_taps"][0]["t_down"]
    assert client.post("/v1/sessions", json=body, headers=H).status_code == 422
    assert client.post("/v1/sessions", json={"user_id": "a b"}, headers=H).status_code == 422


def test_full_flow(client):
    rng = random.Random(7)
    user = "owner1"

    # Chưa đăng ký -> owner_match None
    first = _score(client, _post_session(client, human_session(user, OWNER, rng)))
    assert first["owner_match"] is None and "not_enrolled" in first["reasons"]

    for i in range(3):
        r = client.post(f"/v1/users/{user}/enroll",
                        json={"session_id": _post_session(client, human_session(user, OWNER, rng))}, headers=H)
        assert r.status_code == 200
    assert r.json() == {"user_id": user, "enrolled_sessions": 3, "template_ready": True}

    # Chủ thật, người nhận cũ -> cho qua (trên phần lớn các lần thử)
    owner_results = [_score(client, _post_session(client, human_session(user, OWNER, rng)), amount=100_000)
                     for _ in range(5)]
    assert sum(r["action"] == "allow" for r in owner_results) >= 4, owner_results
    assert all(r["human_score"] > 0.7 for r in owner_results)

    # Người khác biết PIN -> yêu cầu xác thực thêm, có lý do cụ thể
    imp = _score(client, _post_session(client, human_session(user, IMPOSTOR, rng)), amount=100_000)
    assert imp["action"] in ("step_up", "hold"), imp
    assert imp["owner_match"] < 0.5
    assert any(r.startswith(("pin_rhythm_", "tap_offset_")) for r in imp["reasons"])
    assert "không khớp thói quen" in imp["explanation_vi"]

    # Bot -> giữ lệnh, báo không phải người
    bot = _score(client, _post_session(client, bot_session(user)), recipient_is_new=True, amount=5_000_000)
    assert bot["action"] == "hold" and bot["human_score"] < 0.3, bot
    assert "tap_exact_center" in bot["reasons"] and "new_recipient" in bot["reasons"]
    assert "amount_unusual" in bot["reasons"]  # 50x trung vị lịch sử

    # Mẫu chuẩn được cập nhật sau các phiên chủ thật được cho qua
    assert client.get(f"/v1/users/{user}", headers=H).json()["template_updates"] >= 1

    # Dashboard
    flagged = client.get("/v1/sessions?flagged=true", headers=H).json()
    ids = {f["session_id"] for f in flagged}
    assert {imp["session_id"], bot["session_id"]} <= ids
    r = client.post(f"/v1/sessions/{bot['session_id']}/label", json={"label": "fraud"}, headers=H)
    assert r.json()["label"] == "fraud"


def test_enroll_rejects_other_users_session(client):
    sid = _post_session(client, human_session("alice", OWNER, random.Random(1)))
    assert client.post("/v1/users/bob/enroll", json={"session_id": sid}, headers=H).status_code == 400


def test_template_drift_is_capped():
    rng = random.Random(3)
    from app.scoring import features

    feats = [features.extract(human_session("u", OWNER, rng)) for _ in range(3)]
    tpl = owner.build_template(feats)
    far = {k: v + 1000 for k, v in feats[0].items()}  # kẻ gian "dạy dần" bằng phiên lệch xa
    for _ in range(200):
        tpl = owner.update(tpl, far)
    for k in tpl["mu"]:
        assert abs(tpl["mu"][k] - tpl["mu0"][k]) <= owner.DRIFT_CAP * tpl["sd"][k] + 1e-9


def test_collection_meta_and_export(client):
    rng = random.Random(11)
    body = human_session("acc_p01", OWNER, rng)
    body["meta"] = {"participant_id": "p01", "sitting": 1, "role": "genuine"}
    sid = _post_session(client, body)
    imp = human_session("acc_p01", IMPOSTOR, rng)
    imp["meta"] = {"participant_id": "p02", "sitting": 1, "role": "impostor", "note": "xem chủ bấm 1 lần"}
    _post_session(client, imp)
    _post_session(client, human_session("acc_p01", OWNER, rng))  # không meta -> không xuất

    bad = dict(body, meta={"participant_id": "p01", "sitting": 0, "role": "genuine"})
    assert client.post("/v1/sessions", json=bad, headers=H).status_code == 422

    rows = client.get("/v1/export", headers=H).json()
    mine = [r for r in rows if r["user_id"] == "acc_p01"]
    assert [r["meta"]["role"] for r in mine] == ["genuine", "impostor"]
    assert mine[0]["session_id"] == sid and "pin_hold_0" in mine[0]["features"]
    assert [r["meta"]["participant_id"] for r in client.get("/v1/export?participant_id=p02", headers=H).json()] == ["p02"]


def test_unflagged_list_skips_unscored_sessions(client):
    _post_session(client, human_session("unscored", OWNER, random.Random(5)))
    r = client.get("/v1/sessions?flagged=false", headers=H)
    assert r.status_code == 200
    assert all(s["action"] is not None for s in r.json())


def test_bot_meta_requires_tactic(client):
    body = bot_session("acc_bot")
    for meta, code in [({"participant_id": "sim", "sitting": 1, "role": "bot", "tactic": 2}, 200),
                       ({"participant_id": "sim", "sitting": 1, "role": "bot"}, 422),
                       ({"participant_id": "p01", "sitting": 1, "role": "genuine", "tactic": 1}, 422)]:
        assert client.post("/v1/sessions", json=dict(body, meta=meta), headers=H).status_code == code


def test_wallet_page_served(client):
    r = client.get("/")
    assert r.status_code == 200 and "Innate SDK" in r.text


def _replayed(src: dict, user: str, rng: random.Random, noise: float = 0.05) -> dict:
    """Phát lại một phiên thật: thời gian ±noise, toạ độ ±2 px (như chiến thuật 3)."""
    import copy
    s = copy.deepcopy(src)
    s["user_id"] = user
    t = 0.0
    taps = sorted(s["pin_taps"], key=lambda x: x["t_down"])
    for i, tap in enumerate(taps):
        hold = (tap["t_up"] - tap["t_down"]) * rng.uniform(1 - noise, 1 + noise)
        gap = (taps[i + 1]["t_down"] - tap["t_up"]) * rng.uniform(1 - noise, 1 + noise) if i < len(taps) - 1 else 0
        tap["x"] += rng.uniform(-2, 2)
        tap["y"] += rng.uniform(-2, 2)
        tap["t_down"], tap["t_up"] = t, t + hold
        t += hold + gap
    s["pin_taps"] = taps
    return s


def test_replayed_session_is_held_but_new_human_session_is_not(client):
    rng = random.Random(11)
    user = "replay_victim"
    sessions = [human_session(user, OWNER, rng) for _ in range(4)]
    for s in sessions[:3]:
        sid = _post_session(client, s)
        assert client.post(f"/v1/users/{user}/enroll", json={"session_id": sid}, headers=H).status_code == 200

    # phiên người thật mới (không phải bản sao) không bị coi là phát lại
    fresh = _score(client, _post_session(client, sessions[3]))
    assert "replayed_session" not in fresh["reasons"]

    # phát lại một phiên đã đăng ký, thêm nhiễu nhỏ -> giữ lệnh
    r = _score(client, _post_session(client, _replayed(sessions[0], user, rng)))
    assert r["action"] == "hold" and "replayed_session" in r["reasons"]
