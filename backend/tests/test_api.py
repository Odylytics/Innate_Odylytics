import os
import random
import tempfile

os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(tempfile.mkdtemp(), "test.db")
# test-key có mọi quyền cho các test luồng; sdk-key/ops-key/ml-key mỗi key một quyền cho test phân quyền
os.environ["NHIP_API_KEYS"] = "test-key,sdk-key"
os.environ["NHIP_OPS_KEYS"] = "test-key,ops-key"
os.environ["NHIP_ML_KEYS"] = "test-key,ml-key"

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


def test_keys_are_scoped_by_role(client):
    sdk, ops, ml = ({"X-API-Key": k} for k in ("sdk-key", "ops-key", "ml-key"))
    sid = _post_session(client, human_session("scope_u", OWNER, random.Random(21)))
    # key SDK (nằm trong app web) không mở được dashboard, gắn nhãn hay export
    assert client.get("/v1/export", headers=sdk).status_code == 403
    assert client.get("/v1/sessions", headers=sdk).status_code == 403
    assert client.post(f"/v1/sessions/{sid}/label", json={"label": "legit"}, headers=sdk).status_code == 403
    # key ops chỉ dùng dashboard, key ml chỉ export
    assert client.get("/v1/sessions", headers=ops).status_code == 200
    assert client.get("/v1/export", headers=ops).status_code == 403
    assert client.get("/v1/export", headers=ml).status_code == 200
    assert client.post("/v1/sessions", json=human_session("x", OWNER, random.Random(1)), headers=ml).status_code == 403
    # key lạ vẫn là 401; header ngoài ASCII không làm sập server
    assert client.get("/v1/export", headers={"X-API-Key": "sai"}).status_code == 401
    assert client.get("/v1/export", headers={"X-API-Key": "khóa".encode()}).status_code == 401


def _enroll(client, user, sessions):
    for body in sessions:
        r = client.post(f"/v1/users/{user}/enroll", json={"session_id": _post_session(client, body)}, headers=H)
        assert r.status_code == 200, r.text
    return r.json()


def test_enrollment_locked_once_template_ready(client):
    rng = random.Random(31)
    assert _enroll(client, "lock_u", [human_session("lock_u", OWNER, rng) for _ in range(3)])["template_ready"]
    tpl_before = client.get("/v1/users/lock_u", headers=H).json()
    # kẻ gian chèn nhịp của mình vào tài khoản đã đăng ký -> bị chặn, mẫu chuẩn giữ nguyên
    sid = _post_session(client, human_session("lock_u", IMPOSTOR, rng))
    r = client.post("/v1/users/lock_u/enroll", json={"session_id": sid}, headers=H)
    assert r.status_code == 409
    assert client.get("/v1/users/lock_u", headers=H).json() == tpl_before


def test_enrolled_user_without_pin_evidence_is_not_allowed(client):
    rng = random.Random(41)
    no_swipe = [dict(human_session("pin_u", OWNER, rng), swipes=[]) for _ in range(3)]  # mẫu chuẩn không có đặc trưng vuốt
    _enroll(client, "pin_u", no_swipe)
    swipe_only = {"user_id": "pin_u", "pin_taps": [],
                  "swipes": [{"points": [{"t": 0, "x": 200, "y": 600}, {"t": 40, "x": 230, "y": 470},
                                         {"t": 90, "x": 290, "y": 330}]}]}
    r = _score(client, _post_session(client, swipe_only))
    assert r["owner_match"] == 0 and r["action"] != "allow", r
    assert "missing_pin_evidence" in r["reasons"]
    # PIN ngắn hơn PIN đã đăng ký cũng không được coi là khớp
    short = human_session("pin_u", OWNER, rng)
    short["pin_taps"] = short["pin_taps"][:1]
    assert _score(client, _post_session(client, short))["action"] != "allow"


def test_sdk_key_has_no_public_default_outside_local(tmp_path):
    import subprocess
    import sys

    code = "import app.main as m; print(m.SCOPE_KEYS['sdk'])"
    env = {k: v for k, v in os.environ.items() if not k.startswith("NHIP_")}
    # DB thật mà quên NHIP_API_KEYS -> không có key nào hợp lệ (đóng), không rơi về demo-key
    pg = dict(env, DATABASE_URL="postgresql://u:p@localhost:1/db")
    assert subprocess.run([sys.executable, "-c", code], env=pg, capture_output=True, text=True,
                          check=True).stdout.strip() == "[]"
    local = dict(env, DATABASE_URL=f"sqlite:///{tmp_path / 'x.db'}")
    assert subprocess.run([sys.executable, "-c", code], env=local, capture_output=True, text=True,
                          check=True).stdout.strip() == "['demo-key']"


def _export_all(client, **params):
    rows, offset, pages = [], "0", 0
    while offset is not None:
        r = client.get("/v1/export", params={**params, "offset": offset}, headers=H)
        assert r.status_code == 200
        rows += r.json()
        offset, pages = r.headers.get("x-next-offset"), pages + 1
    return rows, pages


def test_export_is_paged_and_byte_bounded(client, monkeypatch):
    import app.main as m

    rng = random.Random(51)
    for i in range(5):
        body = human_session("page_u", OWNER, rng)
        body["meta"] = {"participant_id": "page_p", "sitting": 1, "role": "genuine"}
        _post_session(client, body)
    everything, _ = _export_all(client, participant_id="page_p")
    assert len(everything) == 5
    # trang nhỏ: đi theo X-Next-Offset vẫn lấy đủ, không trùng
    paged, pages = _export_all(client, participant_id="page_p", limit=2)
    assert [r["session_id"] for r in paged] == [r["session_id"] for r in everything] and pages > 1
    # ngân sách byte nhỏ: mỗi trang dừng sớm nhưng vẫn lấy đủ qua nhiều trang
    monkeypatch.setattr(m, "EXPORT_BYTE_BUDGET", 1)
    budgeted, pages = _export_all(client, participant_id="page_p")
    assert len(budgeted) == 5 and pages >= 5


def test_swipe_size_caps(client):
    body = human_session("cap_u", OWNER, random.Random(61))
    body["swipes"] = [{"points": [{"t": i, "x": 200, "y": 600 - i} for i in range(201)]}]
    assert client.post("/v1/sessions", json=body, headers=H).status_code == 422
    body["swipes"] = [{"points": [{"t": 0, "x": 0, "y": 0}, {"t": 1, "x": 1, "y": 1}]}] * 31
    assert client.post("/v1/sessions", json=body, headers=H).status_code == 422
