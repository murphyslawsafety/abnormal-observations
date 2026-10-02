#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import math
import subprocess
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

ART = Path("artifact")
MANIFEST_PATH = Path("research/rcx_pb_gc_0001/SEARCH_MANIFEST_v0.1.json")
manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

def load_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

ctx_rows = load_csv(ART / "CONTEXT_PRETESTS_ALL.csv")
dev_rows = load_csv(ART / "DEVELOPMENT.csv")
val_rows = load_csv(ART / "VALIDATION.csv")
qual = json.loads((ART / "QUALIFICATION_SUMMARY.json").read_text(encoding="utf-8"))

if not qual.get("scoring_authorized"):
    raise SystemExit("corpus qualification does not authorize scoring")
if qual.get("execution_amendment") != "v0.4":
    raise SystemExit("unexpected qualification amendment")
if qual.get("source_sha256") != manifest["source_sha256"]:
    raise SystemExit("source hash mismatch")
if qual.get("source_unavailable_dates") != manifest["source_unavailable_dates"]:
    raise SystemExit("source-unavailable mask mismatch")

actual_runner_blob = subprocess.check_output(
    ["git", "hash-object", "research/rcx_pb_gc_0001/validate_global_parity.py"],
    text=True,
).strip()
if actual_runner_blob != manifest["validation_runner_git_blob_sha"]:
    raise SystemExit(f"validation runner blob mismatch: {actual_runner_blob}")

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
    if len(rows) != 4:
        raise SystemExit(f"pretest context count != 4 on {d}")
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

def draw_targets(rows):
    out = {}
    for r in rows:
        if r["type_class"] == "Draw":
            out[r["date"]] = {
                "white": [int(r[f"ball{i}"]) for i in range(1, 6)],
                "pb": int(r["pb"]),
            }
    return out

dev = draw_targets(dev_rows)
val = draw_targets(val_rows)

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

def white_stats(targets, d, mask, mode):
    remaining = set(range(1, 70))
    out = []
    for chosen in targets[d]["white"]:
        zs = [white_z(d, label, mask, mode) for label in remaining]
        zc = white_z(d, chosen, mask, mode)
        out.append((zs, zc, len(remaining)))
        remaining.remove(chosen)
    return out

def pb_stats(targets, d, mask, mode):
    zs = [pb_z(d, label, mask, mode) for label in range(1, 27)]
    zc = pb_z(d, targets[d]["pb"], mask, mode)
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

dev_dates = sorted(dev)
val_dates = sorted(val)
NVAL = len(val_dates)
if NVAL != manifest["validation_target_dates_expected"]:
    raise SystemExit(f"validation target count mismatch {NVAL}")

mdl_k = manifest["mdl_scalar_parameter_count_k"]
mdl = 0.5 * mdl_k * math.log(NVAL) / NVAL

results = []
for candidate in manifest["validation_candidates"]:
    wmask = int(candidate["white_mask"])
    pmask = int(candidate["pb_mask"])

    # Fit the two scalar coefficients once on ALL DEV using the global grammar.
    beta_w = fit_beta([s for d in dev_dates for s in white_stats(dev, d, wmask, "global")])
    beta_p = fit_beta([s for d in dev_dates for s in pb_stats(dev, d, pmask, "global")])

    global_per_date = []
    forward_per_date = []
    for d in val_dates:
        g = score(white_stats(val, d, wmask, "global"), beta_w)
        g += score(pb_stats(val, d, pmask, "global"), beta_p)
        f = score(white_stats(val, d, wmask, "forward"), beta_w)
        f += score(pb_stats(val, d, pmask, "forward"), beta_p)
        global_per_date.append(g)
        forward_per_date.append(f)

    gmean = sum(global_per_date) / NVAL
    fmean = sum(forward_per_date) / NVAL
    result = {
        **candidate,
        "beta_white_fitted_dev_global": beta_w,
        "beta_pb_fitted_dev_global": beta_p,
        "validation_target_dates": NVAL,
        "validation_global_raw_nats_per_date": gmean,
        "validation_forward_raw_same_beta_nats_per_date": fmean,
        "mdl_scalar_parameter_count_k": mdl_k,
        "validation_mdl_penalty_nats_per_date": mdl,
        "validation_global_score_minus_mdl": gmean - mdl,
        "validation_global_beats_fair": gmean > 0,
        "validation_forward_beats_fair": fmean > 0,
        "validation_advance": (
            gmean - mdl > 0
            and fmean > 0
        ),
    }
    results.append(result)

results.sort(key=lambda x: (
    -x["validation_global_score_minus_mdl"],
    -x["validation_forward_raw_same_beta_nats_per_date"],
    x["model_id"],
))

advancing = [r for r in results if r["validation_advance"]]
selected = advancing[0] if advancing else None

output = {
    "experiment": "RCX-PB-GC-0001",
    "stage": "VALIDATION_GLOBAL_PARITY_SELECTION",
    "manifest_id": manifest["manifest_id"],
    "manifest_git_blob_sha": subprocess.check_output(
        ["git", "hash-object", str(MANIFEST_PATH)], text=True
    ).strip(),
    "source_sha256": qual["source_sha256"],
    "development_target_dates": len(dev_dates),
    "validation_target_dates": NVAL,
    "mdl_scalar_parameter_count_k": mdl_k,
    "validation_mdl_penalty_nats_per_date": mdl,
    "selection_rule": manifest["validation_selection_rule"],
    "results": results,
    "advancing_count": len(advancing),
    "selected_candidate": selected,
    "status": "VALIDATION_PASS" if selected is not None else "VALIDATION_FAIL",
    "sealed_truth_accessed": False,
}
(ART / "VALIDATION_GLOBAL_PARITY_v0.1.json").write_text(
    json.dumps(output, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
print(json.dumps(output, indent=2, sort_keys=True))
