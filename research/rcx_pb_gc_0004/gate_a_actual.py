#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import random
from collections import defaultdict
from pathlib import Path

import numpy as np

WHITE_N = 69
PB_N = 26
WHITE_K = 5
P0_W = WHITE_K / WHITE_N
P0_P = 1 / PB_N
A_W = 20 * WHITE_N
A_P = 20 * PB_N
WINDOWS = (1, 4, 16, 64)
WARMUP = 200
TOL = 1e-12

def load_corpus(path: str):
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        return json.load(f)

def final_white_set(rec):
    return int(rec['pretests'][-1]['ws'])

def final_pb_set(rec):
    return int(rec['pretests'][-1]['ps'])

def white_regime(rec):
    return tuple((int(r['wm']), int(r['ws'])) for r in rec['pretests'])

def pb_regime(rec):
    return tuple((int(r['pm']), int(r['ps'])) for r in rec['pretests'])

def white_fp(rec, candidate: int):
    cur_set = final_white_set(rec)
    out = []
    for r in rec['pretests']:
        if int(r['ws']) != cur_set:
            out.append(-1); continue
        seq = list(map(int, r['balls']))
        try: out.append(seq.index(candidate))
        except ValueError: out.append(-1)
    return tuple(out)

def pb_fp(rec, candidate: int):
    cur_set = final_pb_set(rec)
    out = []
    for r in rec['pretests']:
        if int(r['ps']) != cur_set: out.append(0)
        else: out.append(1 if int(r['pb']) == candidate else 0)
    return tuple(out)

def logit(p):
    eps = 1e-15
    p = min(1-eps, max(eps, float(p)))
    return math.log(p/(1-p))

def midranks(scores):
    scores = np.asarray(scores, float)
    n = len(scores)
    order = np.argsort(scores, kind='mergesort')
    ranks = np.empty(n, float)
    i = 0
    while i < n:
        j = i + 1; v = scores[order[i]]
        while j < n and scores[order[j]] == v: j += 1
        mid = (i + j - 1) / 2.0
        ranks[order[i:j]] = mid
        i = j
    if n == 1: return np.array([0.5])
    return ranks / (n - 1)

def auc_selected(scores, selected_labels, n_obj):
    selected = set(int(x) for x in selected_labels)
    pos = [scores[i-1] for i in sorted(selected)]
    neg = [scores[i-1] for i in range(1, n_obj+1) if i not in selected]
    total = 0.0; count = 0
    for a in pos:
        for b in neg:
            total += 1.0 if a > b else (0.5 if a == b else 0.0)
            count += 1
    return total / count

def component_summary(values):
    vals = np.asarray(values, float)
    n = len(vals); B = n // 30
    blocks = np.array([vals[i*30:(i+1)*30].mean() for i in range(B)], float)
    mean_auc = float(vals.mean())
    if B >= 2 and float(blocks.std(ddof=1)) > 0:
        z = float((blocks.mean() - 0.5) / (blocks.std(ddof=1)/math.sqrt(B)))
    elif blocks.mean() > 0.5: z = float('inf')
    elif blocks.mean() < 0.5: z = float('-inf')
    else: z = 0.0
    terciles = [float(x.mean()) for x in np.array_split(vals, 3)]
    pos_frac = float(np.mean(blocks > 0.5)) if B else 0.0
    candidate = (
        mean_auc > 0.5 and z >= 3.0 and pos_frac >= 0.60
        and all(x > 0.5 for x in terciles)
    )
    return {
        'n_targets': n, 'mean_auc': mean_auc,
        'mean_auc_minus_half': mean_auc - 0.5,
        'full_30_target_blocks': int(B),
        'positive_block_fraction': pos_frac,
        'positive_block_count': int(np.sum(blocks > 0.5)),
        'block_z': z, 'tercile_mean_auc': terciles,
        'gate_a_candidate': bool(candidate),
        'block_mean_auc': [float(x) for x in blocks],
    }

