#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import subprocess
import tempfile
from collections import defaultdict
from datetime import datetime, time, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

MODEL_PATH = Path("research/rcx_pb_gc_0002/RCX_PB_GC_0002_FITTED_MODEL_v1.0.json")
MODEL_SHA256 = "7831729fc8ba4fc385e8956961572f1e5ca8fc289c57ded77ef49fe49b441b87"
SOURCE_URL = "https://cdn.powerball.com/v01/media/powerball-pre-test.pdf"
ET = ZoneInfo("America/New_York")

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def git_blob(path: str) -> str:
    return subprocess.check_output(["git", "hash-object", path], text=True).strip()

def load_model():
    raw = MODEL_PATH.read_bytes()
    got = sha256_bytes(raw)
    if got != MODEL_SHA256:
        raise SystemExit(f"MODEL HASH MISMATCH: {got}")
    model = json.loads(raw.decode("utf-8"))
    if model.get("experiment") != "RCX-PB-GC-0002":
        raise SystemExit("wrong model experiment")
    return model, got

EVENT_RE = re.compile(
    r"(?P<date>\d{2}/\d{2}/\d{2})\s+"
    r"(?P<b1>\d{1,2})\s+(?P<b2>\d{1,2})\s+(?P<b3>\d{1,2})\s+(?P<b4>\d{1,2})\s+(?P<b5>\d{1,2})\s+"
    r"(?P<wm>\d{1,2})\s+(?P<ws>\d{1,2})\s+"
    r"(?P<pb>\d{1,2})\s+"
    r"(?P<pp>--+|-|\d{1,2})\s+"
    r"(?P<pm>\d{1,2})\s+(?P<ps>\d{1,2})\s+"
    r"(?P<type>Pre-test|Post-test|Draw(?:\s*-[A-Za-z0-9]+(?:,\s*[A-Za-z0-9]+)*)?)"
)

def source_events_for_date(target_iso: str):
    target_dt = datetime.strptime(target_iso, "%Y-%m-%d")
    raw_date = target_dt.strftime("%m/%d/%y")

    req = Request(SOURCE_URL, headers={"User-Agent": "Mozilla/5.0 RCX-PB-GC-0002"})
    retrieved = datetime.now(timezone.utc)
    with urlopen(req, timeout=90) as response:
        pdf = response.read()
    source_sha = sha256_bytes(pdf)

    with tempfile.TemporaryDirectory() as td:
        pdf_path = Path(td) / "source.pdf"
        txt_path = Path(td) / "source.txt"
        pdf_path.write_bytes(pdf)
        subprocess.run(
            ["pdftotext", "-layout", "-nopgbrk", str(pdf_path), str(txt_path)],
            check=True,
        )
        text = txt_path.read_text("utf-8", errors="replace")

    marker = re.search(r"POWERBALL.*NUMBERS DRAWN\s+5/69\s*\+\s*1/26", text, re.I)
    if not marker:
        raise SystemExit("current-matrix marker not found")
    matrix = text[marker.start():]

    # Repair only extraction artifacts where a page break split the literal token Pre-test.
    matrix = re.sub(r"Pre\s*\n\s*-test", "Pre-test", matrix)

    events = []
    for m in EVENT_RE.finditer(matrix):
        if m.group("date") != raw_date:
            continue
        typ = m.group("type")
        type_class = "Draw" if typ.startswith("Draw") else typ
        event = {
            "raw_date": m.group("date"),
            "type_raw": typ,
            "type_class": type_class,
            "balls": [int(m.group(f"b{i}")) for i in range(1, 6)],
            "wm": int(m.group("wm")),
            "ws": int(m.group("ws")),
            "pb": int(m.group("pb")),
            "pp_raw": m.group("pp"),
            "pm": int(m.group("pm")),
            "ps": int(m.group("ps")),
        }
        events.append(event)

    return events, {
        "source_url": SOURCE_URL,
        "source_sha256": source_sha,
        "source_bytes": len(pdf),
        "retrieved_at_utc": retrieved.isoformat(),
    }

def canonical_pretest_payload(target_iso: str, pretests):
    return {
        "experiment": "RCX-PB-GC-0002",
        "target_date": target_iso,
        "pretests": [
            {
                "sequence_index": i,
                "balls": row["balls"],
                "pb": row["pb"],
                "wm": row["wm"],
                "ws": row["ws"],
                "pm": row["pm"],
                "ps": row["ps"],
            }
            for i, row in enumerate(pretests)
        ],
    }

