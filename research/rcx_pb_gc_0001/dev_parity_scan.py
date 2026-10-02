#!/usr/bin/env python3
from __future__ import annotations

import csv
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

ART = Path("artifact")
CTX = ART / "CONTEXT_PRETESTS_ALL.csv"
DEV = ART / "DEVELOPMENT.csv"
OUT = ART / "DEV_PARITY_SCAN_v0.1.json"
OUTCSV = ART / "DEV_PARITY_SHORTLIST_v0.1.csv"

def load_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

ctx_rows = load_csv(CTX)
dev_rows = load_csv(DEV)

ctx_by_date = defaultdict(list)
for r in ctx_rows:
    ctx_by_date[r["date"]].append(r)
for d in ctx_by_date:
    ctx_by_date[d].sort(key=lambda r: int(r["sequence_index"]))

white_pattern = {}
pb_pattern = {}
white_patterns_all = {0}
pb_patterns_all = {0}

for d, rows in ctx_by_date.items():
    w = [0] * 70
    for pretest_index, r in enumerate(rows):
        for pos in range(1, 6):
            label = int(r[f"ball{pos}"])
            bit = pretest_index * 5 + (pos - 1)
            w[label] |= 1 << bit
    white_pattern[d] = w
    white_patterns_all.update(w[1:])

    p = [0] * 27
    for pretest_index, r in enumerate(rows):
        label = int(r["pb"])
        p[label] |= 1 << pretest_index
    pb_pattern[d] = p
    pb_patterns_all.update(p[1:])

dev_draws = {}
for r in dev_rows:
    if r["type_class"] == "Draw":
        dev_draws[r["date"]] = {
            "white": [int(r[f"ball{i}"]) for i in range(1, 6)],
            "pb": int(r["pb"]),
        }

dates = sorted(dev_draws)
n_dates = len(dates)
cuts = [0, int(.2*n_dates), int(.4*n_dates), int(.6*n_dates), int(.8*n_dates), n_dates]
folds = [(dates[:cuts[t]], dates[cuts[t]:cuts[t+1]]) for t in (2, 3, 4)]

patterns = sorted(white_patterns_all)
pattern_index = {x:i for i,x in enumerate(patterns)}
pb_patterns = sorted(pb_patterns_all)
pb_pattern_index = {x:i for i,x in enumerate(pb_patterns)}

# GF(2) provenance: 20 binary white-incidence coordinates = 4 pretests x 5 extraction positions.
white_masks = []
for weight in (1, 2, 3, 4):
    for comb in itertools.combinations(range(20), weight):
        mask = sum(1 << i for i in comb)
        white_masks.append({"mask": mask, "weight": weight, "bits": list(comb)})

pb_masks = [
    {"mask": m, "weight": int(m.bit_count()), "bits": [i for i in range(4) if (m >> i) & 1]}
    for m in range(1, 16)
]

P = np.empty((len(white_masks), len(patterns)), dtype=np.uint8)
for i, spec in enumerate(white_masks):
    mask = spec["mask"]
    P[i, :] = [((x & mask).bit_count() & 1) for x in patterns]

PP = np.empty((len(pb_masks), len(pb_patterns)), dtype=np.uint8)
for i, spec in enumerate(pb_masks):
    mask = spec["mask"]
    PP[i, :] = [((x & mask).bit_count() & 1) for x in pb_patterns]

# Risk-set representations for each development target.
white_risk = {}
pb_risk = {}
for d in dates:
    actual = dev_draws[d]["white"]
    remaining = set(range(1, 70))
    per_pos = []
    pat = white_pattern[d]
    for pos, chosen in enumerate(actual):
        counts = np.zeros(len(patterns), dtype=np.int16)
        for label in remaining:
            counts[pattern_index[pat[label]]] += 1
        per_pos.append((counts, pattern_index[pat[chosen]]))
        remaining.remove(chosen)
    white_risk[d] = per_pos

    ppat = pb_pattern[d]
    counts = np.zeros(len(pb_patterns), dtype=np.int16)
    for label in range(1, 27):
        counts[pb_pattern_index[ppat[label]]] += 1
    pb_risk[d] = (counts, pb_pattern_index[ppat[dev_draws[d]["pb"]]])

# Stage A screen: position-specific two-state hazard, alpha fixed at 4.0.
SCREEN_ALPHA = 4.0

