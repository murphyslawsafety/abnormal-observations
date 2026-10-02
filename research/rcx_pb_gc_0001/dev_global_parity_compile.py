#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

ART = Path("artifact")
PARITY = json.loads((ART / "DEV_PARITY_SCAN_v0.1.json").read_text(encoding="utf-8"))

def load_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

ctx_rows = load_csv(ART / "CONTEXT_PRETESTS_ALL.csv")
dev_rows = load_csv(ART / "DEVELOPMENT.csv")

ctx = defaultdict(list)
for r in ctx_rows:
    ctx[r["date"]].append(r)
for d in ctx:
    ctx[d].sort(key=lambda r: int(r["sequence_index"]))

def mode_int(vals):
    c = Counter(int(x) for x in vals)
    return min((-n, v) for v, n in c.items())[1]

state = {}
for d, rows in ctx.items():
    ws = mode_int([r["ws"] for r in rows])
    ps = mode_int([r["ps"] for r in rows])
    wpat = [0] * 70
    for pi, r in enumerate(rows):
        for pos in range(1, 6):
            wpat[int(r[f"ball{pos}"])] |= 1 << (pi * 5 + pos - 1)
    ppat = [0] * 27
    for pi, r in enumerate(rows):
        ppat[int(r["pb"])] |= 1 << pi
    state[d] = {"ws": ws, "ps": ps, "wpat": wpat, "ppat": ppat}

draws = {}
for r in dev_rows:
    if r["type_class"] == "Draw":
        draws[r["date"]] = {
            "white": [int(r[f"ball{i}"]) for i in range(1, 6)],
            "pb": int(r["pb"]),
        }

dates = sorted(draws)
n = len(dates)
cuts = [0, int(.2*n), int(.4*n), int(.6*n), int(.8*n), n]
folds = [(dates[:cuts[t]], dates[cuts[t]:cuts[t+1]]) for t in (2, 3, 4)]

# Frozen schedule; the declared source gap therefore breaks adjacency.
schedule = []
d = date(2015, 10, 7)
while d <= date(2026, 9, 28):
    if (d < date(2021, 8, 23) and d.weekday() in (2, 5)) or (
        d >= date(2021, 8, 23) and d.weekday() in (0, 2, 5)
    ):
        schedule.append(d.isoformat())
    d += timedelta(days=1)
sidx = {d:i for i,d in enumerate(schedule)}

def neighbor(d, offset):
    i = sidx[d] + offset
    if i < 0 or i >= len(schedule):
        return None
    nd = schedule[i]
    return nd if nd in state else None

def white_z(d, label, mask, mode):
    cur = state[d]
    z = ((cur["wpat"][label] & mask).bit_count() & 1)
    offsets = (-1, 1) if mode == "global" else (-1,)
    for off in offsets:
        nd = neighbor(d, off)
        if nd is not None and state[nd]["ws"] == cur["ws"]:
            z += ((state[nd]["wpat"][label] & mask).bit_count() & 1)
    return z

def pb_z(d, label, mask, mode):
    cur = state[d]
    z = ((cur["ppat"][label] & mask).bit_count() & 1)
    offsets = (-1, 1) if mode == "global" else (-1,)
    for off in offsets:
        nd = neighbor(d, off)
        if nd is not None and state[nd]["ps"] == cur["ps"]:
            z += ((state[nd]["ppat"][label] & mask).bit_count() & 1)
    return z

def white_stats(d, mask, mode):
    remaining = set(range(1, 70))
    out = []
    for chosen in draws[d]["white"]:
        zs = [white_z(d, label, mask, mode) for label in remaining]
        zc = white_z(d, chosen, mask, mode)
        out.append((zs, zc, len(remaining)))
        remaining.remove(chosen)
    return out

def pb_stats(d, mask, mode):
    zs = [pb_z(d, label, mask, mode) for label in range(1, 27)]
    zc = pb_z(d, draws[d]["pb"], mask, mode)
    return [(zs, zc, 26)]

def fit_beta(stats):
    beta = 0.0
    for _ in range(60):
        grad = 0.0
        hess = 0.0
        for zs, chosen_z, _risk in stats:
            ex = [math.exp(max(-10.0, min(10.0, beta * z))) for z in zs]
            denom = sum(ex)
            mean = sum(z * e for z, e in zip(zs, ex)) / denom
            mean2 = sum(z * z * e for z, e in zip(zs, ex)) / denom
            grad += chosen_z - mean
            hess -= mean2 - mean * mean
        if abs(hess) < 1e-12:
            break
        step = grad / hess
        beta -= step
        beta = max(-5.0, min(5.0, beta))
        if abs(step) < 1e-10:
            break
    return beta

def score(stats, beta):
    total = 0.0
    for zs, chosen_z, risk in stats:
        denom = sum(math.exp(beta * z) for z in zs)
        total += beta * chosen_z - math.log(denom) + math.log(risk)
    return total

# DEV parity stage froze these as the validation search pool.
white_candidates = PARITY["white_shared_top"][:10]
pb_candidates = PARITY["pb_shared_all"][:5]