def build_context(pretests):
    positions = defaultdict(list)
    row_sets = []
    ordered_rows = []
    pb_counts = defaultdict(int)

    for pi, row in enumerate(pretests):
        seq = list(row["balls"])
        ordered_rows.append(seq)
        row_sets.append(set(seq))
        for pos, label in enumerate(seq):
            positions[label].append((pi, pos))
        pb_counts[row["pb"]] += 1

    return {
        "positions": positions,
        "row_sets": row_sets,
        "ordered_rows": ordered_rows,
        "pb_counts": pb_counts,
    }

def white_features(ctx, candidate: int, position_index: int, prefix):
    union = 1.0 if candidate in ctx["positions"] else 0.0
    same_pos = (
        sum(1 for _pi, pos in ctx["positions"].get(candidate, []) if pos == position_index)
        / 4.0
    )

    if prefix:
        hits = 0
        for prior in prefix:
            hits += int(any(candidate in s and prior in s for s in ctx["row_sets"]))
        prefix_cooccur = hits / len(prefix)
    else:
        prefix_cooccur = 0.0

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

    return [union, same_pos, prefix_cooccur, adj_fwd, adj_rev]

def pb_feature(ctx, candidate: int):
    return [ctx["pb_counts"].get(candidate, 0) / 4.0]

def dot(beta, x):
    return sum(a * b for a, b in zip(beta, x))

def log_softmax_chosen(scores, chosen_index):
    m = max(scores)
    denom_log = m + math.log(sum(math.exp(s - m) for s in scores))
    return scores[chosen_index] - denom_log

def score_draw(model, pretests, draw):
    beta_w = model["coefficients"]["white"]
    beta_p = model["coefficients"]["powerball"]
    ctx = build_context(pretests)

    remaining = list(range(1, 70))
    prefix = []
    white_logp_model = 0.0
    white_logp_fair = 0.0

    for pos, chosen in enumerate(draw["balls"]):
        scores = [
            dot(beta_w, white_features(ctx, candidate, pos, prefix))
            for candidate in remaining
        ]
        ci = remaining.index(chosen)
        white_logp_model += log_softmax_chosen(scores, ci)
        white_logp_fair -= math.log(len(remaining))
        prefix.append(chosen)
        remaining.pop(ci)

    pb_scores = [dot(beta_p, pb_feature(ctx, candidate)) for candidate in range(1, 27)]
    pb_logp_model = log_softmax_chosen(pb_scores, draw["pb"] - 1)
    pb_logp_fair = -math.log(26)

    white_llr = white_logp_model - white_logp_fair
    pb_llr = pb_logp_model - pb_logp_fair
    total_llr = white_llr + pb_llr

    return {
        "white_logp_model": white_logp_model,
        "white_logp_fair": white_logp_fair,
        "white_llr_nats": white_llr,
        "pb_logp_model": pb_logp_model,
        "pb_logp_fair": pb_logp_fair,
        "pb_llr_nats": pb_llr,
        "total_llr_nats": total_llr,
        "log10_e_value": total_llr / math.log(10),
    }

def permuted_pretests(pretests, white_set_id: int, pb_set_id: int):
    def permutation(n, seed_text):
        seed = int.from_bytes(hashlib.sha256(seed_text.encode()).digest()[:8], "big")
        rng = random.Random(seed)
        vals = list(range(1, n + 1))
        shuffled = vals[:]
        rng.shuffle(shuffled)
        return dict(zip(vals, shuffled))

    wm = permutation(69, f"RCX-PB-GC-0002|SHADOW|W|{white_set_id}")
    pm = permutation(26, f"RCX-PB-GC-0002|SHADOW|P|{pb_set_id}")

    out = []
    for row in pretests:
        q = dict(row)
        q["balls"] = [wm[x] for x in row["balls"]]
        q["pb"] = pm[row["pb"]]
        out.append(q)
    return out

