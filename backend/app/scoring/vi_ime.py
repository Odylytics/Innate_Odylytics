"""Kiểu gõ tiếng Việt (Telex/VNI) từ ô `challenge`, KHÔNG cần nội dung người dùng gõ.

Câu thử thách do máy chủ sinh nên máy chủ biết câu đúng. Từ câu đó tính được mỗi âm tiết có bao nhiêu phím "biến đổi" (dấu mũ/móc/đ và dấu thanh).
Phím biến đổi KHÔNG thêm ký tự (n=0 trong InputEvent), nên lộ ra: (1) Telex hay VNI (phím chữ hay phím số), (2) gõ dấu thanh ngay sau nguyên âm hay để cuối âm tiết,
(3) tỉ lệ sửa lỗi, (4) có dùng bộ gõ tiếng Việt không (câu có dấu mà không có phím biến đổi nào = đặt/dán/bàn phím không bộ gõ).
Thói quen 2 và 1 không phụ thuộc câu cụ thể, nên giải quyết đúng điểm yếu của E13 (câu thử khác câu đăng ký).

GIẢ THUYẾT CHƯA ĐO: chưa có dữ liệu gõ tiếng Việt thật. Module này chỉ trích đặc trưng; chưa nối vào fusion/owner.
"""

import unicodedata

_TONE_TELEX = {"̀": "f", "́": "s", "̉": "r", "̃": "x", "̣": "j"}
_TONE_VNI = {"̀": "2", "́": "1", "̉": "3", "̃": "4", "̣": "5"}
# dấu phụ -> (phím Telex thứ hai, phím VNI)
_MARK = {"̂": {"a": ("a", "6"), "e": ("e", "6"), "o": ("o", "6")}, "̆": {"a": ("w", "8")}, "̛": {"o": ("w", "7"), "u": ("w", "7")}}
COMPOSE_MS = 20  # Unikey kiểu "xoá lùi rồi chèn lại": delete + key trong <= 20 ms = một phím biến đổi


def syllable_units(word: str) -> list[dict]:
    """Tách một âm tiết thành các đơn vị: base, mark (phím biến đổi dấu mũ/móc/đ, theo telex/vni), tone (phím dấu thanh)."""
    units = []
    for ch in unicodedata.normalize("NFD", word.lower()):
        if ch == "đ":
            units.append({"base": "d", "mark": ("d", "9"), "tone": None})
        elif unicodedata.combining(ch):
            u = units[-1]
            if ch in _TONE_TELEX:
                u["tone"] = (_TONE_TELEX[ch], _TONE_VNI[ch])
            else:
                u["mark"] = _MARK[ch][u["base"]]
        else:
            units.append({"base": ch, "mark": None, "tone": None})
    return units


def tone_choices(word: str) -> int:
    """Số chỗ hợp lệ để gõ phím dấu thanh (ngay sau nguyên âm mang dấu, hoặc sau mỗi chữ còn lại tới cuối âm tiết). 1 = không có lựa chọn; 0 = không dấu thanh."""
    u = syllable_units(word)
    idx = next((i for i, x in enumerate(u) if x["tone"]), None)
    return 0 if idx is None else len(u) - idx


def expected_transforms(phrase: str) -> int:
    """Số phím biến đổi tối thiểu để gõ câu bằng Telex/VNI (mỗi dấu mũ/móc/đ một phím, mỗi dấu thanh một phím)."""
    return sum((u["mark"] is not None) + (u["tone"] is not None) for w in phrase.split() for u in syllable_units(w))


def _norm(events: list[dict]) -> list[tuple[int, str, str | None]]:
    """-> [(t, 'char'|'transform'|'delete'|'other', cls)]; gộp delete+key sát nhau thành 'transform'."""
    out, i = [], 0
    while i < len(events):
        e = events[i]
        nxt = events[i + 1] if i + 1 < len(events) else None
        if e["kind"] == "delete" and nxt and nxt["kind"] == "key" and nxt["n"] == 1 and nxt["t"] - e["t"] <= COMPOSE_MS:
            out.append((nxt["t"], "transform", nxt.get("cls")))
            i += 2
            continue
        if e["kind"] == "key":
            out.append((e["t"], "transform" if e["n"] == 0 else "char", e.get("cls")))
        elif e["kind"] == "delete":
            out.append((e["t"], "delete", None))
        else:
            out.append((e["t"], "other", None))
        i += 1
    return out


def style_features(events: list[dict], phrase: str) -> dict[str, float]:
    """Đặc trưng kiểu gõ. events = fields[name=challenge].events (dict), phrase = câu máy chủ đã sinh. Thiếu dữ liệu thì bỏ khoá."""
    f: dict[str, float] = {}
    ev = _norm(events)
    chars = [e for e in ev if e[1] == "char"]
    trans = [e for e in ev if e[1] == "transform"]
    need = expected_transforms(phrase)
    if need >= 3 and len(chars) >= 5:  # câu có dấu mà gõ không có phím biến đổi nào: không dùng bộ gõ tiếng Việt (tín hiệu mềm)
        f["vi_ime_coverage"] = min(1.0, len(trans) / need)
    if not trans:
        return f
    known = [e for e in trans if e[2] is not None]  # web trên điện thoại không thấy phím nào: cls = None, không đoán Telex/VNI
    if known:
        f["vi_vni_frac"] = sum(e[2] == "digit" for e in known) / len(known)
    f["vi_delete_rate"] = sum(e[1] == "delete" for e in ev) / max(1, len(chars))
    gc = [b[0] - a[0] for a, b in zip(ev, ev[1:]) if b[1] == "char"]
    gt = [b[0] - a[0] for a, b in zip(ev, ev[1:]) if b[1] == "transform"]
    if len(gc) >= 3 and len(gt) >= 2:
        f["vi_transform_gap_ratio"] = (sum(gt) / len(gt)) / max(1.0, sum(gc) / len(gc))

    # độ muộn của phím dấu thanh: 0 = ngay sau nguyên âm, 1 = cuối âm tiết; chỉ tính âm tiết có >= 2 chỗ đặt
    words, cur = [], []
    for e in ev:
        if e[1] == "other" or (e[1] == "char" and e[2] == "space"):
            words.append(cur)
            cur = []
        else:
            cur.append(e)
    words.append(cur)
    late = []
    for w, syl in zip([w for w in words if w], phrase.split()):
        k = tone_choices(syl) - 1
        if k < 1:
            continue
        ti = max((i for i, e in enumerate(w) if e[1] == "transform"), default=None)
        if ti is None:
            continue
        after = min(k, sum(e[1] == "char" for e in w[ti + 1 :]))
        late.append((k - after) / k)
    if late:
        f["vi_tone_late"] = sum(late) / len(late)
    return f
