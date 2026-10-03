#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
from collections import defaultdict
from pathlib import Path

import numpy as np

WINDOWS=(1,4,16,64)
P0=0.1
SMOOTH=4.0
TOL=1e-12

PRETEST_SHA='6da5a5e2c3c5db14108728da3558b23a69806563b008e5fcd7292886394ca08a'
WIN_SHA='6da25276edac5da7c1aece3db1c145a8b377be9b2821eaf2731124d4e9a5c090'

def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def date_key(r):
    return f'{int(r[3]):04d}-{int(r[1]):02d}-{int(r[2]):02d}'

def load_pretest(path):
    by=defaultdict(list)
    with open(path,newline='',encoding='utf-8') as f:
        for r in csv.reader(f):
            y=int(r[3])
            if y in (2013,2014):
                by[date_key(r)].append(r)
    used={}
    for d,rows in by.items():
        chamber=[]
        for ch in range(4):
            vals=set()
            for r in rows:
                if r[8+2*ch].strip()=='*':
                    vals.add(r[7+2*ch].strip())
                if r[18+2*ch].strip()=='*':
                    vals.add(r[17+2*ch].strip())
            if len(vals)!=1:
                raise SystemExit(f'used ball set not uniquely resolved: {d} chamber {ch+1}: {sorted(vals)}')
            chamber.append(next(iter(vals)))
        used[d]=chamber
    return used

def load_wins(path):
    out={}
    with open(path,newline='',encoding='utf-8') as f:
        for r in csv.reader(f):
            y=int(r[3])
            if y in (2013,2014):
                d=date_key(r)
                digits=[int(r[i]) for i in range(4,8)]
                if any(x<0 or x>9 for x in digits):
                    raise SystemExit(f'bad digit range {d}')
                if d in out:
                    raise SystemExit(f'duplicate outcome {d}')
                out[d]=digits
    return out

def score_digit(history, b):
    vals=[]
    for W in WINDOWS:
        q=history[-W:]
        n=len(q)
        c=sum(1 for x in q if x==b)
        r=(c+SMOOTH*P0)/(n+SMOOTH)
        vals.append(math.log(r/P0))
    return sum(vals)/len(vals)

def auc_one(scores, selected):
    s=scores[selected]
    total=0.0
    for b,v in enumerate(scores):
        if b==selected: continue
        total += 1.0 if s>v else (0.5 if s==v else 0.0)
    return total/9.0

def summary(date_rows):
    vals=np.array([x['date_auc'] for x in date_rows],float)
    B=len(vals)//20
    blocks=np.array([vals[i*20:(i+1)*20].mean() for i in range(B)],float)
    if B>=2 and blocks.std(ddof=1)>0:
        z=float((blocks.mean()-0.5)/(blocks.std(ddof=1)/math.sqrt(B)))
    elif blocks.mean()>0.5: z=float('inf')
    elif blocks.mean()<0.5: z=float('-inf')
    else: z=0.0
    terc=[float(x.mean()) for x in np.array_split(vals,3)]
    chamber=[float(np.mean([r['chamber_auc'][c] for r in date_rows])) for c in range(4)]
    pos_frac=float(np.mean(blocks>0.5)) if B else 0.0
    candidate=(
        float(vals.mean())>0.5 and z>=3.0 and pos_frac>=0.60 and
        all(x>0.5 for x in terc) and sum(x>0.5 for x in chamber)>=3
    )
    return {
        'n_dates':len(date_rows),
        'mean_date_auc':float(vals.mean()),
        'mean_date_auc_minus_half':float(vals.mean()-0.5),
        'chamber_mean_auc':chamber,
        'chronological_tercile_mean_auc':terc,
        'full_20_date_blocks':int(B),
        'positive_block_count':int(np.sum(blocks>0.5)),
        'positive_block_fraction':pos_frac,
        'block_z':z,
        'block_mean_auc':[float(x) for x in blocks],
        'candidate_replication':bool(candidate),
    }

def run(used,wins,relabel_maps=None):
    hist=defaultdict(list)
    rows=[]
    dates=sorted(set(used)&set(wins))

    for d in dates:
        year=int(d[:4])
        sets=used[d]
        digits=wins[d]
        chamber_auc=[]

        for c in range(4):
            set_id=sets[c]
            key=(c,set_id)
            selected=digits[c]
            if relabel_maps is not None:
                selected=relabel_maps[key][selected]
            scores=[score_digit(hist[key],b) for b in range(10)]
            if year==2014:
                chamber_auc.append(auc_one(scores,selected))
            hist[key].append(selected)

        if year==2014:
            if len(chamber_auc)!=4:
                raise SystemExit(f'incomplete chamber AUC {d}')
            rows.append({'date':d,'chamber_auc':chamber_auc,'date_auc':float(np.mean(chamber_auc))})

    return rows

def make_relabel_maps(used):
    keys=set()
    for d,sets in used.items():
        for c,s in enumerate(sets): keys.add((c,s))
    out={}
    for key in sorted(keys):
        seed=int.from_bytes(hashlib.sha256(f'RCX-PB-XFER-0001|RELABEL|{key[0]}|{key[1]}'.encode()).digest()[:8],'big')
        rng=random.Random(seed)
        vals=list(range(10)); perm=vals[:]; rng.shuffle(perm)
        out[key]=dict(zip(vals,perm))
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('pretest_csv')
    ap.add_argument('winning_csv')
    ap.add_argument('--output',default='RCX_PB_XFER_0001_ACTUAL_v1.0.json')
    args=ap.parse_args()

    if file_sha(args.pretest_csv)!=PRETEST_SHA: raise SystemExit('pretest source hash mismatch')
    if file_sha(args.winning_csv)!=WIN_SHA: raise SystemExit('winning source hash mismatch')

    used=load_pretest(args.pretest_csv)
    wins=load_wins(args.winning_csv)
    if len([d for d in used if d.startswith('2013')])!=98: raise SystemExit('2013 pretest date count mismatch')
    if len([d for d in used if d.startswith('2014')])!=313: raise SystemExit('2014 pretest date count mismatch')
    if set(used)!=set(wins): raise SystemExit('pretest/winning date mismatch')

    actual=run(used,wins)
    s=summary(actual)

    maps=make_relabel_maps(used)
    rel=run(used,wins,maps)
    maxdiff=max(abs(a['date_auc']-b['date_auc']) for a,b in zip(actual,rel))
    chdiff=max(abs(a['chamber_auc'][c]-b['chamber_auc'][c]) for a,b in zip(actual,rel) for c in range(4))
    integrity={'pass':max(maxdiff,chdiff)<=TOL,'max_abs_date_auc_diff':maxdiff,'max_abs_chamber_auc_diff':chdiff,'tolerance':TOL}

    status='CANDIDATE_REPLICATION' if s['candidate_replication'] and integrity['pass'] else 'FAIL'
    out={
        'experiment':'RCX-PB-XFER-0001',
        'status':status,
        'pretest_source_sha256':PRETEST_SHA,
        'winning_source_sha256':WIN_SHA,
        'initialization_year':2013,
        'evaluation_year':2014,
        'initialization_dates':98,
        'evaluation_dates':len(actual),
        'summary':s,
        'relabel_integrity':integrity,
        'null_campaign_authorized':bool(status=='CANDIDATE_REPLICATION'),
        'eureka_status':'NONE',
        'per_date':actual,
    }
    Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    report=dict(out); report.pop('per_date')
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=='__main__':
    main()
