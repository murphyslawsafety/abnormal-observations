#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

EXPERIMENT = "RCX-PB-GRAMMAR-0001"

A = (3, 2, 1, 0, 4)
B = (3, 4, 2, 0, 1)
C = (3, 4, 2, 1, 0)
TRUE_G = (A, B, C)

N_DEV = 3000
N_VAL = 1000
N_TEST = 1000

def seed(tag: str) -> int:
    return int.from_bytes(hashlib.sha256(f"{EXPERIMENT}|{tag}".encode()).digest()[:8], "big")

def compose(p, q):
    # p after q
    return tuple(p[q[i]] for i in range(5))

def apply_perm(row, p):
    out = [None] * 5
    for i, value in enumerate(row):
        out[p[i]] = value
    return tuple(out)

def reconstruct_operator(a, b):
    pos = {value: j for j, value in enumerate(b)}
    if len(pos) != 5 or len(set(a)) != 5:
        raise ValueError("rows must contain five unique identities")
    try:
        return tuple(pos[value] for value in a)
    except KeyError as e:
        raise ValueError("synthetic qualification requires complete identity survival") from e

def h_true_from_word(word):
    h = tuple(range(5))
    for idx in word:
        h = compose(TRUE_G[idx], h)
    return h

def true_completion_index(word):
    h = h_true_from_word(word)
    good = [i for i, g in enumerate(TRUE_G) if compose(g, h)[0] == 1]
    if len(good) != 1:
        raise RuntimeError(f"unique-completion property failed for {word}: {good}")
    return good[0]

WORDS_BY_COMPLETION = defaultdict(list)
for i in range(3):
    for j in range(3):
        for k in range(3):
            w = (i, j, k)
            WORDS_BY_COMPLETION[true_completion_index(w)].append(w)

if sorted(len(v) for v in WORDS_BY_COMPLETION.values()) != [3, 6, 18]:
    raise RuntimeError("unexpected completion-class word counts")

def generate_split(n, tag):
    rng = random.Random(seed(tag))
    blocks = []
    for _ in range(n):
        desired = rng.randrange(3)
        word = rng.choice(WORDS_BY_COMPLETION[desired])

        labels = tuple(rng.sample(range(1, 1_000_000_000), 5))
        rows = [labels]
        cur = labels
        for op_idx in word:
            cur = apply_perm(cur, TRUE_G[op_idx])
            rows.append(cur)

        t4d = TRUE_G[desired]
        cur = apply_perm(cur, t4d)
        rows.append(cur)

        blocks.append({
            "rows": [list(r) for r in rows],
            "desired_completion_index": desired,
            "hidden_word_indices": list(word),
        })
    return blocks

def parse_block(block):
    rows = [tuple(r) for r in block["rows"]]
    if len(rows) != 5:
        raise ValueError("expected five rows")
    t12 = reconstruct_operator(rows[0], rows[1])
    t23 = reconstruct_operator(rows[1], rows[2])
    t34 = reconstruct_operator(rows[2], rows[3])
    t4d = reconstruct_operator(rows[3], rows[4])
    h = compose(t34, compose(t23, t12))
    h_rev = compose(t12, compose(t23, t34))
    w = compose(t4d, h)
    return {
        "t12": t12, "t23": t23, "t34": t34, "t4d": t4d,
        "h": h, "h_rev": h_rev, "w": w,
    }

def discover_primitives(parsed_dev):
    c = Counter()
    for x in parsed_dev:
        c[x["t12"]] += 1
        c[x["t23"]] += 1
        c[x["t34"]] += 1
        c[x["t4d"]] += 1
    # The synthetic qualification is defined around a three-generator alphabet.
    # Restrict the discovered alphabet to signatures appearing in pretest transitions;
    # completion signatures must belong to the same discovered set.
    p = Counter()
    for x in parsed_dev:
        p[x["t12"]] += 1
        p[x["t23"]] += 1
        p[x["t34"]] += 1
    primitives = tuple(sorted(p))
    return primitives, c

