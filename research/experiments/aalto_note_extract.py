"""Trích nhịp gõ văn bản tự do THẬT từ Aalto typing37k (mysqldump) thành sự kiện ô nhập ẩn nội dung.

Mỗi dòng open_input_logdata = một thay đổi văn bản: (TIMESTAMP ms, ..., TEST_SECTION_ID, ..., DATA = ký tự, INPUT = văn bản đến lúc đó).
Suy ra sự kiện từ độ dài INPUT: tăng đúng 1 => key; giảm => delete; tăng > 1 => paste (dự đoán/tự sửa/dán). Không dựa vào DATA (có dạng lạ).
CHỈ GIỮ thời gian tương đối, loại sự kiện, số ký tự, lớp ký tự (digit/letter/space/symbol). KHÔNG giữ nội dung.
Gắn mỗi câu với PARTICIPANT_ID (từ open_test_sections) để chia theo người.
Ra: research/data/aalto_note_events.jsonl (gitignored). Chạy: python -I experiments/aalto_note_extract.py [số INSERT, mặc định 300]
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
SQL = ROOT / "data/aalto_processed/processed_mobiletyping_data.sql"
OUT = ROOT / "data/aalto_note_events.jsonl"
K = int(sys.argv[1]) if len(sys.argv) > 1 else 300
S = r"'((?:[^'\\]|\\.)*)'"
RX_LOG = re.compile(r"\((\d+),(\d+|NULL),(\d+|NULL)," + S + "," + S + "," + S + "," + S + "," + S + "," + S + ",")
RX_SEC = re.compile(r"\((\d+),(\d+),(\d+),'")


def inserts(table, limit=None):
    cmd = ["grep", "-a"] + (["-m", str(limit)] if limit else []) + [f"^INSERT INTO `{table}`", str(SQL)]
    with subprocess.Popen(cmd, stdout=subprocess.PIPE) as p:
        for line in p.stdout:
            yield line.decode("utf-8", "replace")


def cls(ch: str) -> str:
    return "digit" if ch.isdigit() else "letter" if ch.isalpha() else "space" if ch.isspace() else "symbol"


sections: dict[str, list[tuple[int, str, str]]] = {}
for line in inserts("open_input_logdata", K):
    for m in RX_LOG.finditer(line):
        ts, _lid, sec, _typ, _key, _code, data, inp, _pr = m.groups()
        if sec != "NULL":
            sections.setdefault(sec, []).append((int(ts), data, inp))

need = set(sections)
owner = {}
for line in inserts("open_test_sections"):
    for m in RX_SEC.finditer(line):
        if m.group(1) in need:
            owner[m.group(1)] = m.group(3)

kept = 0
with OUT.open("w", encoding="utf-8") as f:
    for sec, rows in sections.items():
        if sec not in owner:
            continue
        rows.sort()
        t0, prev, ev = rows[0][0], "", []
        for ts, data, inp in rows:
            d = len(inp) - len(prev)
            t = ts - t0
            if d == 1:  # đúng một ký tự mới: phím gõ (DATA có thể có dạng khác một ký tự, nên lớp lấy từ ký tự cuối của INPUT)
                ev.append([t, "key", 1, cls(inp[-1:] or "a")])
            elif d < 0:
                ev.append([t, "delete", -d, None])
            elif d > 1:  # nhiều ký tự cùng lúc: dự đoán/tự sửa/dán
                ev.append([t, "paste", d, None])
            prev = inp
        if sum(e[1] == "key" for e in ev) >= 15 and len(ev) <= 600:
            f.write(json.dumps({"participant": owner[sec], "section": sec, "events": ev}) + "\n")
            kept += 1
print(f"{len(sections)} câu đọc được, {kept} câu giữ lại (>= 15 phím, <= 600 sự kiện), {len(set(owner.values()))} người")
