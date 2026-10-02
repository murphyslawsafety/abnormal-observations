#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

ART = Path("artifact")
CTX = ART / "CONTEXT_PRETESTS_ALL.csv"
DEV = ART / "DEVELOPMENT.csv"
OUT_JSON = ART / "DEV_CAUSAL_STATE_SCAN_v0.1.json"
OUT_CSV = ART / "DEV_CAUSAL_STATE_CANDIDATES_v0.1.csv"

if not CTX.exists() or not DEV.exists():
    raise SystemExit("qualification artifacts missing")

def load_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

ctx_rows = load_csv(CTX)
dev_rows = load_csv(DEV)

# Build pretest-only context for every observable physical date.
ctx_by_date = defaultdict(list)
for r in ctx_rows:
    ctx_by_date[r["date"]].append(r)
for d in ctx_by_date:
    ctx_by_date[d].sort(key=lambda r: int(r["sequence_index"]))

# Development draw targets only. No validation/sealed draw outcome is read.
dev_draws = {}
for r in dev_rows:
    if r["type_class"] == "Draw":
        dev_draws[r["date"]] = {
            "white": [int(r[f"ball{i}"]) for i in range(1, 6)],
            "pb": int(r["pb"]),
        }

dev_dates = sorted(dev_draws)
if len(dev_dates) < 100:
    raise SystemExit(f"too few development targets: {len(dev_dates)}")

# Frozen schedule index including the source-unavailable date. Neighbor lookup therefore
# naturally breaks at the declared missing physical block.
START = date(2015, 10, 7)
CUTOFF = date(2026, 9, 28)
schedule = []
d = START
while d <= CUTOFF:
    if (d < date(2021, 8, 23) and d.weekday() in (2, 5)) or (
        d >= date(2021, 8, 23) and d.weekday() in (0, 2, 5)
    ):
        schedule.append(d.isoformat())
    d += timedelta(days=1)
idx = {d: i for i, d in enumerate(schedule)}

def mode_int(values):
    c = Counter(int(v) for v in values)
    return min((-n, v) for v, n in c.items())[1]

# Per-date object-state arrays derived only from official pretests.
state = {}
for d, rows in ctx_by_date.items():
    if len(rows) != 4:
        raise SystemExit(f"context pretest count !=4 on {d}: {len(rows)}")

    ws = mode_int([r["ws"] for r in rows])
    ps = mode_int([r["ps"] for r in rows])

    w_seq = [0] * 70
    w_pos = [0] * 70
    w_count = [0] * 70
    for pi, r in enumerate(rows):
        for pos in range(1, 6):
            b = int(r[f"ball{pos}"])
            w_seq[b] |= (1 << pi)
            w_pos[b] |= (1 << (pos - 1))
            w_count[b] += 1

    pb_seq = [0] * 27
    pb_count = [0] * 27
    for pi, r in enumerate(rows):
        b = int(r["pb"])
        pb_seq[b] |= (1 << pi)
        pb_count[b] += 1

    state[d] = {
        "ws": ws, "ps": ps,
        "w_seq": w_seq, "w_pos": w_pos, "w_count": w_count,
        "pb_seq": pb_seq, "pb_count": pb_count,
    }

def sched_neighbor(d, offset):
    i = idx[d] + offset
    if i < 0 or i >= len(schedule):
        return None
    nd = schedule[i]
    return nd if nd in state else None

def bcount(x):
    if x <= 0:
        return 0
    if x == 1:
        return 1
    return 2

def directional_counts(d, label, game, direction, memory):
    """Return same-set recent/future count bins; hard-stop across missing scheduled blocks."""
    base = state[d]
    step = -1 if direction == "forward" else 1
    out = []
    for k in range(1, memory + 1):
        nd = sched_neighbor(d, step * k)
        if nd is None:
            out.extend([-1] * (memory - len(out)))
            break
        other = state[nd]
        if game == "white":
            if other["ws"] != base["ws"]:
                out.append(-1)
            else:
                out.append(bcount(other["w_count"][label]))
        else:
            if other["ps"] != base["ps"]:
                out.append(-1)
            else:
                out.append(bcount(other["pb_count"][label]))
    while len(out) < memory:
        out.append(-1)
    return tuple(out)

