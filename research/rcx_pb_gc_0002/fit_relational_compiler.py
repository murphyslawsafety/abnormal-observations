#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import math
import subprocess
from collections import defaultdict
from pathlib import Path

import numpy as np

ART = Path("artifact")
OUT = ART / "RCX_PB_GC_0002_FITTED_MODEL_v1.0.json"

LAMBDA = 10.0
MAX_ITER = 100
TOL = 1e-10
CLIP = 8.0

def load_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

dev_rows = load_csv(ART / "DEVELOPMENT.csv")
val_rows = load_csv(ART / "VALIDATION.csv")
ctx_rows = load_csv(ART / "CONTEXT_PRETESTS_ALL.csv")
qual = json.loads((ART / "QUALIFICATION_SUMMARY.json").read_text(encoding="utf-8"))

if qual.get("execution_amendment") != "v0.4":
    raise SystemExit("unexpected source qualification amendment")
if qual.get("source_sha256") != "75e66acebe26b9e6803e80e1e4b156f54e0db0e1da8af9f4975a21d784d547f4":
    raise SystemExit("unexpected source snapshot hash")
if qual.get("cutoff") != "2026-09-28":
    raise SystemExit("unexpected historical cutoff")

# Build same-day four-pretest context only.
pre = defaultdict(list)
for r in ctx_rows:
    pre[r["date"]].append(r)
for d in pre:
    pre[d].sort(key=lambda r: int(r["sequence_index"]))
    if len(pre[d]) != 4:
        raise SystemExit(f"pretest count != 4 on {d}")

# Only already-consumed RCX-PB-GC-0001 DEV + VAL targets are authorized.
targets = {}
target_split = {}
for rows, split_name in ((dev_rows, "development"), (val_rows, "validation")):
    for r in rows:
        if r["type_class"] != "Draw":
            continue
        if r["date"] in targets:
            raise SystemExit(f"duplicate target {r['date']}")
        targets[r["date"]] = {
            "white": [int(r[f"ball{i}"]) for i in range(1, 6)],
            "pb": int(r["pb"]),
        }
        target_split[r["date"]] = split_name

if len(targets) != 1139:
    raise SystemExit(f"authorized target count mismatch: {len(targets)} != 1139")

def build_context(rows):
    # Occurrence lookup by object.
    positions = defaultdict(list)   # label -> [(pretest_index, pos_index)]
    row_sets = []
    ordered_rows = []
    pb_counts = defaultdict(int)

    for pi, r in enumerate(rows):
        seq = [int(r[f"ball{i}"]) for i in range(1, 6)]
        ordered_rows.append(seq)
        row_sets.append(set(seq))
        for pos, label in enumerate(seq):
            positions[label].append((pi, pos))
        pb_counts[int(r["pb"])] += 1

    return {
        "positions": positions,
        "row_sets": row_sets,
        "ordered_rows": ordered_rows,
        "pb_counts": pb_counts,
    }

contexts = {d: build_context(pre[d]) for d in targets}

def white_features(ctx, candidate, position_index, prefix):
    # 1. UNION
    union = 1.0 if candidate in ctx["positions"] else 0.0

    # 2. SAME_POS
    same_pos = sum(1 for _pi, pos in ctx["positions"].get(candidate, []) if pos == position_index) / 4.0

    # 3. PREFIX_COOCCUR
    if prefix:
        hits = 0
        for prior in prefix:
            supported = any(candidate in s and prior in s for s in ctx["row_sets"])
            hits += int(supported)
        prefix_cooccur = hits / len(prefix)
    else:
        prefix_cooccur = 0.0

    # 4/5. Directed adjacency with immediately previous official white.
    adj_fwd = 0.0
    adj_rev = 0.0
    if prefix:
        prev = prefix[-1]
        fwd = 0
        rev = 0
        for seq in ctx["ordered_rows"]:
            for k in range(4):
                if seq[k] == prev and seq[k + 1] == candidate:
                    fwd += 1
                if seq[k] == candidate and seq[k + 1] == prev:
                    rev += 1
        adj_fwd = fwd / 4.0
        adj_rev = rev / 4.0

    return np.array([union, same_pos, prefix_cooccur, adj_fwd, adj_rev], dtype=float)

def pb_feature(ctx, candidate):
    return np.array([ctx["pb_counts"].get(candidate, 0) / 4.0], dtype=float)

# Choice sets: (X risk-set matrix, chosen-index).
white_sets = []
pb_sets = []
for d in sorted(targets):
    ctx = contexts[d]
    white = targets[d]["white"]
    remaining = list(range(1, 70))
    prefix = []
    for pos, chosen in enumerate(white):
        X = np.vstack([white_features(ctx, c, pos, prefix) for c in remaining])
        ci = remaining.index(chosen)
        white_sets.append((X, ci))
        prefix.append(chosen)
        remaining.pop(ci)

    Xp = np.vstack([pb_feature(ctx, c) for c in range(1, 27)])
    pb_sets.append((Xp, targets[d]["pb"] - 1))

