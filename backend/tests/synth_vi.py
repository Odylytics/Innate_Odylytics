"""Simulates a person typing a Vietnamese phrase in Telex/VNI (FAKE data, only to test feature extraction)."""

from app.scoring.vi_ime import syllable_units


def type_phrase(phrase: str, system: str = "telex", tone_late: float = 1.0, gap: int = 150, unikey_backspace: bool = False) -> list[dict]:
    """tone_late: 0 = type the tone mark right after the vowel, 1 = leave it to the end of the syllable. unikey_backspace: the transform shows up as a delete + key in close succession."""
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
        place = None if ti is None else ti + round((len(units) - 1 - ti) * tone_late)  # type the tone mark after this unit
        for i, u in enumerate(units):
            add("key", 1, "letter")
            if u["mark"]:
                transform(u["mark"][si])
            if i == place:
                transform(units[ti]["tone"][si])
    return ev
