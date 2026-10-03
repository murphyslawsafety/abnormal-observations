#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import subprocess
from collections import defaultdict
from pathlib import Path

ART = Path("artifact")
VAULT = Path("vault")
MODEL_PATH = Path("research/rcx_pb_gc_0002/RCX_PB_GC_0002_FITTED_MODEL_v1.0.json")
MODEL_SHA256 = "7831729fc8ba4fc385e8956961572f1e5ca8fc289c57ded77ef49fe49b441b87"
SCORER_PATH = Path("research/rcx_pb_gc_0002/live_score.py")

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

model_bytes = MODEL_PATH.read_bytes()
if sha256_bytes(model_bytes) != MODEL_SHA256:
    raise SystemExit("parent model SHA-256 mismatch")
model = json.loads(model_bytes.decode("utf-8"))

# Import the exact frozen live scorer implementation.
spec = importlib.util.spec_from_file_location("rcx_pb_gc_0002_live", SCORER_PATH)
live = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(live)

# Read safe pretest context and only then open the sealed truth after prereg/evaluator freeze.
with (ART / "CONTEXT_PRETESTS_ALL.csv").open(newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

pretests_by_date = defaultdict(list)
for r in rows:
    if r["type_class"] != "Pre-test":
        continue
    pretests_by_date[r["date"]].append({
        "balls": [int(r[f"ball{i}"]) for i in range(1, 6)],
        "pb": int(r["pb"]),
        "wm": int(r["wm"]),
        "ws": int(r["ws"]),
        "pm": int(r["pm"]),
        "ps": int(r["ps"]),
    })

for d in pretests_by_date:
    if len(pretests_by_date[d]) != 4:
        raise SystemExit(f"pretest count !=4 on {d}")

truth_path = VAULT / "SEALED_TRUTH.json"
truth_bytes = truth_path.read_bytes()
truth_sha = sha256_bytes(truth_bytes)
sealed = json.loads(truth_bytes.decode("utf-8"))

if len(sealed) != 273:
    raise SystemExit(f"sealed target count mismatch: {len(sealed)}")

results = []
for rec in sorted(sealed, key=lambda x: x["date"]):
    d = rec["date"]
    if d not in pretests_by_date:
        raise SystemExit(f"missing pretest context for sealed target {d}")
    draw = {"balls": [int(x) for x in rec["balls"]], "pb": int(rec["pb"])}
    score = live.score_draw(model, pretests_by_date[d], draw)
    results.append({
        "date": d,
        "white_llr_nats": score["white_llr_nats"],
        "pb_llr_nats": score["pb_llr_nats"],
        "total_llr_nats": score["total_llr_nats"],
        "log10_e_value": score["log10_e_value"],
    })

n = len(results)
white_total = sum(r["white_llr_nats"] for r in results)
pb_total = sum(r["pb_llr_nats"] for r in results)
llr_total = sum(r["total_llr_nats"] for r in results)
log10e = llr_total / math.log(10)
positive = [r["total_llr_nats"] for r in results if r["total_llr_nats"] > 0]
negative = [r["total_llr_nats"] for r in results if r["total_llr_nats"] < 0]
sum_positive = sum(positive)
max_positive = max(positive) if positive else 0.0
max_negative = min(negative) if negative else 0.0
max_positive_share = (max_positive / sum_positive) if sum_positive > 0 else None

chunks = []
for start in range(0, 270, 30):
    block = results[start:start+30]
    chunks.append({
        "block_index": start // 30 + 1,
        "start_date": block[0]["date"],
        "end_date": block[-1]["date"],
        "n": len(block),
        "llr_nats": sum(r["total_llr_nats"] for r in block),
    })
remainder = results[270:]
remainder_summary = {
    "start_date": remainder[0]["date"] if remainder else None,
    "end_date": remainder[-1]["date"] if remainder else None,
    "n": len(remainder),
    "llr_nats": sum(r["total_llr_nats"] for r in remainder),
}
positive_full_blocks = sum(1 for b in chunks if b["llr_nats"] > 0)

quartiles = []
cuts = [0, n//4, n//2, (3*n)//4, n]
for i in range(4):
    q = results[cuts[i]:cuts[i+1]]
    quartiles.append({
        "quartile": i + 1,
        "start_date": q[0]["date"],
        "end_date": q[-1]["date"],
        "n": len(q),
        "llr_nats": sum(r["total_llr_nats"] for r in q),
    })

historical_signal = (
    llr_total >= math.log(10000)
    and positive_full_blocks >= 6
    and (max_positive_share is not None and max_positive_share <= 0.25)
)

if llr_total < 0:
    status = "FAIL"
elif historical_signal:
    status = "HISTORICAL_SIGNAL"
else:
    status = "INCONCLUSIVE"

out = {
    "experiment": "RCX-PB-GC-0002H",
    "status": status,
    "parent_model_sha256": MODEL_SHA256,
    "parent_model_git_blob_sha": subprocess.check_output(
        ["git","hash-object",str(MODEL_PATH)], text=True
    ).strip(),
    "frozen_live_scorer_git_blob_sha": subprocess.check_output(
        ["git","hash-object",str(SCORER_PATH)], text=True
    ).strip(),
    "sealed_truth_sha256": truth_sha,
    "sealed_target_count": n,
    "white_llr_total_nats": white_total,
    "pb_llr_total_nats": pb_total,
    "total_llr_nats": llr_total,
    "log10_e_value": log10e,
    "e_value": (math.exp(llr_total) if llr_total < 700 else None),
    "positive_date_count": len(positive),
    "positive_date_fraction": len(positive) / n,
    "max_single_positive_llr_nats": max_positive,
    "max_single_negative_llr_nats": max_negative,
    "max_single_positive_share_of_positive_total": max_positive_share,
    "positive_full_30_target_blocks": positive_full_blocks,
    "full_30_target_blocks": chunks,
    "final_remainder": remainder_summary,
    "chronological_quartiles": quartiles,
    "thresholds": {
        "historical_signal_min_e_value": 10000,
        "historical_signal_min_positive_full_30_target_blocks": 6,
        "historical_signal_max_single_positive_share": 0.25,
        "fail_if_total_llr_below_zero": True,
    },
    "per_date": results,
    "claim_boundary": "Historical sealed holdout only; not a literal live prospective prediction test and not EUREKA-eligible by itself.",
    "eureka_status": "NONE",
}

(ART / "RCX_PB_GC_0002H_RESULT_v1.0.json").write_text(
    json.dumps(out, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

summary = dict(out)
summary.pop("per_date")
(ART / "RCX_PB_GC_0002H_SUMMARY_v1.0.json").write_text(
    json.dumps(summary, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

print(json.dumps(summary, indent=2, sort_keys=True))
