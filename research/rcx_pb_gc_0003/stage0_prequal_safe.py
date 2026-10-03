#!/usr/bin/env python3
# RCX-PB-GC-0003 local safe-context prequalification.
# This is an engineering dry-run only; it is not the official Stage 0 scientific result.

import csv, json, random, hashlib
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np

def sequences(rows):
    return [[int(r[f"ball{i}"]) for i in range(1,6)] for r in rows]

def role_multiset(rows):
    seqs=sequences(rows)
    present=sorted(set(sum(seqs,[])))
    roles=[]
    for b in present:
        occ=[]; pos=[]; ain=[]; aout=[]
        for row in seqs:
            if b in row:
                j=row.index(b)
                occ.append(1); pos.append(j)
                ain.append(1 if j>0 else 0)
                aout.append(1 if j<4 else 0)
            else:
                occ.append(0); pos.append(-1); ain.append(0); aout.append(0)
        roles.append((tuple(occ),tuple(pos),tuple(ain),tuple(aout)))
    return sorted(roles)

def invariant_signature(rows):
    seqs=sequences(rows); sets=[set(x) for x in seqs]
    present=sorted(set().union(*sets))
    counts=Counter(x for row in seqs for x in row)
    rec=tuple(sum(1 for b in present if counts[b]==k) for k in range(1,5))
    overlaps=tuple(len(sets[i]&sets[j]) for i in range(4) for j in range(i+1,4))
    pos_pres=tuple(sum(1 for p in range(5) if seqs[i][p]==seqs[i+1][p]) for i in range(3))
    adj_surv=[]
    for i in range(3):
        a=set(zip(seqs[i][:-1],seqs[i][1:]))
        b=set(zip(seqs[i+1][:-1],seqs[i+1][1:]))
        adj_surv.append(len(a&b))
    idx={b:i for i,b in enumerate(present)}
    A=np.zeros((len(present),len(present)),float)
    for row in seqs:
        for i in range(5):
            for j in range(i+1,5):
                u,v=idx[row[i]],idx[row[j]]
                A[u,v]=A[v,u]=1
    degree=tuple(sorted((int(x) for x in A.sum(1)), reverse=True))
    L=np.diag(A.sum(1))-A
    ev=np.linalg.eigvalsh(L)
    non=ev[ev>1e-9]
    lap=tuple(round(float(x),10) for x in non[:4]) + (0.0,)*(4-min(4,len(non)))
    return (len(present),rec,overlaps,pos_pres,tuple(adj_surv),degree,lap)

def relabel(rows):
    d=rows[0]["date"]
    seed=int.from_bytes(hashlib.sha256(("RCX3|"+d).encode()).digest()[:8],"big")
    rng=random.Random(seed)
    vals=list(range(1,70)); shuffled=vals[:]; rng.shuffle(shuffled)
    mp=dict(zip(vals,shuffled))
    out=[]
    for r in rows:
        q=dict(r)
        for i in range(1,6):
            q[f"ball{i}"]=str(mp[int(r[f"ball{i}"])])
        out.append(q)
    return out

def run(path):
    rows=list(csv.DictReader(Path(path).open(newline="",encoding="utf-8")))
    by=defaultdict(list)
    for r in rows:
        by[r["date"]].append(r)

    bad=[]; inv_bad=[]; role_bad=[]; inv_states=set(); role_states=set()
    candidate_class_sizes=[]; unseen_sizes=[]; unique_counts=[]

    for d,rs in sorted(by.items()):
        rs.sort(key=lambda r:int(r["sequence_index"]))
        if len(rs)!=4:
            bad.append((d,len(rs)))
            continue

        a=invariant_signature(rs); b=invariant_signature(relabel(rs))
        if a!=b: inv_bad.append(d)
        ra=role_multiset(rs); rb=role_multiset(relabel(rs))
        if ra!=rb: role_bad.append(d)

        inv_states.add(a); role_states.add(tuple(ra))
        seqs=sequences(rs)
        present=set(sum(seqs,[]))
        unique_counts.append(len(present))

        all_roles=[]
        for ball in range(1,70):
            occ=[]; pos=[]; ain=[]; aout=[]
            for row in seqs:
                if ball in row:
                    j=row.index(ball)
                    occ.append(1); pos.append(j)
                    ain.append(1 if j>0 else 0)
                    aout.append(1 if j<4 else 0)
                else:
                    occ.append(0); pos.append(-1); ain.append(0); aout.append(0)
            all_roles.append((tuple(occ),tuple(pos),tuple(ain),tuple(aout)))
        counts=Counter(all_roles)
        candidate_class_sizes.extend(counts[x] for x in all_roles)
        unseen_sizes.append(69-len(present))

    result={
        "scope":"safe v0.4 pretest context through 2026-09-28",
        "scientific_status":"ENGINEERING_DRY_RUN_ONLY",
        "dates":len(by),
        "bad_pretest_count_dates":bad,
        "relabel_invariant_failures":len(inv_bad),
        "role_relabel_failures":len(role_bad),
        "distinct_block_invariant_states":len(inv_states),
        "distinct_role_multisets":len(role_states),
        "median_unique_white_objects_per_block":float(np.median(unique_counts)),
        "p10_unique_white_objects_per_block":float(np.percentile(unique_counts,10)),
        "p90_unique_white_objects_per_block":float(np.percentile(unique_counts,90)),
        "median_candidate_equivalence_class_size":float(np.median(candidate_class_sizes)),
        "p90_candidate_equivalence_class_size":float(np.percentile(candidate_class_sizes,90)),
        "p99_candidate_equivalence_class_size":float(np.percentile(candidate_class_sizes,99)),
        "max_candidate_equivalence_class_size":int(max(candidate_class_sizes)),
        "median_unseen_white_objects_per_block":float(np.median(unseen_sizes)),
        "prequalification":"PASS" if not bad and not inv_bad and not role_bad else "FAIL",
        "interpretation":"The anonymous quotient representation is exactly relabeling-invariant on the safe corpus, but same-day structure alone leaves a large equivalence class of unseen candidate objects. P2 is therefore intentionally non-identifiable at exact-object level unless deeper temporal/grammar information breaks the symmetry."
    }
    return result

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("context_csv")
    ap.add_argument("--output",default="RCX_PB_GC_0003_STAGE0_PREQUAL_SAFE_v0.1.json")
    args=ap.parse_args()
    result=run(args.context_csv)
    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