class HazardTables:
    def __init__(self):
        self.g = defaultdict(lambda: [0,0])
        self.s = defaultdict(lambda: [0,0])
        self.r = defaultdict(lambda: [0,0])

    def score(self, fp, set_id, regime, p0, alpha):
        sg, eg = self.g[fp]
        pG = (sg + alpha*p0)/(eg + alpha)
        ss, es = self.s[(set_id, fp)]
        pS = (ss + alpha*pG)/(es + alpha)
        sr, er = self.r[(regime, fp)]
        pR = (sr + alpha*pS)/(er + alpha)
        return logit(pR)

    def update(self, fp, set_id, regime, selected):
        for tab, key in (
            (self.g, fp),
            (self.s, (set_id, fp)),
            (self.r, (regime, fp))
        ):
            tab[key][1] += 1
            if selected: tab[key][0] += 1

def temporal_score(hist, candidate, p0):
    vals = []
    for W in WINDOWS:
        q = hist[-W:]
        n = len(q)
        c = sum(1 for selected in q if candidate in selected)
        rate = (c + 4*p0)/(n + 4)
        vals.append(math.log(rate/p0))
    return sum(vals)/len(vals)

def run_records(records):
    hW = HazardTables(); hP = HazardTables()
    histW = defaultdict(list); histP = defaultdict(list)
    aucs = {k: [] for k in (
        'W1_white','W2_white','W3_white',
        'W1_pb','W2_pb','W3_pb'
    )}
    per_target = []

    for idx, rec in enumerate(records):
        ws = final_white_set(rec); ps = final_pb_set(rec)
        wr = white_regime(rec); pr = pb_regime(rec)

        w1 = np.array([
            hW.score(white_fp(rec,b), ws, wr, P0_W, A_W)
            for b in range(1,WHITE_N+1)
        ], float)
        w2 = np.array([
            temporal_score(histW[ws], b, P0_W)
            for b in range(1,WHITE_N+1)
        ], float)
        w3 = 0.5*midranks(w1) + 0.5*midranks(w2)

        p1 = np.array([
            hP.score(pb_fp(rec,b), ps, pr, P0_P, A_P)
            for b in range(1,PB_N+1)
        ], float)
        p2 = np.array([
            temporal_score(histP[ps], b, P0_P)
            for b in range(1,PB_N+1)
        ], float)
        p3 = 0.5*midranks(p1) + 0.5*midranks(p2)

        if idx >= WARMUP:
            draw_w = list(map(int, rec['draw']['balls']))
            draw_p = int(rec['draw']['pb'])
            target = {
                'date': rec['date'],
                'W1_white': auc_selected(w1, draw_w, WHITE_N),
                'W2_white': auc_selected(w2, draw_w, WHITE_N),
                'W3_white': auc_selected(w3, draw_w, WHITE_N),
                'W1_pb': auc_selected(p1, [draw_p], PB_N),
                'W2_pb': auc_selected(p2, [draw_p], PB_N),
                'W3_pb': auc_selected(p3, [draw_p], PB_N),
            }
            per_target.append(target)
            for k in aucs: aucs[k].append(target[k])

        draw_set = set(map(int, rec['draw']['balls']))
        for b in range(1,WHITE_N+1):
            hW.update(white_fp(rec,b), ws, wr, b in draw_set)
        hP_selected = int(rec['draw']['pb'])
        for b in range(1,PB_N+1):
            hP.update(pb_fp(rec,b), ps, pr, b == hP_selected)
        histW[ws].append(draw_set)
        histP[ps].append({hP_selected})

    summaries = {k: component_summary(v) for k,v in aucs.items()}
    return summaries, per_target

