"""[E21] Like aalto_note_extract.py but KEEPS the key's character (to normalize by key pair). Output: data/aalto_note_keys.jsonl (gitignored, research only).

Extract REAL free-text typing rhythm from Aalto typing37k (mysqldump) into content-hidden input-field events.

Each open_input_logdata row = one text change: (TIMESTAMP ms, ..., TEST_SECTION_ID, ..., DATA = character, INPUT = text so far).
Infer the event from the INPUT length: increases by exactly 1 => key; decreases => delete; increases by > 1 => paste (prediction/autocorrect/paste). Does not rely on DATA (it has odd forms).
KEEP ONLY relative time, event type, character count, character class (digit/letter/space/symbol). Content is NOT kept.
Attach each sentence to a PARTICIPANT_ID (from open_test_sections) to split by person.
Output: research/data/aalto_note_events.jsonl (gitignored). Run: python -I experiments/aalto_note_extract.py [number of INSERTs, default 300]
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
SQL = ROOT / "data/aalto_processed/processed_mobiletyping_data.sql"
OUT = ROOT / "data/aalto_note_keys.jsonl"
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
            if d == 1:  # exactly one new character: a key press (DATA may be something other than one character, so the class is taken from the last character of INPUT)
                ev.append([t, "key", 1, (inp[-1:] or "a").lower()])  # REAL LETTERS, for research only (Aalto sample sentences, not personal data); not put into the product
            elif d < 0:
                ev.append([t, "delete", -d, None])
            elif d > 1:  # several characters at once: prediction/autocorrect/paste
                ev.append([t, "paste", d, None])
            prev = inp
        if sum(e[1] == "key" for e in ev) >= 15 and len(ev) <= 600:
            f.write(json.dumps({"participant": owner[sec], "section": sec, "events": ev}) + "\n")
            kept += 1
print(f"{len(sections)} sentences read, {kept} sentences kept (>= 15 keys, <= 600 events), {len(set(owner.values()))} people")