def draw_deadline_utc(target_iso: str):
    d = datetime.strptime(target_iso, "%Y-%m-%d").date()
    local = datetime.combine(d, time(22, 59), tzinfo=ET)
    return local.astimezone(timezone.utc)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target-date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--calibration", action="store_true")
    ap.add_argument("--predraw-commit-sha", default=None)
    ap.add_argument("--output", default=None)
    args = ap.parse_args()

    model, model_sha = load_model()
    scorer_blob = git_blob("research/rcx_pb_gc_0002/live_score.py")
    events, source_meta = source_events_for_date(args.target_date)

    pretests = [e for e in events if e["type_class"] == "Pre-test"]
    draws = [e for e in events if e["type_class"] == "Draw"]
    posttests = [e for e in events if e["type_class"] == "Post-test"]

    now_utc = datetime.now(timezone.utc)
    deadline = draw_deadline_utc(args.target_date)

    result = {
        "experiment": "RCX-PB-GC-0002",
        "target_date": args.target_date,
        "mode": "CALIBRATION" if args.calibration else "LIVE",
        "model_sha256": model_sha,
        "scorer_git_blob_sha": scorer_blob,
        "source": source_meta,
        "draw_deadline_utc": deadline.isoformat(),
        "run_at_utc": now_utc.isoformat(),
        "pretest_count": len(pretests),
        "draw_count": len(draws),
        "posttest_count": len(posttests),
        "sealed_rcx_pb_gc_0001_outcomes_used": False,
        "eureka_status": "NONE",
    }

    if len(pretests) == 4:
        payload = canonical_pretest_payload(args.target_date, pretests)
        payload_bytes = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
        context_sha = sha256_bytes(payload_bytes)
        commit_payload = {
            "experiment": "RCX-PB-GC-0002",
            "target_date": args.target_date,
            "model_sha256": model_sha,
            "scorer_git_blob_sha": scorer_blob,
            "pretest_context_sha256": context_sha,
        }
        commit_bytes = (json.dumps(commit_payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
        result["pretest_context_sha256"] = context_sha
        result["prediction_commit_sha256"] = sha256_bytes(commit_bytes)

        # Model is invariant to the order of the four pretest rows by construction.
        reversed_payload = canonical_pretest_payload(args.target_date, list(reversed(pretests)))
        result["row_order_shadow_is_model_invariant_by_definition"] = True

    if args.calibration:
        result["status"] = (
            "CALIBRATION_PARSE_PASS"
            if len(pretests) == 4 and len(draws) == 1
            else "CALIBRATION_PARSE_FAIL"
        )
        # Deliberately omit outcome values and model score in calibration mode.
    else:
        if len(pretests) != 4:
            result["status"] = "SOURCE_NOT_READY" if now_utc < deadline else "SOURCE_UNAVAILABLE_OR_PARSE_BLOCK"
        elif len(draws) == 0:
            result["status"] = (
                "LIVE_PREDICTION_COMMITTED"
                if now_utc < deadline
                else "PROSPECTIVE_FROZEN_MODEL_ONLY_PENDING_DRAW"
            )
        elif len(draws) == 1:
            score = score_draw(model, pretests, draws[0])
            result["score"] = score
            result["status"] = (
                "LIVE_PREDICTION_COMMITTED_AND_SCORED"
                if args.predraw_commit_sha
                else "PROSPECTIVE_FROZEN_MODEL_ONLY"
            )
            result["provided_predraw_commit_sha256"] = args.predraw_commit_sha

            # Secondary shadow: deterministic within-set relabeling of pretest identities only.
            white_set_id = pretests[0]["ws"]
            pb_set_id = pretests[0]["ps"]
            shadow_pretests = permuted_pretests(pretests, white_set_id, pb_set_id)
            result["shadow_deterministic_label_permutation"] = score_draw(model, shadow_pretests, draws[0])

            # Implementation baseline: zero coefficients must reproduce fair exactly.
            fair_model = json.loads(json.dumps(model))
            fair_model["coefficients"]["white"] = [0.0] * 5
            fair_model["coefficients"]["powerball"] = [0.0]
            zero = score_draw(fair_model, pretests, draws[0])
            result["zero_coefficient_control_total_llr_nats"] = zero["total_llr_nats"]
        else:
            result["status"] = "BLOCKED_MULTIPLE_DRAW_ROWS"

    out = args.output or f"artifact/RCX_PB_GC_0002_{args.target_date}_{'CALIBRATION' if args.calibration else 'LIVE'}.json"
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