def state_key(d, label, game, family, direction):
    s = state[d]
    if game == "white":
        count = s["w_count"][label]
        seq = s["w_seq"][label]
        pos = s["w_pos"][label]
    else:
        count = s["pb_count"][label]
        seq = s["pb_seq"][label]
        pos = 0

    if family == "COUNT":
        return (count,)
    if family == "SEQ":
        return (seq,)
    if family == "POS":
        return (pos,) if game == "white" else (seq,)
    if family == "SEQPOS":
        return (seq, pos) if game == "white" else (seq,)
    if family == "RECENT1":
        return ((seq, pos) if game == "white" else (seq,)) + directional_counts(d, label, game, direction, 1)
    if family == "RECENT2":
        return ((seq, pos) if game == "white" else (seq,)) + directional_counts(d, label, game, direction, 2)
    raise ValueError(family)

FAMILIES = [
    {"family": "COUNT", "bidirectional": False},
    {"family": "SEQ", "bidirectional": False},
    {"family": "POS", "bidirectional": False},
    {"family": "SEQPOS", "bidirectional": False},
    {"family": "RECENT1", "bidirectional": True},
    {"family": "RECENT2", "bidirectional": True},
]
ALPHAS = [0.25, 1.0, 4.0, 16.0]

def fit_tables(train_dates, family, direction, alpha):
    w_exp = [Counter() for _ in range(5)]
    w_chosen = [Counter() for _ in range(5)]
    pb_exp = Counter()
    pb_chosen = Counter()

    for d in train_dates:
        actual = dev_draws[d]["white"]
        remaining = set(range(1, 70))
        for pos, chosen in enumerate(actual):
            for label in remaining:
                key = state_key(d, label, "white", family, direction)
                w_exp[pos][key] += 1
            ck = state_key(d, chosen, "white", family, direction)
            w_chosen[pos][ck] += 1
            remaining.remove(chosen)

        chosen_pb = dev_draws[d]["pb"]
        for label in range(1, 27):
            key = state_key(d, label, "pb", family, direction)
            pb_exp[key] += 1
        pb_chosen[state_key(d, chosen_pb, "pb", family, direction)] += 1

    def make_weight(exp, chosen, base_rate):
        table = {}
        for key, n in exp.items():
            y = chosen.get(key, 0)
            rate = (y + alpha * base_rate) / (n + alpha)
            table[key] = max(rate / base_rate, 1e-12)
        return table

    return {
        "white": [
            make_weight(w_exp[pos], w_chosen[pos], 1.0 / (69 - pos))
            for pos in range(5)
        ],
        "pb": make_weight(pb_exp, pb_chosen, 1.0 / 26.0),
        "k": sum(max(0, len(x) - 1) for x in w_exp) + max(0, len(pb_exp) - 1),
    }

