"""E21: does normalizing rhythm by KEY PAIR (digraph) help recognize the owner when the test sentence differs from the enrollment sentence?

Reason: Innate Challenge changes the sentence every time, and the time between two keys depends on the key pair ("th" fast, "qx" slow). E13 used the raw log interval, so part of the
difference is due to the sentence CONTENT. Here we subtract the population mean of each key pair (prior from a separate group of people, disjoint from the evaluation group) and divide by the std
(z = (log gap - mu_ab) / sd_ab), with a fallback by character class when the pair is rare. Same protocol as E13: enroll 3 sentences, test other sentences, cut at the first n keys, shrink the variance toward the population.
The idea is in the same family as the relative measure of Gunetti & Picardi (TISSEC 2005) and TypeNet/TypeFormer learning per key pair.
Real people only, no bots (the team's bot data has no characters). Data needed: research/data/aalto_note_keys.jsonl (aalto_note_chars.py; gitignored, contains the letters of the sample sentences).
Run: python experiments/e21_digraph_norm.py
"""
import json
import random
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parents[2]
NS, SEED, K, NU, BOOT, MINC = (10, 20, 30), 0, 3, 5, 80, 30
rng = random.Random(SEED)


def kc(ch):  # fallback character class
    return "_" if ch.isspace() else "a" if ch.isalpha() else "o"


by_p = defaultdict(list)  # person -> [list (t, ch)]
for line in open(ROOT / "research/data/aalto_note_keys.jsonl"):
    r = json.loads(line)
    ks = [(e[0], e[3]) for e in r["events"] if e[1] == "key"]
    if len(ks) >= max(NS) + 1:
        by_p[r["participant"]].append(sorted(ks))
people = [p for p, v in by_p.items() if len(v) >= 8]
rng.shuffle(people)
prior_p, eval_p = people[:300], people[300:1300]
print(f"{len(people)} people; prior {len(prior_p)}, evaluation {len(eval_p)}")

# key-pair statistics from the prior group (interval measured on adjacent keys, 20 ms .. 2 s)
pair, cls_pair = defaultdict(list), defaultdict(list)
for p in prior_p:
    for s in by_p[p]:
        for (t0, a), (t1, b) in zip(s, s[1:]):
            g = t1 - t0
            if 20 <= g <= 2000:
                pair[(a, b)].append(np.log(g)); cls_pair[(kc(a), kc(b))].append(np.log(g))
stat = {k: (np.mean(v), np.std(v) + 1e-6) for k, v in pair.items() if len(v) >= MINC}
cstat = {k: (np.mean(v), np.std(v) + 1e-6) for k, v in cls_pair.items()}
print(f"{len(stat)} key pairs with enough samples (>= {MINC}); covers {np.mean([ (a,b) in stat for s in by_p[prior_p[0]] for (_,a),(_,b) in zip(s,s[1:])]):.0%} of the pairs of one prior person")


def logs(s, n):
    return np.log(np.maximum(np.diff([t for t, _ in s[:n]]), 1.0))


def zs(s, n):
    out = []
    for (t0, a), (t1, b) in zip(s[:n], s[1:n]):
        mu, sd = stat.get((a, b)) or cstat[(kc(a), kc(b))]
        out.append((np.log(max(t1 - t0, 1.0)) - mu) / sd)
    return np.array(out)


def six(x):
    return [x.mean(), x.std(), np.median(x), np.percentile(x, 10), np.percentile(x, 90), np.abs(np.diff(x)).mean()]


FE = {
    "E13 raw (6 log-interval features)": lambda s, n: np.array(six(logs(s, n))),
    "digraph-normalized (6 z features)": lambda s, n: np.array(six(zs(s, n))),
    "overall speed only (mean z, 1 feature)": lambda s, n: np.array([zs(s, n).mean()]),
    "raw + normalized (12 features)": lambda s, n: np.concatenate([six(logs(s, n)), six(zs(s, n))]),
}


def metrics(gen, imp):
    gen, imp = np.asarray(gen), np.asarray(imp)
    ths = np.unique(np.quantile(np.concatenate([gen, imp]), np.linspace(0, 1, 300)))
    frr = np.array([(gen > t).mean() for t in ths]); far = np.array([(imp <= t).mean() for t in ths])
    i = np.argmin(np.abs(frr - far))
    return np.array([(frr[i] + far[i]) / 2, (imp <= np.quantile(gen, 0.95)).mean()])


L = ["# E21 — digraph-normalized typing rhythm, recognizing the owner when the test sentence differs from the enrollment sentence (Aalto, real people)", "",
     "E13 protocol: enroll 3 sentences, test other sentences, impostor = another person's sentence; key-pair prior and variance from a separate group of people. EER and FAR@FRR5%, bootstrap confidence intervals by person.", "",
     "| Features | n keys | EER | FAR @ FRR 5% |", "|---|---|---|---|"]
for name, fe in FE.items():
    for n in NS:
        pv = np.mean([np.var(np.array([fe(s, n) for s in by_p[p]]), axis=0, ddof=1) for p in prior_p], axis=0)
        per = {}
        for p in eval_p:
            ss = by_p[p]; idx = list(range(len(ss))); rng.shuffle(idx)
            enr = np.array([fe(ss[i], n) for i in idx[:K]]); mu = enr.mean(0)
            sd = np.sqrt(((K - 1) * enr.var(0, ddof=1) + NU * pv) / (K - 1 + NU))
            sc = lambda f: float(np.mean(np.abs(f - mu) / sd))  # noqa: E731
            per[p] = ([sc(fe(ss[i], n)) for i in idx[K:K + 5]], [sc(fe(rng.choice(by_p[q]), n)) for q in rng.sample(eval_p, 12) if q != p])
        ps = sorted(per)
        est = metrics(sum((per[p][0] for p in ps), []), sum((per[p][1] for p in ps), []))
        bs = []
        for _ in range(BOOT):
            r = [rng.choice(ps) for _ in ps]
            bs.append(metrics(sum((per[p][0] for p in r), []), sum((per[p][1] for p in r), [])))
        lo, hi = np.quantile(bs, 0.025, axis=0), np.quantile(bs, 0.975, axis=0)
        L.append(f"| {name} | {n} | {est[0]:.3f} [{lo[0]:.3f}, {hi[0]:.3f}] | {est[1]:.3f} [{lo[1]:.3f}, {hi[1]:.3f}] |")
        print(L[-1], flush=True)
(ROOT / "research/results/e21_digraph_norm.md").write_text("\n".join(L) + "\n", encoding="utf-8")