def train_operation_lookup(parsed_dev):
    votes = defaultdict(Counter)
    for x in parsed_dev:
        votes[x["h"]][x["t4d"]] += 1

    lookup = {}
    conflicts = 0
    for h, ctr in votes.items():
        max_n = max(ctr.values())
        winners = sorted(k for k, v in ctr.items() if v == max_n)
        lookup[h] = winners[0]
        if len(ctr) > 1:
            conflicts += 1
    return lookup, votes, conflicts

def select_invariant(parsed_dev):
    support = {}
    for k in range(5):
        support[k] = sum(1 for x in parsed_dev if x["w"][0] == k)
    max_s = max(support.values())
    winners = [k for k, v in support.items() if v == max_s]
    return min(winners), support

def op_predict(lookup, h):
    return lookup.get(h)

def inv_predict(primitives, h, kstar):
    good = [g for g in primitives if compose(g, h)[0] == kstar]
    if len(good) == 1:
        return good[0]
    return None

def evaluate(parsed, lookup, primitives, kstar, use_reversed=False, outcome_override=None):
    op_correct = 0
    inv_correct = 0
    inv_ident = 0
    agree = 0
    unseen = 0
    n = len(parsed)

    for i, x in enumerate(parsed):
        h = x["h_rev"] if use_reversed else x["h"]
        truth = x["t4d"] if outcome_override is None else outcome_override[i]

        op = op_predict(lookup, h)
        inv = inv_predict(primitives, h, kstar)

        if op is None:
            unseen += 1
        if op == truth:
            op_correct += 1
        if inv is not None:
            inv_ident += 1
            if inv == truth:
                inv_correct += 1
        if op is not None and inv is not None and op == inv:
            agree += 1

    return {
        "n": n,
        "operation_accuracy": op_correct / n,
        "invariant_identifiable_fraction": inv_ident / n,
        "invariant_accuracy_all_blocks": inv_correct / n,
        "operation_invariant_agreement": agree / n,
        "unseen_h_count": unseen,
    }

def relabel_blocks(blocks, tag):
    rng = random.Random(seed(tag))
    out = []
    for b in blocks:
        flat = sorted(set(v for row in b["rows"] for v in row))
        if len(flat) != 5:
            raise RuntimeError("unexpected synthetic identity count")
        new = rng.sample(range(1_000_000_001, 2_000_000_000), 5)
        mp = dict(zip(flat, new))
        q = {
            "rows": [[mp[v] for v in row] for row in b["rows"]],
            "desired_completion_index": b["desired_completion_index"],
            "hidden_word_indices": b["hidden_word_indices"],
        }
        out.append(q)
    return out

def exact_parsed_signature(x):
    return (x["t12"], x["t23"], x["t34"], x["t4d"], x["h"], x["h_rev"], x["w"])

def negative_outcomes(parsed_test):
    arr = [x["t4d"] for x in parsed_test]
    rng = random.Random(seed("NEG"))
    rng.shuffle(arr)
    return arr

def gate(split_eval):
    return (
        split_eval["operation_accuracy"] >= 0.98
        and split_eval["invariant_accuracy_all_blocks"] >= 0.98
        and split_eval["operation_invariant_agreement"] >= 0.98
        and split_eval["invariant_identifiable_fraction"] >= 0.98
    )

