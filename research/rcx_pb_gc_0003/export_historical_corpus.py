#!/usr/bin/env python3
from __future__ import annotations
import csv, gzip, hashlib, json
from collections import defaultdict
from pathlib import Path
import importlib.util

ART=Path("artifact")
VAULT=Path("vault")
OUT=ART/"RCX_PB_GC_0003_HISTORICAL_CORPUS_v1.0.json.gz"

def load_csv(path):
    with path.open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))

def pretest_record(r):
    return {
        "sequence_index":int(r["sequence_index"]),
        "balls":[int(r[f"ball{i}"]) for i in range(1,6)],
        "pb":int(r["pb"]),
        "wm":int(r["wm"]),"ws":int(r["ws"]),
        "pm":int(r["pm"]),"ps":int(r["ps"]),
    }

ctx=load_csv(ART/"CONTEXT_PRETESTS_ALL.csv")
pre=defaultdict(list)
for r in ctx:
    if r["type_class"]=="Pre-test":
        pre[r["date"]].append(pretest_record(r))
for d in pre:
    pre[d].sort(key=lambda x:x["sequence_index"])
    if len(pre[d])!=4:
        raise SystemExit(f"bad pretest count {d}: {len(pre[d])}")

draws={}
for fn in ("DEVELOPMENT.csv","VALIDATION.csv"):
    for r in load_csv(ART/fn):
        if r["type_class"]=="Draw":
            draws[r["date"]]={"balls":[int(r[f"ball{i}"]) for i in range(1,6)],"pb":int(r["pb"])}

sealed=json.loads((VAULT/"SEALED_TRUTH.json").read_text(encoding="utf-8"))
for rec in sealed:
    draws[rec["date"]]={"balls":[int(x) for x in rec["balls"]],"pb":int(rec["pb"])}

if len(draws)!=1412:
    raise SystemExit(f"expected 1412 through 2026-09-28, got {len(draws)}")
if set(draws)!=set(pre):
    raise SystemExit("pretest/draw date mismatch before 2026-09-30 append")

scorer=Path("research/rcx_pb_gc_0002/live_score.py")
spec=importlib.util.spec_from_file_location("live",scorer)
live=importlib.util.module_from_spec(spec); spec.loader.exec_module(live)
events, source_meta = live.source_events_for_date("2026-09-30")
pt=[e for e in events if e["type_class"]=="Pre-test"]
dr=[e for e in events if e["type_class"]=="Draw"]
if len(pt)!=4 or len(dr)!=1:
    raise SystemExit(f"2026-09-30 parse mismatch pre={len(pt)} draw={len(dr)}")
pre["2026-09-30"]=[
    {"sequence_index":i,"balls":e["balls"],"pb":e["pb"],"wm":e["wm"],"ws":e["ws"],"pm":e["pm"],"ps":e["ps"]}
    for i,e in enumerate(pt)
]
draws["2026-09-30"]={"balls":dr[0]["balls"],"pb":dr[0]["pb"]}

dates=sorted(draws)
records=[{"date":d,"pretests":pre[d],"draw":draws[d]} for d in dates]
payload={
    "experiment":"RCX-PB-GC-0003",
    "artifact":"historical_corpus_v1.0",
    "matrix":"5/69+1/26",
    "start_date":dates[0],
    "cutoff":"2026-09-30",
    "usable_completed_blocks":len(records),
    "declared_source_gap":["2025-03-01"],
    "source_url":source_meta["source_url"],
    "source_sha256":source_meta["source_sha256"],
    "source_bytes":source_meta["source_bytes"],
    "parent_qualification_source_sha256":"75e66acebe26b9e6803e80e1e4b156f54e0db0e1da8af9f4975a21d784d547f4",
    "records":records,
}
raw=(json.dumps(payload,sort_keys=True,separators=(",",":"))+"\n").encode()
with OUT.open("wb") as fout:
    with gzip.GzipFile(filename="", mode="wb", fileobj=fout, compresslevel=9, mtime=0) as f:
        f.write(raw)
sha=hashlib.sha256(OUT.read_bytes()).hexdigest()
(ART/"RCX_PB_GC_0003_HISTORICAL_CORPUS_v1.0.sha256").write_text(
    sha+"  RCX_PB_GC_0003_HISTORICAL_CORPUS_v1.0.json.gz\n",encoding="utf-8")
receipt={k:payload[k] for k in payload if k!="records"}
receipt["gzip_sha256"]=sha
(ART/"RCX_PB_GC_0003_HISTORICAL_CORPUS_RECEIPT_v1.0.json").write_text(
    json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print(json.dumps(receipt,indent=2,sort_keys=True))
