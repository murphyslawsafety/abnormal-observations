#!/usr/bin/env python3
from __future__ import annotations

import hashlib, json, math, random
from collections import defaultdict
from pathlib import Path

import numpy as np

EXP = "ROX-0002B"
BURN = 1000
NREC = 20000
NDEV = 10000
NVAL = 5000
NTEST = 5000
LN100 = math.log(100.0)

def seed(tag: str) -> int:
    return int.from_bytes(hashlib.sha256(f"{EXP}|{tag}".encode()).digest()[:8], "big")

def rng_for(tag: str) -> random.Random:
    return random.Random(seed(tag))

def noise(kind, idx, edge):
    rng = rng_for(f"NOISE|{kind}|{idx}|{edge}")
    return rng.uniform(0.06, 0.14)

def generate(kind: str, idx: int):
    rng = rng_for(f"GEN|{kind}|{idx}")
    pa = noise(kind, idx, "A")
    pz = noise(kind, idx, "Z")
    pm = noise(kind, idx, "M")
    s = seed(f"S0|{kind}|{idx}") & 1
    m = seed(f"M0|{kind}|{idx}") & 1
    rows = []
    for t in range(BURN + NREC):
        if kind == "BREAK_MA":
            a = rng.randrange(2)
        else:
            ea = 1 if rng.random() < pa else 0
            a = m ^ s ^ ea

        if kind == "BREAK_AZ":
            z = rng.randrange(2)
        else:
            ez = 1 if rng.random() < pz else 0
            z = a ^ s ^ ez

        em = 1 if rng.random() < pm else 0
        if kind == "BREAK_ZM":
            mp = m ^ em
        else:
            mp = m ^ z ^ em

        if t >= BURN:
            rows.append((s, m, a, z, mp))

        es = 1 if rng.random() < 0.08 else 0
        s = s ^ es
        m = mp

    opaque = hashlib.sha256(f"{kind}|{idx}|{seed('OPAQUE')}".encode()).hexdigest()[:12]
    return {
        "opaque_id": opaque,
        "truth": kind,
        "noise": {"A": pa, "Z": pz, "M": pm},
        "data": np.asarray(rows, dtype=np.int8),
    }

def fit_conditional(data, target_col, cond_cols, rows):
    counts = defaultdict(lambda: [1.0, 1.0])  # add-1 beta
    for t in rows:
        key = tuple(int(data[t, c]) for c in cond_cols)
        y = int(data[t, target_col])
        counts[key][y] += 1.0
    probs = {}
    for key, (c0, c1) in counts.items():
        probs[key] = c1 / (c0 + c1)
    return probs

def ll_conditional(model, data, target_col, cond_cols, rows):
    out = 0.0
    for t in rows:
        key = tuple(int(data[t, c]) for c in cond_cols)
        p = model.get(key, 0.5)
        y = int(data[t, target_col])
        p = min(1-1e-15, max(1e-15, p))
        out += math.log(p if y else (1-p))
    return out

def edge_models(data):
    dev = range(0, NDEV)
    models = {
        "E2_base": fit_conditional(data, 2, (0,), dev),      # A|S
        "E2_full": fit_conditional(data, 2, (0,1), dev),    # A|S,M
        "E3_base": fit_conditional(data, 3, (0,), dev),      # Z|S
        "E3_full": fit_conditional(data, 3, (0,2), dev),    # Z|S,A
        "E4_base": fit_conditional(data, 4, (1,), dev),      # M'|M
        "E4_full": fit_conditional(data, 4, (1,3), dev),    # M'|M,Z
    }
    return models

def score_edges(models, data, rows):
    n = len(list(rows))
    # reconstruct iterator after len consumption
    rows = list(rows)
    penalty = 0.5 * 2 * math.log(n)
    e2 = ll_conditional(models["E2_full"], data, 2, (0,1), rows) - ll_conditional(models["E2_base"], data, 2, (0,), rows) - penalty
    e3 = ll_conditional(models["E3_full"], data, 3, (0,2), rows) - ll_conditional(models["E3_base"], data, 3, (0,), rows) - penalty
    e4 = ll_conditional(models["E4_full"], data, 4, (1,3), rows) - ll_conditional(models["E4_base"], data, 4, (1,), rows) - penalty
    return {"E2": e2, "E3": e3, "E4": e4, "L_loop": min(e2,e3,e4)}

def classify(scores):
    e2,e3,e4 = scores["E2"], scores["E3"], scores["E4"]
    if e2 > LN100 and e3 > LN100 and e4 > LN100:
        return "LOOP"
    miss = []
    if e2 <= 0 and e3 > LN100 and e4 > LN100: miss.append("BREAK_MA")
    if e3 <= 0 and e2 > LN100 and e4 > LN100: miss.append("BREAK_AZ")
    if e4 <= 0 and e2 > LN100 and e3 > LN100: miss.append("BREAK_ZM")
    return miss[0] if len(miss)==1 else "UNIDENTIFIABLE"

