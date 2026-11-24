"""Ô nhập ngoài PIN (số tiền, người nhận, ghi chú) cho bot, theo từng chiến thuật. Khớp `SessionIn.fields` của backend.

Chỉ thời gian (ms nguyên), loại sự kiện, số ký tự, lớp ký tự: KHÔNG có nội dung.

1. Mã độc Trợ năng đặt thẳng văn bản (`ACTION_SET_TEXT`): một sự kiện `set_text`, không có phím.
2. Gõ phím tự động (kiểu `adb input text` có độ trễ): khoảng cách giữa phím ngẫu nhiên đều, không xoá, không dán.
3. Phát lại: chép chuỗi sự kiện của một phiên người thật, nhiễu ±5% khoảng cách.
4. Lấy mẫu từ dân số người thật: khoảng cách lấy độc lập từ kho, tỷ lệ xoá/dán khớp kho.

`humans` là danh sách phiên có `fields` (người thật). Không có thì chiến thuật 3, 4 trả về rỗng (không có gì để chép).
"""

import copy
import random

FIELD_PLAN = (("amount", "digit", (4, 8)), ("recipient", "digit", (10, 10)), ("note", "letter", (12, 40)))


def _start(rng: random.Random) -> float:
    return rng.uniform(300, 1500)


def set_text(rng: random.Random) -> list[dict]:
    t, out = _start(rng), []
    for name, _cls, (lo, hi) in FIELD_PLAN:
        out.append({"name": name, "events": [{"t": round(t), "kind": "set_text", "n": rng.randint(lo, hi)}]})
        t += rng.uniform(200, 600)
    return out


def even_typing(rng: random.Random) -> list[dict]:
    t, out = _start(rng), []
    for name, cls, (lo, hi) in FIELD_PLAN:
        ev = []
        for _ in range(rng.randint(lo, hi)):
            t += rng.uniform(60, 250)
            ev.append({"t": round(t), "kind": "key", "n": 1, "cls": cls})
        out.append({"name": name, "events": ev})
        t += rng.uniform(200, 600)
    return out


def replay(fields: list[dict], rng: random.Random) -> list[dict]:
    """Chép chuỗi sự kiện của phiên người thật, nhiễu ±5% khoảng cách giữa các sự kiện."""
    out = copy.deepcopy(fields)
    for fld in out:
        t, prev = 0.0, None
        for e in sorted(fld["events"], key=lambda e: e["t"]):
            gap = 0.0 if prev is None else (e["t"] - prev) * rng.uniform(0.95, 1.05)
            prev, t = e["t"], t + gap
            e["t"] = round(t)
    return out


def sampled(humans: list[dict], rng: random.Random, names: tuple[str, ...] | None = None) -> list[dict]:
    """Khoảng cách giữa sự kiện lấy độc lập từ kho người thật (cùng tên ô); tỷ lệ xoá/dán khớp kho."""
    out = []
    for name in names or [n for n, _c, _r in FIELD_PLAN]:
        pool = [f for h in humans for f in h.get("fields", []) if f["name"] == name]
        if not pool:
            continue
        gaps, cls_pool, lens, dels, pastes, keys = [], [], [], 0, [], 0
        for f in pool:
            ev = sorted(f["events"], key=lambda e: e["t"])
            gaps += [b["t"] - a["t"] for a, b in zip(ev, ev[1:])]
            lens.append(sum(e["kind"] == "key" for e in ev))
            cls_pool += [e.get("cls") for e in ev if e["kind"] == "key" and e.get("cls")]
            keys += sum(e["kind"] == "key" for e in ev)
            dels += sum(e["n"] for e in ev if e["kind"] == "delete")
            pastes += [e["n"] for e in ev if e["kind"] == "paste"]
        if not gaps or not cls_pool:
            continue
        p_del, p_paste = dels / max(keys, 1), len(pastes) / max(keys, 1)
        t, ev = _start(rng), []
        for _ in range(max(rng.choice(lens), 1)):
            t += rng.choice(gaps)
            ev.append({"t": round(t), "kind": "key", "n": 1, "cls": rng.choice(cls_pool)})
            r = rng.random()
            if r < p_del and ev:
                t += rng.choice(gaps)
                ev.append({"t": round(t), "kind": "delete", "n": 1})
            elif r < p_del + p_paste and pastes:
                t += rng.choice(gaps)
                ev.append({"t": round(t), "kind": "paste", "n": rng.choice(pastes)})
        out.append({"name": name, "events": ev})
    return out


def for_tactic(tactic: int, rng: random.Random, humans: list[dict], source: dict | None = None) -> list[dict]:
    if tactic == 1:
        return set_text(rng)
    if tactic == 2:
        return even_typing(rng)
    if tactic == 3:
        return replay(source["fields"], rng) if source and source.get("fields") else []
    if tactic == 4:
        return sampled(humans, rng)
    raise ValueError(f"Không có chiến thuật {tactic}")
