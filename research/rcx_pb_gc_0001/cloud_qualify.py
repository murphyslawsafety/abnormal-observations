#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.request import Request, urlopen

EXP = "RCX-PB-GC-0001"
EXECUTION_AMENDMENT = "v0.4"
URL = "https://cdn.powerball.com/v01/media/powerball-pre-test.pdf"
EXPECTED_SOURCE_SHA256 = "75e66acebe26b9e6803e80e1e4b156f54e0db0e1da8af9f4975a21d784d547f4"
START = date(2015, 10, 7)
CUTOFF = date(2026, 9, 28)

OUT = Path("artifact")
VAULT = Path("vault")
OUT.mkdir(exist_ok=True)
VAULT.mkdir(exist_ok=True)

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def split_for(iso: str):
    bucket = hashlib.sha256(f"{EXP}|{iso}".encode()).digest()[0] % 10
    split = "development" if bucket <= 5 else "validation" if bucket <= 7 else "sealed_test"
    return bucket, split

def expected_schedule(start: date, end: date):
    out = []
    d = start
    while d <= end:
        # Powerball was Wed/Sat in this matrix until Monday drawings began 2021-08-23.
        if (d < date(2021, 8, 23) and d.weekday() in (2, 5)) or (
            d >= date(2021, 8, 23) and d.weekday() in (0, 2, 5)
        ):
            out.append(d.isoformat())
        d += timedelta(days=1)
    return out

EXPECTED_DATES = expected_schedule(START, CUTOFF)
EXPECTED_SET = set(EXPECTED_DATES)

def parse_date_token(raw: str):
    """Return (iso_date_or_none, normalization_kind_or_none)."""
    candidates = [(raw, None)]
    if re.fullmatch(r"\d{2}/\d{4}", raw):
        candidates.append((raw[:5] + "/" + raw[5:], "MM_DDYY_TO_MM_DD_YY"))
    if re.fullmatch(r"\d{2}/\d{2}-\d{2}", raw):
        candidates.append((raw[:5] + "/" + raw[6:], "MM_DD_DASH_YY_TO_MM_DD_YY"))
    for token, kind in candidates:
        try:
            return datetime.strptime(token, "%m/%d/%y").date().isoformat(), kind
        except ValueError:
            pass
    return None, None

def locate_event_type(tokens):
    for i, tok in enumerate(tokens):
        if tok in ("Pre-test", "Post-test", "Draw") or tok.startswith("Draw-"):
            type_raw = " ".join(tokens[i:])
            type_class = "Draw" if tok == "Draw" or tok.startswith("Draw-") else tok
            return i, type_raw, type_class
    return None, None, None

def parse_event_line(raw_line: str, matrix_line: int):
    tokens = raw_line.split()
    type_i, type_raw, type_class = locate_event_type(tokens)
    if type_i is None:
        return None

    data = tokens[:type_i]
    if len(data) not in (11, 12):
        return {
            "parse_error": "AMBIGUOUS_EVENT_ROW_TOKENIZATION",
            "matrix_line": matrix_line,
            "raw_line_sha256": sha256_bytes(raw_line.encode()),
            "raw_date": data[0] if data else None,
            "type_class": type_class,
            "data_token_count": len(data),
        }

    raw_date = data[0]
    values = data[1:]
    try:
        balls = [int(x) for x in values[:5]]
        wm = int(values[5])
        ws = int(values[6])
        pb = int(values[7])
        if len(data) == 12:
            pp_raw = values[8]
            if not (pp_raw.isdigit() or re.fullmatch(r"-+", pp_raw)):
                raise ValueError(f"invalid PP token {pp_raw!r}")
            pm = int(values[9])
            ps = int(values[10])
            pp_structurally_absent = False
        else:
            pp_raw = ""
            pm = int(values[8])
            ps = int(values[9])
            pp_structurally_absent = True
    except Exception as exc:
        return {
            "parse_error": "AMBIGUOUS_EVENT_ROW_TOKENIZATION",
            "matrix_line": matrix_line,
            "raw_line_sha256": sha256_bytes(raw_line.encode()),
            "raw_date": raw_date,
            "type_class": type_class,
            "detail": str(exc),
        }

    row_date, date_normalization = parse_date_token(raw_date)
    return {
        "matrix_line": matrix_line,
        "raw_line": raw_line,
        "raw_line_sha256": sha256_bytes(raw_line.encode()),
        "raw_tokens": tokens,
        "raw_date": raw_date,
        "row_date": row_date,
        "date_normalization": date_normalization,
        "type_raw": type_raw,
        "type_class": type_class,
        "wm": wm,
        "ws": ws,
        "pm": pm,
        "ps": ps,
        "pp_raw": pp_raw,
        "pp_structurally_absent": pp_structurally_absent,
        "pb": pb,
        "balls": balls,
    }