def deterministic_relabel(records):
    maps_w = {}; maps_p = {}
    def make_map(n, key):
        seed = int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], 'big')
        rng = random.Random(seed)
        vals = list(range(1,n+1)); perm = vals[:]; rng.shuffle(perm)
        return dict(zip(vals,perm))

    out = []
    for rec in records:
        q = json.loads(json.dumps(rec))
        for row in q['pretests']:
            ws = int(row['ws']); ps = int(row['ps'])
            if ws not in maps_w:
                maps_w[ws] = make_map(WHITE_N, f'RCX-PB-GC-0004|RELABEL|W|{ws}')
            if ps not in maps_p:
                maps_p[ps] = make_map(PB_N, f'RCX-PB-GC-0004|RELABEL|P|{ps}')
            row['balls'] = [maps_w[ws][int(x)] for x in row['balls']]
            row['pb'] = maps_p[ps][int(row['pb'])]

        ws = int(q['pretests'][-1]['ws'])
        ps = int(q['pretests'][-1]['ps'])
        if ws not in maps_w:
            maps_w[ws] = make_map(WHITE_N, f'RCX-PB-GC-0004|RELABEL|W|{ws}')
        if ps not in maps_p:
            maps_p[ps] = make_map(PB_N, f'RCX-PB-GC-0004|RELABEL|P|{ps}')
        q['draw']['balls'] = [maps_w[ws][int(x)] for x in q['draw']['balls']]
        q['draw']['pb'] = maps_p[ps][int(q['draw']['pb'])]
        out.append(q)
    return out

def compare_relabel(per_a, per_b):
    if len(per_a) != len(per_b):
        return {'pass': False, 'reason': 'target_count_mismatch'}
    max_abs = 0.0; bad = 0
    for a,b in zip(per_a, per_b):
        if a['date'] != b['date']:
            return {'pass': False, 'reason': 'date_mismatch'}
        for k in (
            'W1_white','W2_white','W3_white',
            'W1_pb','W2_pb','W3_pb'
        ):
            d = abs(a[k]-b[k]); max_abs = max(max_abs,d)
            if d > TOL: bad += 1
    return {
        'pass': bad == 0,
        'max_abs_auc_difference': max_abs,
        'violations': bad,
        'tolerance': TOL
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('corpus')
    ap.add_argument('--output', default='RCX_PB_GC_0004_GATE_A_ACTUAL_v1.0.json')
    args = ap.parse_args()

    payload = load_corpus(args.corpus)
    records = payload['records']
    if len(records) != 1413:
        raise SystemExit(f'corpus count mismatch: {len(records)}')
    if payload.get('cutoff') != '2026-09-30':
        raise SystemExit('corpus cutoff mismatch')

    summaries, per = run_records(records)
    rel_records = deterministic_relabel(records)
    _, rel_per = run_records(rel_records)
    integrity = compare_relabel(per, rel_per)

    candidates = [k for k,v in summaries.items() if v['gate_a_candidate']]
    status = 'GATE_A_CANDIDATE' if candidates and integrity['pass'] else 'FAIL'

    out = {
        'experiment': 'RCX-PB-GC-0004',
        'stage': 'ACTUAL_HISTORY_CHEAP_SCREEN',
        'status': status,
        'corpus_sha256_expected':
            'ffc95ec931d6c0d6ba7a92a39c4385b9a8c93e243ae8a25826c9b02e5e21048b',
        'corpus_blocks': len(records),
        'warmup_blocks': WARMUP,
        'eligible_targets': len(per),
        'first_target': per[0]['date'],
        'last_target': per[-1]['date'],
        'gate_a_candidates': candidates,
        'component_summaries': summaries,
        'representation_integrity_relabel': integrity,
        'mapping_note':
            'For rare within-day ball-set discontinuities, candidate physical identity and draw identity are associated with the final pretest set; pretest rows from a different set do not count as appearances of the final-set object.',
        'null_campaign_authorized': bool(status == 'GATE_A_CANDIDATE'),
        'eureka_status': 'NONE',
        'per_target_auc': per,
    }
    Path(args.output).write_text(
        json.dumps(out, indent=2, sort_keys=True)+'\n',
        encoding='utf-8'
    )
    summary = dict(out); summary.pop('per_target_auc')
    print(json.dumps(summary, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
