"""python -m nhip_attacker {generate,report,adb} ...  —  xem README.md."""

import argparse
import json
import os
import random
import statistics
import sys

import httpx

from . import adb, tactics


def _client(args) -> httpx.Client:
    key = args.key or os.environ.get("NHIP_API_KEY")
    if not key:
        sys.exit("Missing API key: set the NHIP_API_KEY environment variable or pass --key")
    return httpx.Client(base_url=args.api, headers={"X-API-Key": key}, timeout=30)


def _humans(args, c: httpx.Client) -> list[dict]:
    """Source of human sessions for tactics 3-4."""
    src = args.human_source
    if src == "synth":
        return tactics.synth_humans(30, args.pin)
    if src == "api":
        ml_key = args.ml_key or os.environ.get("NHIP_ML_KEY")
        if not ml_key:
            sys.exit("--human-source api needs an ML-scope key: set NHIP_ML_KEY or --ml-key (or use --human-source synth)")
        rows, offset = [], "0"
        while offset is not None:  # export is paged; the X-Next-Offset header signals more pages
            r = c.get("/v1/export", params={"offset": offset}, headers={"X-API-Key": ml_key}).raise_for_status()
            rows += r.json()
            offset = r.headers.get("X-Next-Offset")
        out = [r["raw"] for r in rows if (r.get("meta") or {}).get("role") == "genuine"]
        if not out:
            sys.exit("The API has no real human sessions yet (meta.role = genuine). Use --human-source synth to try first")
        return out
    if src.startswith("file:"):
        with open(src[5:], encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]
    sys.exit(f"--human-source is invalid: {src}")


def _post(c: httpx.Client, session: dict, tactic: int, note: str) -> str:
    session["meta"] = {"participant_id": "sim", "sitting": 1, "role": "bot", "tactic": tactic, "note": note}
    return c.post("/v1/sessions", json=session).raise_for_status().json()["session_id"]


def cmd_generate(args) -> None:
    """Generate labeled bot sessions so Member 1 can pull them via /v1/export as "machine" data."""
    c = _client(args)
    humans = _humans(args, c) if set(args.tactic) & {3, 4} else []
    rng = random.Random(args.seed)
    for t in args.tactic:
        for _ in range(args.n):
            _post(c, tactics.generate(t, args.user, args.pin, humans, rng), t, "generate")
        print(f"tactic {t}: sent {args.n} sessions for {args.user}")


def cmd_report(args) -> None:
    """Score each tactic on an account with enrolled rhythm -> catch rate."""
    c = _client(args)
    humans = _humans(args, c)
    rng = random.Random(args.seed)
    target, replay = args.target, None
    if args.enroll_synth:
        target = f"sim_target_{random.Random().randrange(10**6)}"
        *enroll, replay = tactics.synth_owner(target, 4, args.pin, seed=args.seed)
        for s in enroll:
            sid = c.post("/v1/sessions", json=s).raise_for_status().json()["session_id"]
            c.post(f"/v1/users/{target}/enroll", json={"session_id": sid}).raise_for_status()
    if not target:
        sys.exit("Need --target <enrolled user_id> or --enroll-synth")
    user = c.get(f"/v1/users/{target}").raise_for_status().json()
    if not user["template_ready"]:
        sys.exit(f"{target} has not completed 3 enrollment rounds")

    print(f"Target account: {target} · {args.n} sessions/tactic · human source: {args.human_source}")
    print(f"{'Tactic':<12}{'hold':>8}{'step_up':>9}{'allow':>8}{'flagged':>11}{'human TB':>10}")
    for t in args.tactic:
        acts, hs = [], []
        for _ in range(args.n):
            # tactic 3 with a synthetic target: replay a session of the account owner (malware that recorded it)
            s = tactics.tactic3(target, replay, rng) if t == 3 and replay else tactics.generate(t, target, args.pin, humans, rng)
            sid = _post(c, s, t, "report")
            r = c.post(f"/v1/sessions/{sid}/score", json={"recipient_is_new": args.new_recipient}).raise_for_status().json()
            acts.append(r["action"])
            hs.append(r["human_score"])
        pct = lambda a: 100 * acts.count(a) / len(acts)  # noqa: E731
        print(f"{t:<12}{pct('hold'):>7.0f}%{pct('step_up'):>8.0f}%{pct('allow'):>7.0f}%"
              f"{100 - pct('allow'):>10.0f}%{statistics.fmean(hs):>10.2f}")


def cmd_adb(args) -> None:
    layout = adb.load_layout(args.layout)
    swipe = tuple(args.swipe) if args.swipe else None
    for cmd in adb.attack(args.pin, layout, args.tactic, args.serial, swipe, args.dry_run):
        print("adb " + " ".join(cmd))


def main(argv=None) -> None:
    p = argparse.ArgumentParser(prog="nhip_attacker", description="Hacker simulator for Innate")
    sub = p.add_subparsers(dest="cmd", required=True)

    def api_args(sp):
        sp.add_argument("--api", default=os.environ.get("NHIP_API_URL", "http://localhost:8000"))
        sp.add_argument("--key", help="SDK key, defaults to NHIP_API_KEY")
        sp.add_argument("--ml-key", help="ML key for reading /v1/export, defaults to NHIP_ML_KEY")
        sp.add_argument("--pin", default="1593")
        sp.add_argument("--tactic", type=int, nargs="+", default=[1, 2, 3, 4], choices=[1, 2, 3, 4])
        sp.add_argument("--n", type=int, default=20)
        sp.add_argument("--seed", type=int, default=0)
        sp.add_argument("--human-source", default="api", help="api | synth | file:<path to .jsonl>")

    g = sub.add_parser("generate", help="generate labeled bot sessions as training data")
    api_args(g)
    g.add_argument("--user", required=True, help="user_id of the attacked account")
    g.set_defaults(func=cmd_generate)

    r = sub.add_parser("report", help="measure catch rate per tactic")
    api_args(r)
    r.add_argument("--target", help="user_id with enrolled rhythm (careful: scored sessions may update the template)")
    r.add_argument("--enroll-synth", action="store_true", help="create a synthetic enrolled account as the target")
    r.add_argument("--new-recipient", action="store_true")
    r.set_defaults(func=cmd_report)

    a = sub.add_parser("adb", help="real attack on a phone via adb")
    a.add_argument("--layout", required=True, help="layout.json of key coordinates (device pixels)")
    a.add_argument("--pin", default="1593")
    a.add_argument("--tactic", type=int, default=1, choices=[1, 2])
    a.add_argument("--serial", help="adb -s <serial> when several devices are attached")
    a.add_argument("--swipe", type=int, nargs=4, metavar=("X1", "Y1", "X2", "Y2"))
    a.add_argument("--dry-run", action="store_true", help="only print the commands, do not send")
    a.set_defaults(func=cmd_adb)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