# Acquire and lock the exact authoritative source snapshot.
req = Request(URL, headers={"User-Agent": "Mozilla/5.0 RCX-PB-GC-0001"})
with urlopen(req, timeout=90) as response:
    pdf = response.read()
source_sha = sha256_bytes(pdf)
(VAULT / "powerball-pre-test.pdf").write_bytes(pdf)
if source_sha != EXPECTED_SOURCE_SHA256:
    raise SystemExit(
        "AUTHORITATIVE SOURCE SNAPSHOT CHANGED: "
        f"{source_sha} != {EXPECTED_SOURCE_SHA256}. "
        "Do not continue without a new pre-scoring source-snapshot amendment."
    )

subprocess.run(
    [
        "pdftotext",
        "-layout",
        "-nopgbrk",
        str(VAULT / "powerball-pre-test.pdf"),
        str(VAULT / "powerball-pre-test-layout.txt"),
    ],
    check=True,
)
full_text = (VAULT / "powerball-pre-test-layout.txt").read_text("utf-8", errors="replace")
text_sha = sha256_bytes(full_text.encode())

marker = re.search(r"POWERBALL.*NUMBERS DRAWN\s+5/69\s*\+\s*1/26", full_text, re.I)
if not marker:
    raise SystemExit("current-matrix marker 5/69 + 1/26 not found")
matrix = full_text[marker.start():]
(VAULT / "current_matrix_extraction.txt").write_text(matrix, encoding="utf-8")

# Parse all physical event lines structurally, preserving raw source only in the vault.
events = []
blocking = []
anomalies = []
for matrix_line, raw_line in enumerate(matrix.splitlines(), 1):
    if not re.search(r"\b(?:Pre-test|Post-test|Draw(?:[-\s]|$))", raw_line):
        continue
    parsed = parse_event_line(raw_line, matrix_line)
    if parsed is None:
        continue
    if "parse_error" in parsed:
        parsed["blocking"] = True
        blocking.append(parsed)
        anomalies.append(parsed)
    else:
        events.append(parsed)

# Keep a full audit ledger in the sealed/source vault, never in model-selection artifacts.
with (VAULT / "PARSED_EVENT_LEDGER_FULL.jsonl").open("w", encoding="utf-8") as f:
    for event in events:
        f.write(json.dumps(event, sort_keys=True) + "\n")

# Build physical blocks: four pretests terminated by one Draw; Post-tests excluded.
blocks = []
pending_pretests = []
for event in events:
    if event["type_class"] == "Post-test":
        continue
    if event["type_class"] == "Pre-test":
        pending_pretests.append(event)
        continue
    if event["type_class"] == "Draw":
        block = {"pretests": pending_pretests[:], "draw": event}
        if len(pending_pretests) != 4:
            rec = {
                "kind": "PRETEST_COUNT",
                "blocking": True,
                "draw_matrix_line": event["matrix_line"],
                "raw_draw_date": event["raw_date"],
                "count": len(pending_pretests),
            }
            blocking.append(rec)
            anomalies.append(rec)
        blocks.append(block)
        pending_pretests = []

if pending_pretests:
    rec = {
        "kind": "TRAILING_PRETESTS_WITHOUT_DRAW",
        "blocking": True,
        "count": len(pending_pretests),
        "first_matrix_line": pending_pretests[0]["matrix_line"],
    }
    blocking.append(rec)
    anomalies.append(rec)

# Source-order block-date assignment. For an off-schedule/invalid draw date, v0.4
# permits normalization only when exactly one expected date lies strictly between
# the preceding and following calendar-valid draw-row dates.
provisional = [block["draw"]["row_date"] for block in blocks]

def nearest_valid_before(i):
    for j in range(i - 1, -1, -1):
        if provisional[j] is not None:
            return provisional[j]
    return None

def nearest_valid_after(i):
    for j in range(i + 1, len(provisional)):
        if provisional[j] is not None:
            return provisional[j]
    return None

