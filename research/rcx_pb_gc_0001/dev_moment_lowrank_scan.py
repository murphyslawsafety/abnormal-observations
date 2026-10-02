#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

import numpy as np

ART = Path("artifact")
OUT = ART / "DEV_MOMENT_LOWRANK_SCAN_v0.1.json"
OUTCSV = ART / "DEV_MOMENT_LOWRANK_SHORTLIST_v0.1.csv"

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

def mode_int(values):
    c = Counter(int(x) for x in values)
    return min((-n, v) for v, n in c.items())[1]

# Fixed normalized event coordinates from v0.5.
T = np.array([-1.0, -1.0/3.0, 1.0/3.0, 1.0], dtype=float)
P = np.array([-1.0, -0.5, 0.0, 0.5, 1.0], dtype=float)

state = {}
for d, rows in ctx.items():
    if len(rows) != 4:
        raise SystemExit(f"pretest count != 4 on {d}: {len(rows)}")
    ws = mode_int([r["ws"] for r in rows])
    ps = mode_int([r["ps"] for r in rows])

    # label index 1..69 x 6 moments: C,T1,P1,T2,P2,TP
    wm = np.zeros((70, 6), dtype=float)
    for pi, r in enumerate(rows):
        for pos in range(1, 6):
            label = int(r[f"ball{pos}"])
            t = T[pi]
            p = P[pos - 1]
            wm[label] += np.array([1.0, t, p, t*t, p*p, t*p]) / 4.0

    # label index 1..26 x 3 moments: C,T1,T2
    pm = np.zeros((27, 3), dtype=float)
    for pi, r in enumerate(rows):
        label = int(r["pb"])
        t = T[pi]
        pm[label] += np.array([1.0, t, t*t]) / 4.0

    state[d] = {"ws": ws, "ps": ps, "white_m": wm, "pb_m": pm}

draws = {}
for r in dev_rows:
    if r["type_class"] == "Draw":
        draws[r["date"]] = {
            "white": [int(r[f"ball{i}"]) for i in range(1, 6)],
            "pb": int(r["pb"]),
        }

dates = sorted(draws)
N = len(dates)
if N != 878:
    raise SystemExit(f"unexpected DEV target count: {N}")

# Frozen schedule: source-unavailable date breaks adjacency because it is absent from state.
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

BASES = {
    "B1": {"white_idx": [0], "pb_idx": [0]},
    "B3": {"white_idx": [0, 1, 2], "pb_idx": [0, 1]},
    "B6": {"white_idx": [0, 1, 2, 3, 4, 5], "pb_idx": [0, 1, 2]},
}
RANKS = [1, 2, 3]
LAMBDAS = [0.1, 1.0, 10.0, 100.0]

def temporal_features(prev, cur, nxt, rank):
    modes = [
        (prev + cur + nxt) / 3.0,
        (nxt - prev) / 2.0,
        (prev - 2.0 * cur + nxt) / 4.0,
    ]
    return np.concatenate(modes[:rank], axis=1)

# Cache full label-feature matrices for each date/config/mode.
feature_cache = {}

def get_features(d, game, basis, rank, mode):
    key = (d, game, basis, rank, mode)
    if key in feature_cache:
        return feature_cache[key]

    s = state[d]
    if game == "white":
        idxs = BASES[basis]["white_idx"]
        cur = s["white_m"][:, idxs]
        zero = np.zeros_like(cur)
        pdate = neighbor(d, -1)
        ndate = neighbor(d, +1)
        prev = (
            state[pdate]["white_m"][:, idxs]
            if pdate is not None and state[pdate]["ws"] == s["ws"]
            else zero
        )
        nxt = (
            state[ndate]["white_m"][:, idxs]
            if mode == "global"
            and ndate is not None
            and state[ndate]["ws"] == s["ws"]
            else zero
        )
    else:
        idxs = BASES[basis]["pb_idx"]
        cur = s["pb_m"][:, idxs]
        zero = np.zeros_like(cur)
        pdate = neighbor(d, -1)
        ndate = neighbor(d, +1)
        prev = (
            state[pdate]["pb_m"][:, idxs]
            if pdate is not None and state[pdate]["ps"] == s["ps"]
            else zero
        )
        nxt = (
            state[ndate]["pb_m"][:, idxs]
            if mode == "global"
            and ndate is not None
            and state[ndate]["ps"] == s["ps"]
            else zero
        )

    X = temporal_features(prev, cur, nxt, rank)
    feature_cache[key] = X
    return X

# Choice sets are tuples (X risk-set matrix, chosen row index within X).
def choice_sets(target_dates, game, basis, rank, mode):
    sets = []
    if game == "white":
        for d in target_dates:
            full = get_features(d, game, basis, rank, mode)
            remaining = list(range(1, 70))
            for chosen in draws[d]["white"]:
                X = full[remaining]
                chosen_index = remaining.index(chosen)
                sets.append((X, chosen_index))
                remaining.pop(chosen_index)
    else:
        labels = list(range(1, 27))
        for d in target_dates:
            full = get_features(d, game, basis, rank, mode)
            X = full[labels]
            chosen_index = draws[d]["pb"] - 1
            sets.append((X, chosen_index))
    return sets

def logsumexp(z):
    m = float(np.max(z))
    return m + math.log(float(np.exp(z - m).sum()))