def screen_white():
    total = np.zeros(len(white_masks), dtype=float)
    fold_scores = []
    total_dates = 0
    for train, test in folds:
        tables = []
        for pos in range(5):
            exp = np.zeros(len(patterns), dtype=np.int64)
            chosen = np.zeros(len(patterns), dtype=np.int64)
            for d in train:
                cnt, ci = white_risk[d][pos]
                exp += cnt
                chosen[ci] += 1
            e1 = P @ exp
            y1 = P @ chosen
            e0 = exp.sum() - e1
            y0 = chosen.sum() - y1
            base = 1.0 / (69 - pos)
            w1 = (y1 + SCREEN_ALPHA * base) / (e1 + SCREEN_ALPHA) / base
            w0 = (y0 + SCREEN_ALPHA * base) / (e0 + SCREEN_ALPHA) / base
            tables.append((w0, w1))

        fold_total = np.zeros(len(white_masks), dtype=float)
        for d in test:
            for pos in range(5):
                cnt, ci = white_risk[d][pos]
                n1 = P @ cnt
                n0 = cnt.sum() - n1
                actual_parity = P[:, ci]
                w0, w1 = tables[pos]
                denom = n0 * w0 + n1 * w1
                actual_weight = np.where(actual_parity == 1, w1, w0)
                fold_total += np.log(np.maximum(actual_weight / denom, 1e-300)) + math.log(69 - pos)
        total += fold_total
        fold_scores.append(fold_total / len(test))
        total_dates += len(test)
    return total / total_dates, fold_scores

def screen_pb():
    total = np.zeros(len(pb_masks), dtype=float)
    fold_scores = []
    total_dates = 0
    for train, test in folds:
        exp = np.zeros(len(pb_patterns), dtype=np.int64)
        chosen = np.zeros(len(pb_patterns), dtype=np.int64)
        for d in train:
            cnt, ci = pb_risk[d]
            exp += cnt
            chosen[ci] += 1
        e1 = PP @ exp
        y1 = PP @ chosen
        e0 = exp.sum() - e1
        y0 = chosen.sum() - y1
        base = 1.0 / 26.0
        w1 = (y1 + SCREEN_ALPHA * base) / (e1 + SCREEN_ALPHA) / base
        w0 = (y0 + SCREEN_ALPHA * base) / (e0 + SCREEN_ALPHA) / base

        fold_total = np.zeros(len(pb_masks), dtype=float)
        for d in test:
            cnt, ci = pb_risk[d]
            n1 = PP @ cnt
            n0 = cnt.sum() - n1
            actual_parity = PP[:, ci]
            denom = n0 * w0 + n1 * w1
            actual_weight = np.where(actual_parity == 1, w1, w0)
            fold_total += np.log(np.maximum(actual_weight / denom, 1e-300)) + math.log(26)
        total += fold_total
        fold_scores.append(fold_total / len(test))
        total_dates += len(test)
    return total / total_dates, fold_scores

white_screen, white_screen_folds = screen_white()
pb_screen, pb_screen_folds = screen_pb()

white_top_idx = np.argsort(-white_screen)[:32]
pb_top_idx = np.argsort(-pb_screen)[:15]

# Stage B: refit each screened grammar as one shared conditional-logit coefficient beta.
def white_choice_stats(d, mask):
    pat = white_pattern[d]
    remaining = set(range(1, 70))
    out = []
    for chosen in dev_draws[d]["white"]:
        n1 = sum(((pat[label] & mask).bit_count() & 1) for label in remaining)
        y = ((pat[chosen] & mask).bit_count() & 1)
        out.append((len(remaining), n1, y))
        remaining.remove(chosen)
    return out

def pb_choice_stats(d, mask):
    pat = pb_pattern[d]
    n1 = sum(((pat[label] & mask).bit_count() & 1) for label in range(1, 27))
    y = ((pat[dev_draws[d]["pb"]] & mask).bit_count() & 1)
    return [(26, n1, y)]

def fit_beta(stats):
    beta = 0.0
    for _ in range(50):
        grad = 0.0
        hess = 0.0
        eb = math.exp(max(-10.0, min(10.0, beta)))
        for risk, n1, y in stats:
            n0 = risk - n1
            denom = n0 + n1 * eb
            q = (n1 * eb / denom) if denom else 0.0
            grad += y - q
            hess -= q * (1.0 - q)
        if abs(hess) < 1e-12:
            break
        step = grad / hess
        beta -= step
        beta = max(-5.0, min(5.0, beta))
        if abs(step) < 1e-10:
            break
    return beta

def score_stats(stats, beta):
    eb = math.exp(beta)
    total = 0.0
    for risk, n1, y in stats:
        n0 = risk - n1
        denom = n0 + n1 * eb
        total += beta * y - math.log(denom) + math.log(risk)
    return total

white_shared = []
for idxw in white_top_idx:
    spec = white_masks[int(idxw)]
    mask = spec["mask"]
    fold = []
    betas = []
    for train, test in folds:
        beta = fit_beta([s for d in train for s in white_choice_stats(d, mask)])
        betas.append(beta)
        fold.append(score_stats([s for d in test for s in white_choice_stats(d, mask)], beta) / len(test))
    white_shared.append({
        **spec,
        "screen_mean_nats_per_date": float(white_screen[idxw]),
        "screen_fold_nats_per_date": [float(x[idxw]) for x in white_screen_folds],
        "shared_beta_cv_mean_nats_per_date": float(sum(fold) / len(fold)),
        "shared_beta_cv_fold_nats_per_date": [float(x) for x in fold],
        "shared_beta_train_fold_estimates": [float(x) for x in betas],
    })
white_shared.sort(key=lambda x: (-x["shared_beta_cv_mean_nats_per_date"], x["weight"], x["mask"]))