white_results = {}
for w in white_candidates:
    mask = int(w["mask"])
    global_folds = []
    forward_folds = []
    betas = []
    for train, test in folds:
        beta = fit_beta([s for d in train for s in white_stats(d, mask, "global")])
        betas.append(beta)
        global_folds.append(score([s for d in test for s in white_stats(d, mask, "global")], beta) / len(test))
        # No refit: forward removes the +1 temporal side but uses the same beta.
        forward_folds.append(score([s for d in test for s in white_stats(d, mask, "forward")], beta) / len(test))
    white_results[mask] = {
        "mask": mask,
        "bits": w["bits"],
        "weight": w["weight"],
        "global_cv_folds": global_folds,
        "forward_cv_folds_same_beta": forward_folds,
        "global_cv_mean": sum(global_folds) / len(global_folds),
        "forward_cv_mean_same_beta": sum(forward_folds) / len(forward_folds),
        "global_train_fold_betas": betas,
    }

pb_results = {}
for p in pb_candidates:
    mask = int(p["mask"])
    global_folds = []
    forward_folds = []
    betas = []
    for train, test in folds:
        beta = fit_beta([s for d in train for s in pb_stats(d, mask, "global")])
        betas.append(beta)
        global_folds.append(score([s for d in test for s in pb_stats(d, mask, "global")], beta) / len(test))
        forward_folds.append(score([s for d in test for s in pb_stats(d, mask, "forward")], beta) / len(test))
    pb_results[mask] = {
        "mask": mask,
        "bits": p["bits"],
        "weight": p["weight"],
        "global_cv_folds": global_folds,
        "forward_cv_folds_same_beta": forward_folds,
        "global_cv_mean": sum(global_folds) / len(global_folds),
        "forward_cv_mean_same_beta": sum(forward_folds) / len(forward_folds),
        "global_train_fold_betas": betas,
    }

mdl_k = 2
mdl = 0.5 * mdl_k * math.log(n) / n
pairs = []
for wmask, w in white_results.items():
    for pmask, p in pb_results.items():
        global_folds = [a + b for a, b in zip(w["global_cv_folds"], p["global_cv_folds"])]
        forward_folds = [a + b for a, b in zip(w["forward_cv_folds_same_beta"], p["forward_cv_folds_same_beta"])]
        g = sum(global_folds) / len(global_folds)
        f = sum(forward_folds) / len(forward_folds)
        pairs.append({
            "model_id": f"GF2_W{wmask}_P{pmask}",
            "white_mask": wmask,
            "white_bits": w["bits"],
            "pb_mask": pmask,
            "pb_bits": p["bits"],
            "dev_global_cv_raw_nats_per_date": g,
            "dev_forward_cv_raw_same_beta_nats_per_date": f,
            "dev_global_cv_folds": global_folds,
            "dev_forward_cv_folds_same_beta": forward_folds,
            "mdl_scalar_parameter_count_k": mdl_k,
            "mdl_penalty_nats_per_date": mdl,
            "dev_global_score_minus_mdl": g - mdl,
            "dev_forward_raw_all_folds_positive": all(x > 0 for x in forward_folds),
            "dev_global_raw_all_folds_positive": all(x > 0 for x in global_folds),
        })

pairs.sort(key=lambda x: (
    -x["dev_global_score_minus_mdl"],
    -(min(x["dev_global_cv_folds"])),
    -(min(x["dev_forward_cv_folds_same_beta"])),
    x["model_id"],
))

advancing = [
    x for x in pairs
    if x["dev_global_score_minus_mdl"] > 0
    and x["dev_forward_cv_raw_same_beta_nats_per_date"] > 0
    and x["dev_global_raw_all_folds_positive"]
    and x["dev_forward_raw_all_folds_positive"]
]

payload = {
    "experiment": "RCX-PB-GC-0001",
    "stage": "DEV_GLOBAL_PARITY_COMPILATION",
    "version": "v0.1",
    "grammar": {
        "white_operator": "same frozen GF(2) incidence mask applied to target-day, immediately previous, and immediately next pretest blocks when ball-set identity matches",
        "pb_operator": "same construction on 4-bit PB pretest incidence",
        "global_feature": "z_current + z_previous + z_next",
        "forward_feature": "z_current + z_previous",
        "parameter_transfer": "fit one beta per game on global DEV grammar; forward score drops future term without refitting beta",
        "source_gap_rule": "missing scheduled physical block breaks adjacency",
    },
    "dev_target_dates": n,
    "mdl_scalar_parameter_count_k": mdl_k,
    "mdl_penalty_nats_per_date": mdl,
    "white_results": list(white_results.values()),
    "pb_results": list(pb_results.values()),
    "all_pairs": pairs,
    "advancement_rule": "global score-minus-MDL > 0; forward raw > 0; every DEV CV fold positive in both global and forward modes",
    "advancing_pairs": advancing,
}

(ART / "DEV_GLOBAL_PARITY_COMPILE_v0.1.json").write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

print(json.dumps({
    "stage": payload["stage"],
    "candidate_pairs": len(pairs),
    "advancing_count": len(advancing),
    "advancing_pairs": advancing,
    "top5_all_pairs": pairs[:5],
}, indent=2, sort_keys=True))