def score_date(d, family, forward_table, reverse_table=None):
    actual = dev_draws[d]["white"]
    remaining = list(range(1, 70))
    logp_forward = 0.0
    logp_global = 0.0

    for pos, chosen in enumerate(actual):
        wf = []
        wg = []
        for label in remaining:
            kf = state_key(d, label, "white", family, "forward")
            f = forward_table["white"][pos].get(kf, 1.0)
            if reverse_table is None:
                g = f
            else:
                kr = state_key(d, label, "white", family, "reverse")
                r = reverse_table["white"][pos].get(kr, 1.0)
                g = f * r
            wf.append(f)
            wg.append(g)
        ci = remaining.index(chosen)
        logp_forward += math.log(wf[ci] / sum(wf))
        logp_global += math.log(wg[ci] / sum(wg))
        remaining.pop(ci)

    chosen_pb = dev_draws[d]["pb"]
    labels = list(range(1, 27))
    wf = []
    wg = []
    for label in labels:
        kf = state_key(d, label, "pb", family, "forward")
        f = forward_table["pb"].get(kf, 1.0)
        if reverse_table is None:
            g = f
        else:
            kr = state_key(d, label, "pb", family, "reverse")
            r = reverse_table["pb"].get(kr, 1.0)
            g = f * r
        wf.append(f)
        wg.append(g)
    ci = chosen_pb - 1
    logp_forward += math.log(wf[ci] / sum(wf))
    logp_global += math.log(wg[ci] / sum(wg))

    baseline = -sum(math.log(69 - pos) for pos in range(5)) - math.log(26)
    return logp_forward - baseline, logp_global - baseline

# Three expanding-window chronological DEV folds: 40->60, 60->80, 80->100%.
n = len(dev_dates)
cuts = [0, int(0.2*n), int(0.4*n), int(0.6*n), int(0.8*n), n]
folds = []
for test_bin in (2, 3, 4):
    train = dev_dates[:cuts[test_bin]]
    test = dev_dates[cuts[test_bin]:cuts[test_bin+1]]
    folds.append((train, test))

results = []
for fam in FAMILIES:
    family = fam["family"]
    for alpha in ALPHAS:
        fwd_scores = []
        global_scores = []
        for train, test in folds:
            ft = fit_tables(train, family, "forward", alpha)
            rt = fit_tables(train, family, "reverse", alpha) if fam["bidirectional"] else None
            for d in test:
                sf, sg = score_date(d, family, ft, rt)
                fwd_scores.append(sf)
                global_scores.append(sg)

        full_f = fit_tables(dev_dates, family, "forward", alpha)
        full_r = fit_tables(dev_dates, family, "reverse", alpha) if fam["bidirectional"] else None
        k = full_f["k"] + (full_r["k"] if full_r is not None else 0)
        N = len(dev_dates)
        mdl = 0.5 * k * math.log(N) / N
        fmean = sum(fwd_scores) / len(fwd_scores)
        gmean = sum(global_scores) / len(global_scores)
        results.append({
            "model_id": f"CS_{family}_A{alpha:g}",
            "family": family,
            "alpha": alpha,
            "bidirectional": fam["bidirectional"],
            "dev_cv_scored_dates": len(global_scores),
            "dev_cv_forward_logscore_improvement_nats_per_date": fmean,
            "dev_cv_global_logscore_improvement_nats_per_date": gmean,
            "full_dev_parameter_count_k": k,
            "mdl_penalty_nats_per_date": mdl,
            "dev_selection_score_global_minus_mdl": gmean - mdl,
            "dev_selection_score_forward_minus_mdl": fmean - mdl,
        })

results.sort(key=lambda r: (-r["dev_selection_score_global_minus_mdl"], r["full_dev_parameter_count_k"], r["model_id"]))
payload = {
    "experiment": "RCX-PB-GC-0001",
    "stage": "DEV_CAUSAL_STATE_DISCOVERY",
    "version": "v0.1",
    "data_policy": "development draw outcomes only; all-split pretest-only context; no validation/sealed draw outcomes",
    "development_target_dates": len(dev_dates),
    "cv_design": "three expanding-window chronological folds: first 40%->next20%, first60%->next20%, first80%->last20%",
    "baseline": "ordered fair without-replacement white draw times uniform 1/26 PB",
    "families": FAMILIES,
    "alphas": ALPHAS,
    "results": results,
}
OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

fields = list(results[0].keys())
with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(results)

print(json.dumps({
    "stage": payload["stage"],
    "development_target_dates": len(dev_dates),
    "candidate_count": len(results),
    "top5": results[:5],
}, indent=2, sort_keys=True))