def main():
    dev = generate_split(N_DEV, "DEV")
    val = generate_split(N_VAL, "VAL")
    test = generate_split(N_TEST, "TEST")

    pd = [parse_block(x) for x in dev]
    pv = [parse_block(x) for x in val]
    pt = [parse_block(x) for x in test]

    primitives, primitive_counts = discover_primitives(pd)
    lookup, votes, conflicts = train_operation_lookup(pd)
    kstar, inv_support = select_invariant(pd)

    val_eval = evaluate(pv, lookup, primitives, kstar)
    test_eval = evaluate(pt, lookup, primitives, kstar)

    # Representation relabeling control.
    val2 = [parse_block(x) for x in relabel_blocks(val, "RELABEL_VAL")]
    test2 = [parse_block(x) for x in relabel_blocks(test, "RELABEL_TEST")]
    operator_mismatch = sum(
        exact_parsed_signature(a) != exact_parsed_signature(b)
        for a, b in zip(pv, val2)
    ) + sum(
        exact_parsed_signature(a) != exact_parsed_signature(b)
        for a, b in zip(pt, test2)
    )
    val2_eval = evaluate(val2, lookup, primitives, kstar)
    test2_eval = evaluate(test2, lookup, primitives, kstar)
    prediction_mismatch = int(val2_eval != val_eval) + int(test2_eval != test_eval)

    # Order destruction.
    reversed_test = evaluate(pt, lookup, primitives, kstar, use_reversed=True)
    order_gap = test_eval["operation_accuracy"] - reversed_test["operation_accuracy"]

    # Matched no-grammar negative.
    neg_truth = negative_outcomes(pt)
    neg_eval = evaluate(pt, lookup, primitives, kstar, outcome_override=neg_truth)

    primitive_set_true = set(TRUE_G)
    discovered_set = set(primitives)
    primitive_recovery_exact = discovered_set == primitive_set_true

    bits_per_completion = math.ceil(math.log2(max(2, len(primitives))))
    lookup_bits = len(lookup) * bits_per_completion

    val_pass = gate(val_eval)
    test_pass = gate(test_eval)
    representation_pass = operator_mismatch == 0 and prediction_mismatch == 0
    order_pass = order_gap >= 0.20
    negative_pass = (
        neg_eval["operation_accuracy"] <= 0.45
        and neg_eval["invariant_accuracy_all_blocks"] <= 0.45
    )

    status = "CONTROL_PASS" if all([
        primitive_recovery_exact,
        val_pass,
        test_pass,
        representation_pass,
        order_pass,
        negative_pass,
    ]) else "CONTROL_FAIL"

    out = {
        "experiment": EXPERIMENT,
        "status": status,
        "evidence_class": "architectural/methodological synthetic control",
        "eureka_status": "NONE",
        "seeds": {
            "DEV": seed("DEV"), "VAL": seed("VAL"), "TEST": seed("TEST"),
            "NEG": seed("NEG"),
        },
        "counts": {"DEV": N_DEV, "VAL": N_VAL, "TEST": N_TEST},
        "true_generators": [list(x) for x in TRUE_G],
        "discovered_primitives": [list(x) for x in primitives],
        "primitive_recovery_exact": primitive_recovery_exact,
        "distinct_primitive_signatures": len(primitives),
        "distinct_h_states_dev": len(lookup),
        "h_states_with_conflicting_completion_labels": conflicts,
        "lookup_description_bits": lookup_bits,
        "invariant_candidates": [0,1,2,3,4],
        "selected_invariant_k": kstar,
        "invariant_dev_support": inv_support,
        "VAL": val_eval,
        "TEST": test_eval,
        "representation_control": {
            "operator_mismatch_count": operator_mismatch,
            "prediction_summary_mismatch_count": prediction_mismatch,
            "pass": representation_pass,
        },
        "order_control": {
            "true_order_operation_accuracy": test_eval["operation_accuracy"],
            "reversed_order_operation_accuracy": reversed_test["operation_accuracy"],
            "accuracy_gap": order_gap,
            "required_gap": 0.20,
            "pass": order_pass,
        },
        "matched_no_grammar_negative": {
            **neg_eval,
            "max_allowed_operation_accuracy": 0.45,
            "max_allowed_invariant_accuracy": 0.45,
            "pass": negative_pass,
        },
        "gates": {
            "VAL_positive": val_pass,
            "TEST_positive": test_pass,
            "representation": representation_pass,
            "order": order_pass,
            "matched_negative": negative_pass,
        },
        "claim_boundary":
            "Synthetic qualification only. PASS validates decompiler discrimination on a known hidden grammar; it is not evidence that Powerball or reality has this grammar.",
    }

    Path("RCX_PB_GRAMMAR_0001_SYNTHETIC_RESULT_v1.0.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(out, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
