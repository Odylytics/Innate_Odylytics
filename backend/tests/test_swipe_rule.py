from app.scoring import features, human


def _swipe(speeds, dt=16):
    pts, y, t = [{"t": 0, "x": 100.0, "y": 800.0}], 800.0, 0
    for v in speeds:
        t += dt
        y -= v * dt
        pts.append({"t": t, "x": 100.0, "y": y})
    return {"points": pts}


def _f(swipes):
    return features.extract({"pin_taps": [], "swipes": swipes})


def test_uniform_speed_swipe_is_flagged_human_like_is_not():
    bot = _f([_swipe([2.0] * 8)])
    human_like = _f([_swipe([0.5, 1.4, 2.6, 3.1, 2.2, 1.1, 0.6, 0.2])])  # thẳng tuyệt đối nhưng tăng-giảm tốc như ngón tay
    assert bot["swipe_robotic"] == 1.0 and human_like["swipe_robotic"] == 0.0


def test_short_straight_human_stroke_not_flagged_as_before():
    f = _f([_swipe([0.4, 2.8, 0.9])])  # 4 điểm, thẳng: luật cũ (straight > 0.999) gắn cờ nhầm
    assert f["swipe_straight_max"] > 0.999 and f["swipe_robotic"] == 0.0


def test_swipes_do_not_enter_owner_identity():
    from app.scoring import owner
    assert not any(owner.is_identity_feature(k) for k in ("swipe_dur_mean", "swipe_v_peak_mean", "swipe_robotic"))