def fit_conditional_logit(choice_sets, p):
    beta = np.zeros(p, dtype=float)
    eye = np.eye(p)
    converged = False
    last_step = None

    for iteration in range(1, MAX_ITER + 1):
        grad = -LAMBDA * beta
        hess = -LAMBDA * eye.copy()

        for X, ci in choice_sets:
            eta = X @ beta
            m = float(np.max(eta))
            w = np.exp(eta - m)
            probs = w / w.sum()
            mean = probs @ X
            centered = X - mean
            cov = (centered.T * probs) @ centered
            grad += X[ci] - mean
            hess -= cov

        try:
            step = np.linalg.solve(hess, grad)
        except np.linalg.LinAlgError:
            raise SystemExit("UNIDENTIFIABLE: singular penalized Hessian")

        max_abs = float(np.max(np.abs(step))) if step.size else 0.0
        if max_abs > 1.0:
            step = step / max_abs

        beta -= step
        beta = np.clip(beta, -CLIP, CLIP)
        last_step = float(np.max(np.abs(step))) if step.size else 0.0

        if last_step < TOL:
            converged = True
            break

    if not converged:
        raise SystemExit(f"UNIDENTIFIABLE: optimizer did not converge; last_step={last_step}")
    return beta, iteration, last_step

beta_w, it_w, step_w = fit_conditional_logit(white_sets, 5)
beta_p, it_p, step_p = fit_conditional_logit(pb_sets, 1)

def log_score(choice_sets, beta):
    total = 0.0
    for X, ci in choice_sets:
        eta = X @ beta
        m = float(np.max(eta))
        total += float(eta[ci] - (m + math.log(float(np.exp(eta - m).sum()))))
    return total

white_logp = log_score(white_sets, beta_w)
pb_logp = log_score(pb_sets, beta_p)
n_targets = len(targets)
fair_white_logp = n_targets * (-sum(math.log(x) for x in [69,68,67,66,65]))
fair_pb_logp = n_targets * (-math.log(26))

model = {
    "experiment": "RCX-PB-GC-0002",
    "model_version": "1.0",
    "fit_status": "FROZEN_CANDIDATE_MODEL",
    "preregistration": "RCX_PB_GC_0002_PREREGISTRATION_v1.0.md",
    "historical_estimation_policy": "RCX-PB-GC-0001 development + validation only; prior sealed_test excluded",
    "historical_cutoff": "2026-09-28",
    "training_target_count": n_targets,
    "training_split_counts": {
        "development": sum(1 for d in targets if target_split[d] == "development"),
        "validation": sum(1 for d in targets if target_split[d] == "validation"),
    },
    "source_sha256": qual["source_sha256"],
    "source_unavailable_dates": qual["source_unavailable_dates"],
    "feature_order_white": ["UNION","SAME_POS","PREFIX_COOCCUR","ADJ_FWD","ADJ_REV"],
    "feature_order_powerball": ["PB_OCCUR"],
    "lambda_l2": LAMBDA,
    "optimizer": {
        "name": "deterministic penalized Newton/IRLS",
        "zero_initialization": True,
        "max_iterations": MAX_ITER,
        "coefficient_clip": [-CLIP, CLIP],
        "convergence_tolerance_max_abs_step": TOL,
        "damp_step_if_max_abs_exceeds": 1.0,
        "white_iterations": it_w,
        "white_final_max_abs_step": step_w,
        "pb_iterations": it_p,
        "pb_final_max_abs_step": step_p,
    },
    "coefficients": {
        "white": [float(x) for x in beta_w],
        "powerball": [float(x) for x in beta_p],
    },
    "training_diagnostic_only_not_evidence": {
        "white_mean_logscore_improvement_nats_per_draw": float((white_logp - fair_white_logp) / n_targets),
        "pb_mean_logscore_improvement_nats_per_draw": float((pb_logp - fair_pb_logp) / n_targets),
        "total_mean_logscore_improvement_nats_per_draw": float((white_logp + pb_logp - fair_white_logp - fair_pb_logp) / n_targets),
    },
    "prospective_start": "2026-10-03",
    "block_a_usable_draws": 30,
    "sealed_rcx_pb_gc_0001_outcomes_used": False,
    "eureka_status": "NONE",
}

model_bytes = (json.dumps(model, indent=2, sort_keys=True) + "\n").encode()
OUT.write_bytes(model_bytes)
(ART / "RCX_PB_GC_0002_FITTED_MODEL_v1.0.sha256").write_text(
    hashlib.sha256(model_bytes).hexdigest() + "  RCX_PB_GC_0002_FITTED_MODEL_v1.0.json\n",
    encoding="utf-8",
)

print(json.dumps({
    "experiment": model["experiment"],
    "training_target_count": n_targets,
    "training_split_counts": model["training_split_counts"],
    "coefficients": model["coefficients"],
    "optimizer": model["optimizer"],
    "training_diagnostic_only_not_evidence": model["training_diagnostic_only_not_evidence"],
    "model_sha256": hashlib.sha256(model_bytes).hexdigest(),
}, indent=2, sort_keys=True))