def permute_within_strata(data, target_col, strata_cols, rows, tag):
    d = data.copy()
    rng = rng_for(tag)
    groups = defaultdict(list)
    for t in rows:
        key = tuple(int(d[t,c]) for c in strata_cols)
        groups[key].append(t)
    for key, idxs in groups.items():
        vals = [int(d[t,target_col]) for t in idxs]
        rng.shuffle(vals)
        for t,v in zip(idxs, vals):
            d[t,target_col] = v
    return d

def targeted_destruction(case, models):
    data = case["data"]
    rows = list(range(NDEV+NVAL, NREC))
    dma = permute_within_strata(data, 2, (0,), rows, f"DMA|{case['opaque_id']}")
    daz = permute_within_strata(data, 3, (0,), rows, f"DAZ|{case['opaque_id']}")
    dzm = permute_within_strata(data, 4, (1,), rows, f"DZM|{case['opaque_id']}")
    s_ma = score_edges(models, dma, rows)["E2"]
    s_az = score_edges(models, daz, rows)["E3"]
    s_zm = score_edges(models, dzm, rows)["E4"]

    shift = data.copy()
    vals = shift[rows,4].copy()
    vals = np.roll(vals, 1)
    shift[rows,4] = vals
    s_shift = score_edges(models, shift, rows)["E4"]

    return {
        "D_MA_E2": s_ma,
        "D_AZ_E3": s_az,
        "D_ZM_E4": s_zm,
        "closure_shift_E4": s_shift,
        "pass": bool(s_ma <= 0 and s_az <= 0 and s_zm <= 0 and s_shift <= 0),
    }

def flip_representation(data, opaque_id):
    d = data.copy()
    rng = rng_for(f"FLIP|{opaque_id}")
    fs = rng.randrange(2)
    fm = rng.randrange(2)
    fa = rng.randrange(2)
    fz = rng.randrange(2)
    if fs: d[:,0] = 1-d[:,0]
    if fm:
        d[:,1] = 1-d[:,1]
        d[:,4] = 1-d[:,4]
    if fa: d[:,2] = 1-d[:,2]
    if fz: d[:,3] = 1-d[:,3]
    return d, {"S":fs,"M_and_Mprime":fm,"A":fa,"Z":fz}

def main():
    cases = [generate(kind,i) for kind in ("LOOP","BREAK_MA","BREAK_AZ","BREAK_ZM") for i in range(4)]
    results = []
    correct = 0
    loops_ok = True
    broken_not_loop = True
    broken_good_or_one_unid = 0
    destruction_ok = True
    flip_mismatch = 0

    for c in cases:
        models = edge_models(c["data"])
        val_scores = score_edges(models, c["data"], range(NDEV, NDEV+NVAL))
        test_scores = score_edges(models, c["data"], range(NDEV+NVAL, NREC))
        pred = classify(test_scores)
        if pred == c["truth"]:
            correct += 1
        if c["truth"] == "LOOP" and pred != "LOOP":
            loops_ok = False
        if c["truth"] != "LOOP" and pred == "LOOP":
            broken_not_loop = False

        dest = None
        if c["truth"] == "LOOP":
            dest = targeted_destruction(c, models)
            destruction_ok &= dest["pass"]

        fd, flips = flip_representation(c["data"], c["opaque_id"])
        fmodels = edge_models(fd)
        fpred = classify(score_edges(fmodels, fd, range(NDEV+NVAL, NREC)))
        if fpred != pred:
            flip_mismatch += 1

        results.append({
            "opaque_id": c["opaque_id"],
            "truth": c["truth"],
            "prediction": pred,
            "noise": c["noise"],
            "VAL": val_scores,
            "TEST": test_scores,
            "destruction_controls": dest,
            "representation_flip": {"flips": flips, "prediction": fpred},
        })

    broken = [r for r in results if r["truth"] != "LOOP"]
    broken_correct = sum(r["prediction"] == r["truth"] for r in broken)
    broken_unid = sum(r["prediction"] == "UNIDENTIFIABLE" for r in broken)
    broken_gate = (broken_correct >= 11 and broken_correct + broken_unid == 12 and broken_not_loop)

    passed = (
        correct >= 15
        and loops_ok
        and broken_gate
        and destruction_ok
        and flip_mismatch == 0
        and broken_not_loop
    )

    out = {
        "experiment": EXP,
        "status": "CONTROL_PASS" if passed else "CONTROL_FAIL",
        "evidence_class": "architectural/methodological synthetic control",
        "cases_correct": correct,
        "cases_total": 16,
        "all_LOOP_classified_LOOP": bool(loops_ok),
        "broken_cases_correct": broken_correct,
        "broken_cases_unidentifiable": broken_unid,
        "no_broken_case_classified_LOOP": bool(broken_not_loop),
        "all_LOOP_destruction_controls_pass": bool(destruction_ok),
        "representation_flip_mismatch_count": flip_mismatch,
        "results": results,
        "claim_boundary": "Synthetic sufficient-state loop-topology discrimination only; no natural-domain or Powerball evidence.",
        "eureka_status": "NONE"
    }
    Path("ROX_0002B_RESULT_v1.0.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