canonical_blocks = []
used_dates = set()
for i, block in enumerate(blocks):
    draw = block["draw"]
    provisional_date = draw["row_date"]
    canonical = provisional_date
    normalized_block_date = False

    if canonical is None or (
        START.isoformat() <= canonical <= CUTOFF.isoformat() and canonical not in EXPECTED_SET
    ):
        prev_date = nearest_valid_before(i)
        next_date = nearest_valid_after(i)
        candidates = []
        if prev_date is not None and next_date is not None:
            lo, hi = sorted((prev_date, next_date))
            candidates = [
                d for d in EXPECTED_DATES
                if lo < d < hi and d not in used_dates
            ]
        if len(candidates) == 1:
            canonical = candidates[0]
            normalized_block_date = True
            anomalies.append({
                "kind": "BLOCK_DATE_NORMALIZATION",
                "blocking": False,
                "draw_matrix_line": draw["matrix_line"],
                "raw_draw_date": draw["raw_date"],
                "parsed_draw_date": provisional_date,
                "canonical_date": canonical,
                "rule": "unique_expected_date_between_adjacent_usable_blocks",
            })
        elif canonical is None:
            rec = {
                "kind": "AMBIGUOUS_BLOCK_DATE",
                "blocking": True,
                "draw_matrix_line": draw["matrix_line"],
                "raw_draw_date": draw["raw_date"],
                "candidate_count": len(candidates),
            }
            blocking.append(rec)
            anomalies.append(rec)
            continue

    # Source contains dates beyond the frozen cutoff; retain them only in vault.
    if canonical is None:
        continue
    canonical_date_obj = date.fromisoformat(canonical)
    if canonical_date_obj < START or canonical_date_obj > CUTOFF:
        continue

    if canonical not in EXPECTED_SET:
        rec = {
            "kind": "UNEXPECTED_CANONICAL_DATE",
            "blocking": True,
            "canonical_date": canonical,
            "raw_draw_date": draw["raw_date"],
            "draw_matrix_line": draw["matrix_line"],
        }
        blocking.append(rec)
        anomalies.append(rec)
        continue

    if canonical in used_dates:
        rec = {
            "kind": "DUPLICATE_CANONICAL_DATE",
            "blocking": True,
            "canonical_date": canonical,
            "draw_matrix_line": draw["matrix_line"],
        }
        blocking.append(rec)
        anomalies.append(rec)
        continue
    used_dates.add(canonical)

    bucket, split = split_for(canonical)
    block["canonical_date"] = canonical
    block["split_bucket"] = bucket
    block["split"] = split
    block["block_date_normalized"] = normalized_block_date

    # Preserve row-date defects as metadata only; block membership is source-order structural.
    for event in block["pretests"] + [block["draw"]]:
        if event["date_normalization"] is not None:
            anomalies.append({
                "kind": "SYNTAX_ONLY_DATE_NORMALIZATION",
                "blocking": False,
                "canonical_date": canonical,
                "matrix_line": event["matrix_line"],
                "type_class": event["type_class"],
                "raw_date": event["raw_date"],
                "parsed_row_date": event["row_date"],
                "normalization": event["date_normalization"],
            })
        if event["row_date"] is None:
            anomalies.append({
                "kind": "ROW_DATE_INVALID",
                "blocking": False,
                "canonical_date": canonical,
                "matrix_line": event["matrix_line"],
                "type_class": event["type_class"],
                "raw_date": event["raw_date"],
                "raw_line_sha256": event["raw_line_sha256"],
            })
        elif event["row_date"] != canonical:
            anomalies.append({
                "kind": "ROW_DATE_DISAGREEMENT",
                "blocking": False,
                "canonical_date": canonical,
                "matrix_line": event["matrix_line"],
                "type_class": event["type_class"],
                "raw_date": event["raw_date"],
                "parsed_row_date": event["row_date"],
                "raw_line_sha256": event["raw_line_sha256"],
            })

        if event["pp_structurally_absent"] or (
            event["pp_raw"] and not event["pp_raw"].isdigit() and event["pp_raw"] != "--"
        ):
            anomalies.append({
                "kind": "PP_TOKEN_NORMALIZATION",
                "blocking": False,
                "canonical_date": canonical,
                "matrix_line": event["matrix_line"],
                "type_class": event["type_class"],
                "raw_pp": event["pp_raw"],
                "normalized_pp": None,
            })

    # Scientific row checks. Do not emit sealed numerical outcomes into safe artifacts.
    all_rows = block["pretests"] + [block["draw"]]
    for event in all_rows:
        if len(set(event["balls"])) != 5:
            rec = {
                "kind": "DUPLICATE_WHITE_LABEL_WITHIN_ROW",
                "blocking": True,
                "canonical_date": canonical,
                "matrix_line": event["matrix_line"],
                "type_class": event["type_class"],
            }
            blocking.append(rec)
            anomalies.append(rec)
        if not all(1 <= x <= 69 for x in event["balls"]):
            rec = {
                "kind": "WHITE_OUT_OF_RANGE",
                "blocking": True,
                "canonical_date": canonical,
                "matrix_line": event["matrix_line"],
                "type_class": event["type_class"],
            }
            blocking.append(rec)
            anomalies.append(rec)
        if not 1 <= event["pb"] <= 26:
            rec = {
                "kind": "POWERBALL_OUT_OF_RANGE",
                "blocking": True,
                "canonical_date": canonical,
                "matrix_line": event["matrix_line"],
                "type_class": event["type_class"],
            }
            blocking.append(rec)
            anomalies.append(rec)

    # Preserve hardware/set discontinuities without exposing sealed draw-specific values.
    for field in ("wm", "ws", "pm", "ps"):
        vals = [event[field] for event in all_rows]
        if len(set(vals)) > 1:
            anomalies.append({
                "kind": "SOURCE_REGIME_DISCONTINUITY",
                "blocking": False,
                "canonical_date": canonical,
                "field": field,
                "distinct_count": len(set(vals)),
            })

    canonical_blocks.append(block)

