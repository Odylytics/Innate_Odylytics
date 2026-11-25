from app.scoring.vi_ime import expected_transforms, style_features, tone_choices
from tests.synth_vi import type_phrase

P = "Hôm nay trời đẹp quá"


def test_tone_choices_and_expected_transforms():
    assert [tone_choices(w) for w in P.split()] == [0, 0, 2, 2, 1]  # trời: sau ơ hoặc sau i; đẹp: sau ẹ hoặc sau p; quá: chỉ cuối
    assert expected_transforms(P) == 6  # ô, ơ+huyền, đ, ẹ, á => 1+2+1+1+1


def test_telex_late_vs_early_and_vni():
    late = style_features(type_phrase(P, "telex", 1.0), P)
    early = style_features(type_phrase(P, "telex", 0.0), P)
    vni = style_features(type_phrase(P, "vni", 1.0), P)
    assert late["vi_tone_late"] == 1.0 and early["vi_tone_late"] == 0.0
    assert late["vi_vni_frac"] == 0.0 and vni["vi_vni_frac"] == 1.0
    assert late["vi_ime_coverage"] == 1.0


def test_unikey_backspace_mode_counts_as_transform():
    f = style_features(type_phrase(P, "telex", 1.0, unikey_backspace=True), P)
    assert f["vi_ime_coverage"] == 1.0 and f["vi_tone_late"] == 1.0


def test_no_ime_typing_is_flagged():
    plain = [{"t": 150 * i, "kind": "key", "n": 1, "cls": "letter"} for i in range(20)]
    assert style_features(plain, P) == {"vi_ime_coverage": 0.0}


def test_phone_web_without_key_class_does_not_guess_telex_or_vni():
    ev = [{**e, "cls": None} if e["n"] == 0 else e for e in type_phrase(P)]
    assert "vi_vni_frac" not in style_features(ev, P)
