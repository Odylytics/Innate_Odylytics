import math

from app.scoring import owner


def _enroll(n=3, taps=6):
    """n lượt đăng ký giống hệt nhau (phương sai mẫu = 0) để thấy rõ phần co rút."""
    f = {"pin_total": 900.0}
    for i in range(taps):
        f[f"pin_hold_{i}"] = 90.0
        f[f"pin_dx_{i}"] = 0.1
        f[f"pin_dy_{i}"] = -0.1
        if i < taps - 1:
            f[f"pin_flight_{i}"] = 200.0
    return [dict(f) for _ in range(n)]


def test_timing_sd_is_shrunk_toward_population_but_offsets_keep_the_floor():
    prior = owner._PRIOR
    assert prior, "thiếu population_prior.json"
    tpl = owner.build_template(_enroll())
    n, nu = 3, prior["nu"]
    for k in ("pin_hold_0", "pin_flight_2"):  # phương sai mẫu = 0 -> chỉ còn phần prior
        assert math.isclose(tpl["sd"][k], math.sqrt(nu * prior["within_var"][k] / (n - 1 + nu)), rel_tol=1e-9)
    assert tpl["sd"]["pin_dx_0"] == owner._floor("pin_dx_0", 0.1)  # lệch tâm: không co rút (E10)
    assert math.isclose(tpl["sd"]["pin_total"], math.sqrt(nu * prior["within_var"]["pin_total"] / (n - 1 + nu)))


def test_pin_total_prior_only_applies_to_six_key_pins():
    tpl4 = owner.build_template(_enroll(taps=4))  # PIN 4 số: tổng thời gian khác dữ liệu nguồn -> sd có sàn
    assert tpl4["sd"]["pin_total"] == owner._floor("pin_total", 900.0)
    assert "pin_hold_3" in tpl4["sd"]  # nhưng hold/flight theo vị trí vẫn dùng prior


def test_falls_back_to_floor_when_prior_is_missing(monkeypatch):
    monkeypatch.setattr(owner, "_PRIOR", {})
    tpl = owner.build_template(_enroll())
    assert tpl["sd"]["pin_hold_0"] == owner._floor("pin_hold_0", 90.0)
