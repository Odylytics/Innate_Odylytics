"""Giả lập người gõ câu tiếng Việt bằng Telex/VNI (dữ liệu GIẢ, chỉ để test trích đặc trưng)."""

from app.scoring.vi_ime import syllable_units


def type_phrase(phrase: str, system: str = "telex", tone_late: float = 1.0, gap: int = 150, unikey_backspace: bool = False) -> list[dict]:
    """tone_late: 0 = gõ dấu thanh ngay sau nguyên âm, 1 = để cuối âm tiết. unikey_backspace: biến đổi lộ ra dạng delete + key sát nhau."""
    si = 0 if system == "telex" else 1
    ev, t = [], 0

    def add(kind, n, cls):
        nonlocal t
        ev.append({"t": t, "kind": kind, "n": n, "cls": cls})
        t += gap

    def transform(key):
        cls = "digit" if key.isdigit() else "letter"
        if unikey_backspace:
            add("delete", 1, None)
            t_back = ev[-1]["t"]
            ev.append({"t": t_back + 5, "kind": "key", "n": 1, "cls": cls})
        else:
            add("key", 0, cls)

    for wi, word in enumerate(phrase.split()):
        if wi:
            add("key", 1, "space")
        units = syllable_units(word)
        ti = next((i for i, u in enumerate(units) if u["tone"]), None)
        place = None if ti is None else ti + round((len(units) - 1 - ti) * tone_late)  # gõ dấu thanh sau đơn vị này
        for i, u in enumerate(units):
            add("key", 1, "letter")
            if u["mark"]:
                transform(u["mark"][si])
            if i == place:
                transform(units[ti]["tone"][si])
    return ev