def fit_conditional_logit(sets, lam):
    p = sets[0][0].shape[1]
    beta = np.zeros(p, dtype=float)
    eye = np.eye(p)

    for _ in range(50):
        grad = -lam * beta
        hess = -lam * eye.copy()

        for X, chosen_index in sets:
            eta = X @ beta
            m = float(np.max(eta))
            w = np.exp(eta - m)
            probs = w / w.sum()
            mean = probs @ X
            centered = X - mean
            cov = (centered.T * probs) @ centered
            grad += X[chosen_index] - mean
            hess -= cov

        # Newton step for maximization; hessian is negative-definite after ridge.
        try:
            step = np.linalg.solve(hess, grad)
        except np.linalg.LinAlgError:
            step = np.linalg.lstsq(hess, grad, rcond=None)[0]

        # Conservative damping for numerical stability.
        max_abs = float(np.max(np.abs(step))) if step.size else 0.0
        if max_abs > 1.0:
            step = step / max_abs
        beta -= step
        beta = np.clip(beta, -8.0, 8.0)

        if float(np.max(np.abs(step))) < 1e-8:
            break

    return beta

def score_sets(sets, beta):
    total = 0.0
    for X, chosen_index in sets:
        eta = X @ beta
        total += float(eta[chosen_index]) - logsumexp(eta) + math.log(X.shape[0])
    return total

cuts = [0, int(0.2*N), int(0.4*N), int(0.6*N), int(0.8*N), N]
folds = [(dates[:cuts[t]], dates[cuts[t]:cuts[t+1]]) for t in (2, 3, 4)]

results = []
for basis in ("B1", "B3", "B6"):
    for rank in RANKS:
        white_p = len(BASES[basis]["white_idx"]) * rank
        pb_p = len(BASES[basis]["pb_idx"]) * rank
        k = white_p + pb_p
        mdl = 0.5 * k * math.log(N) / N

        for lam in LAMBDAS:
            global_fold = []
            forward_fold = []
            fold_betas = []

            for train_dates, test_dates in folds:
                white_train = choice_sets(train_dates, "white", basis, rank, "global")
                pb_train = choice_sets(train_dates, "pb", basis, rank, "global")
                bw = fit_conditional_logit(white_train, lam)
                bp = fit_conditional_logit(pb_train, lam)

                white_test_global = choice_sets(test_dates, "white", basis, rank, "global")
                pb_test_global = choice_sets(test_dates, "pb", basis, rank, "global")
                white_test_forward = choice_sets(test_dates, "white", basis, rank, "forward")
                pb_test_forward = choice_sets(test_dates, "pb", basis, rank, "forward")

                g = (
                    score_sets(white_test_global, bw)
                    + score_sets(pb_test_global, bp)
                ) / len(test_dates)
                f = (
                    score_sets(white_test_forward, bw)
                    + score_sets(pb_test_forward, bp)
                ) / len(test_dates)

                global_fold.append(float(g))
                forward_fold.append(float(f))
                fold_betas.append({
                    "white": [float(x) for x in bw],
                    "pb": [float(x) for x in bp],
                })

            gmean = sum(global_fold) / len(global_fold)
            fmean = sum(forward_fold) / len(forward_fold)
            score_minus_mdl = gmean - mdl
            advances = (
                gmean > 0
                and score_minus_mdl > 0
                and fmean > 0
                and all(x > 0 for x in global_fold)
                and all(x > 0 for x in forward_fold)
            )

            results.append({
                "model_id": f"MOM_{basis}_R{rank}_L{lam:g}",
                "basis": basis,
                "temporal_rank": rank,
                "lambda": lam,
                "white_parameter_count": white_p,
                "pb_parameter_count": pb_p,
                "scalar_parameter_count_k": k,
                "mdl_penalty_nats_per_date": mdl,
                "dev_global_cv_folds": global_fold,
                "dev_forward_cv_folds_same_beta": forward_fold,
                "dev_global_cv_raw_nats_per_date": gmean,
                "dev_forward_cv_raw_same_beta_nats_per_date": fmean,
                "dev_global_score_minus_mdl": score_minus_mdl,
                "dev_advance": advances,
                "fold_betas": fold_betas,
            })

results.sort(key=lambda x: (
    -x["dev_global_score_minus_mdl"],
    -x["dev_forward_cv_raw_same_beta_nats_per_date"],
    x["scalar_parameter_count_k"],
    x["model_id"],
))

advancing = [x for x in results if x["dev_advance"]][:3]

payload = {
    "experiment": "RCX-PB-GC-0001",
    "stage": "DEV_MOMENT_LOWRANK_DISCOVERY",
    "execution_amendment": "v0.5",
    "data_policy": "development draw outcomes only; all-split pretest-only context; no validation/sealed draw outcomes used",
    "development_target_dates": N,
    "bases": BASES,
    "temporal_ranks": RANKS,
    "l2_lambda_grid": LAMBDAS,
    "candidate_count": len(results),
    "advancement_rule": "mean global raw >0; global raw-MDL >0; mean forward raw >0; every global and forward chronological DEV fold >0",
    "results": results,
    "advancing_candidates": advancing,
    "advancing_count": len(advancing),
}
OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

with OUTCSV.open("w", newline="", encoding="utf-8") as f:
    fields = [
        "rank", "model_id", "basis", "temporal_rank", "lambda",
        "scalar_parameter_count_k", "mdl_penalty_nats_per_date",
        "dev_global_cv_raw_nats_per_date",
        "dev_forward_cv_raw_same_beta_nats_per_date",
        "dev_global_score_minus_mdl", "dev_advance"
    ]
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for i, r in enumerate(results, 1):
        w.writerow({k: (i if k == "rank" else r[k]) for k in fields})

print(json.dumps({
    "stage": payload["stage"],
    "candidate_count": len(results),
    "advancing_count": len(advancing),
    "advancing_candidates": advancing,
    "top10": results[:10],
}, indent=2, sort_keys=True))