observed_dates = {block["canonical_date"] for block in canonical_blocks}
missing_dates = sorted(EXPECTED_SET - observed_dates)
extra_dates = sorted(observed_dates - EXPECTED_SET)

# v0.4: published-source missingness is outcome-blind and nonblocking, but never imputed.
for missing in missing_dates:
    bucket, split = split_for(missing)
    anomalies.append({
        "kind": "SOURCE_UNAVAILABLE",
        "blocking": False,
        "canonical_date": missing,
        "split_bucket": bucket,
        "split": split,
        "policy": "exclude_symmetrically_from_real_and_null_scoring_no_imputation",
    })

if extra_dates:
    rec = {
        "kind": "UNEXPECTED_CANONICAL_DATES_PRESENT",
        "blocking": True,
        "count": len(extra_dates),
        "dates": extra_dates,
    }
    blocking.append(rec)
    anomalies.append(rec)

# v0.4 is frozen against the observed source gap mask. Any different missingness is blocking.
FROZEN_SOURCE_UNAVAILABLE = ["2025-03-01"]
if missing_dates != FROZEN_SOURCE_UNAVAILABLE:
    rec = {
        "kind": "SOURCE_UNAVAILABLE_MASK_CHANGED",
        "blocking": True,
        "expected_mask": FROZEN_SOURCE_UNAVAILABLE,
        "observed_mask": missing_dates,
    }
    blocking.append(rec)
    anomalies.append(rec)

# Expand qualified physical blocks into rows.
rows = []
for block in canonical_blocks:
    canonical = block["canonical_date"]
    for sequence_index, event in enumerate(block["pretests"] + [block["draw"]]):
        row = {
            "matrix_line": event["matrix_line"],
            "raw_line_sha256": event["raw_line_sha256"],
            "raw_date": event["raw_date"],
            "row_date": event["row_date"] or "",
            "date": canonical,
            "split_bucket": block["split_bucket"],
            "split": block["split"],
            "sequence_index": sequence_index,
            "type_raw": event["type_raw"],
            "type_class": event["type_class"],
            "wm": event["wm"],
            "ws": event["ws"],
            "pm": event["pm"],
            "ps": event["ps"],
            "pp_raw": event["pp_raw"],
            "ball1": event["balls"][0],
            "ball2": event["balls"][1],
            "ball3": event["balls"][2],
            "ball4": event["balls"][3],
            "ball5": event["balls"][4],
            "pb": event["pb"],
            "white_object_ids": "|".join(f"WS:{event['ws']}:B:{x}" for x in event["balls"]),
            "powerball_object_id": f"PS:{event['ps']}:B:{event['pb']}",
        }
        rows.append(row)

fields = [
    "matrix_line", "raw_line_sha256", "raw_date", "row_date", "date",
    "split_bucket", "split", "sequence_index", "type_raw", "type_class",
    "wm", "ws", "pm", "ps", "pp_raw",
    "ball1", "ball2", "ball3", "ball4", "ball5", "pb",
    "white_object_ids", "powerball_object_id",
]

def masked_row(row):
    q = dict(row)
    if row["split"] == "sealed_test" and row["type_class"] == "Draw":
        for key in (
            "wm", "ws", "pm", "ps", "pp_raw",
            "ball1", "ball2", "ball3", "ball4", "ball5", "pb",
            "white_object_ids", "powerball_object_id",
        ):
            q[key] = "MASKED"
    return q