pb_shared = []
for idxp in pb_top_idx:
    spec = pb_masks[int(idxp)]
    mask = spec["mask"]
    fold = []
    betas = []
    for train, test in folds:
        beta = fit_beta([s for d in train for s in pb_choice_stats(d, mask)])
        betas.append(beta)
        fold.append(score_stats([s for d in test for s in pb_choice_stats(d, mask)], beta) / len(test))
    pb_shared.append({
        **spec,
        "screen_mean_nats_per_date": float(pb_screen[idxp]),
        "screen_fold_nats_per_date": [float(x[idxp]) for x in pb_screen_folds],
        "shared_beta_cv_mean_nats_per_date": float(sum(fold) / len(fold)),
        "shared_beta_cv_fold_nats_per_date": [float(x) for x in fold],
        "shared_beta_train_fold_estimates": [float(x) for x in betas],
    })
pb_shared.sort(key=lambda x: (-x["shared_beta_cv_mean_nats_per_date"], x["weight"], x["mask"]))

mdl_k = 2
mdl_penalty = 0.5 * mdl_k * math.log(n_dates) / n_dates
pairs = []
for w in white_shared[:10]:
    for p in pb_shared[:5]:
        raw = w["shared_beta_cv_mean_nats_per_date"] + p["shared_beta_cv_mean_nats_per_date"]
        pairs.append({
            "white_mask": w["mask"],
            "white_bits": w["bits"],
            "white_weight": w["weight"],
            "pb_mask": p["mask"],
            "pb_bits": p["bits"],
            "pb_weight": p["weight"],
            "dev_cv_raw_combined_nats_per_date": raw,
            "mdl_scalar_parameter_count_k": mdl_k,
            "mdl_penalty_nats_per_date": mdl_penalty,
            "dev_cv_score_minus_mdl": raw - mdl_penalty,
            "white_cv_folds": w["shared_beta_cv_fold_nats_per_date"],
            "pb_cv_folds": p["shared_beta_cv_fold_nats_per_date"],
        })
pairs.sort(key=lambda x: (-x["dev_cv_score_minus_mdl"], x["white_weight"] + x["pb_weight"], x["white_mask"], x["pb_mask"]))

bit_semantics = {
    str(bit): {"pretest_index": bit // 5 + 1, "white_extraction_position": bit % 5 + 1}
    for bit in range(20)
}
payload = {
    "experiment": "RCX-PB-GC-0001",
    "stage": "DEV_SPARSE_GF2_PARITY_DISCOVERY",
    "version": "v0.1",
    "data_policy": "development draw outcomes only; all-split pretest-only context; no validation/sealed draw outcomes",
    "development_target_dates": n_dates,
    "white_binary_representation": "20 independently defined event-incidence bits: four pretests x five ordered white extraction positions",
    "powerball_binary_representation": "4 independently defined event-incidence bits: one PB occurrence bit per pretest",
    "white_mask_search": "all Hamming-weight 1..4 masks over 20 coordinates",
    "white_masks_screened": len(white_masks),
    "pb_masks_screened": len(pb_masks),
    "screen_alpha": SCREEN_ALPHA,
    "screen_keep_white": 32,
    "screen_keep_pb": 15,
    "stage_b_model": "one shared conditional-logit beta for white parity and one for PB parity",
    "scalar_parameter_count": mdl_k,
    "mdl_penalty_nats_per_date": mdl_penalty,
    "bit_semantics": bit_semantics,
    "white_shared_top": white_shared[:20],
    "pb_shared_all": pb_shared,
    "combined_top": pairs[:50],
}
OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

with OUTCSV.open("w", newline="", encoding="utf-8") as f:
    fields = [
        "rank", "white_mask", "white_bits", "white_weight", "pb_mask", "pb_bits", "pb_weight",
        "dev_cv_raw_combined_nats_per_date", "mdl_penalty_nats_per_date", "dev_cv_score_minus_mdl"
    ]
    wr = csv.DictWriter(f, fieldnames=fields)
    wr.writeheader()
    for rank, row in enumerate(pairs[:50], 1):
        wr.writerow({
            "rank": rank,
            "white_mask": row["white_mask"],
            "white_bits": json.dumps(row["white_bits"]),
            "white_weight": row["white_weight"],
            "pb_mask": row["pb_mask"],
            "pb_bits": json.dumps(row["pb_bits"]),
            "pb_weight": row["pb_weight"],
            "dev_cv_raw_combined_nats_per_date": row["dev_cv_raw_combined_nats_per_date"],
            "mdl_penalty_nats_per_date": row["mdl_penalty_nats_per_date"],
            "dev_cv_score_minus_mdl": row["dev_cv_score_minus_mdl"],
        })

print(json.dumps({
    "stage": payload["stage"],
    "development_target_dates": n_dates,
    "white_masks_screened": len(white_masks),
    "top_white_shared": white_shared[:5],
    "top_pb_shared": pb_shared[:5],
    "top_combined": pairs[:5],
}, indent=2, sort_keys=True))