def export_csv(path, predicate, mask_sealed_draw=False):
    with (OUT / path).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            if not predicate(row):
                continue
            writer.writerow(masked_row(row) if mask_sealed_draw else row)

export_csv("DEVELOPMENT.csv", lambda r: r["split"] == "development")
export_csv("VALIDATION.csv", lambda r: r["split"] == "validation")
export_csv("CONTEXT_PRETESTS_ALL.csv", lambda r: r["type_class"] == "Pre-test")
export_csv("SEALED_WORKING_VIEW.csv", lambda r: r["split"] == "sealed_test", True)
export_csv("PRIMARY_WORKING_VIEW.csv", lambda r: True, True)

# Store sealed truth only in the separately hashed vault.
sealed_truth = []
for block in canonical_blocks:
    if block["split"] != "sealed_test":
        continue
    event = block["draw"]
    sealed_truth.append({
        "date": block["canonical_date"],
        "matrix_line": event["matrix_line"],
        "type_raw": event["type_raw"],
        "wm": event["wm"],
        "ws": event["ws"],
        "pm": event["pm"],
        "ps": event["ps"],
        "pp_raw": event["pp_raw"],
        "balls": event["balls"],
        "pb": event["pb"],
        "white_object_ids": [f"WS:{event['ws']}:B:{x}" for x in event["balls"]],
        "powerball_object_id": f"PS:{event['ps']}:B:{event['pb']}",
    })
truth_bytes = (json.dumps(sealed_truth, sort_keys=True, separators=(",", ":")) + "\n").encode()
(VAULT / "SEALED_TRUTH.json").write_bytes(truth_bytes)
(VAULT / "SEALED_TRUTH.sha256").write_text(
    sha256_bytes(truth_bytes) + "  SEALED_TRUTH.json\n"
)

# Write safe audit ledgers. They contain no sealed draw-number payloads.
(OUT / "ANOMALY_LEDGER.json").write_text(
    json.dumps(anomalies, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
(OUT / "BLOCKING_ANOMALIES.json").write_text(
    json.dumps(blocking, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

scheduled_split_counts = Counter(split_for(d)[1] for d in EXPECTED_DATES)
observable_split_counts = Counter(block["split"] for block in canonical_blocks)
source_missing_split_counts = Counter(split_for(d)[1] for d in missing_dates)

status = (
    "BLOCKED"
    if blocking
    else "QUALIFIED_WITH_SOURCE_MISSINGNESS"
    if missing_dates
    else "QUALIFIED_COMPLETE"
)
summary = {
    "experiment": EXP,
    "execution_amendment": EXECUTION_AMENDMENT,
    "qualification_status": status,
    "source_url": URL,
    "source_sha256": source_sha,
    "source_snapshot_sha256_expected": EXPECTED_SOURCE_SHA256,
    "extracted_text_sha256": text_sha,
    "pdf_bytes": len(pdf),
    "matrix_start": START.isoformat(),
    "cutoff": CUTOFF.isoformat(),
    "scheduled_dates": len(EXPECTED_DATES),
    "observable_physical_dates": len(canonical_blocks),
    "observable_primary_rows": len(rows),
    "scheduled_split_counts": dict(sorted(scheduled_split_counts.items())),
    "observable_split_counts": dict(sorted(observable_split_counts.items())),
    "source_unavailable_dates": missing_dates,
    "source_unavailable_split_counts": dict(sorted(source_missing_split_counts.items())),
    "unexpected_dates": extra_dates,
    "anomaly_count": len(anomalies),
    "blocking_anomaly_count": len(blocking),
    "anomaly_breakdown": dict(sorted(Counter(a["kind"] for a in anomalies).items())),
    "sealed_truth_rows": len(sealed_truth),
    "sealed_truth_sha256": sha256_bytes(truth_bytes),
    "full_schedule_complete": len(missing_dates) == 0,
    "scoring_scope": "frozen_observable_physical_corpus_only",
    "scoring_authorized": len(blocking) == 0,
}
(OUT / "QUALIFICATION_SUMMARY.json").write_text(
    json.dumps(summary, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
(OUT / "SOURCE_HASHES.txt").write_text(
    f"{source_sha}  powerball-pre-test.pdf\n"
    f"{text_sha}  powerball-pre-test-layout.txt\n"
    f"{sha256_bytes(truth_bytes)}  SEALED_TRUTH.json\n",
    encoding="utf-8",
)

print(json.dumps(summary, indent=2, sort_keys=True))
print("=== BLOCKING ANOMALY BREAKDOWN ===")
print(json.dumps(dict(sorted(Counter(a["kind"] for a in blocking).items())), indent=2))
