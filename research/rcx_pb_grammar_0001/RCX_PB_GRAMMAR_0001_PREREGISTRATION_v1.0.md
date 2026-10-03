# RCX-PB-GRAMMAR-0001 — Anonymous Transformation-Grammar Decompiler

**Version:** 1.0  
**Freeze date:** 2026-10-03  
**ROH class:** ROH-PROBE + ROH-CONTROL  
**Status:** PREREGISTERED / SYNTHETIC QUALIFICATION REQUIRED BEFORE HISTORICAL POWERBALL SCORING  
**EUREKA status:** NONE

## 0. Governing directive

This experiment is governed by:
`research/unified/RECURSIVE_OBSERVABILITY_CROSS_PROJECT_DIRECTIVE_v1.0_2026-10-03.md`.

The experiment tests grammar before rendered values.

It does not assume that Powerball is predictable, that the Recursive Observability Hypothesis is true, or that an observer is conscious.

## 1. Scientific question

Can a label-invariant decompiler recover a low-complexity, order-sensitive transformation grammar and its independently testable invariant closure from anonymous event relations, then transfer that grammar to held-out compositions before exact rendered labels are scored?

The Powerball history is not opened for this experiment's grammar scoring until the synthetic qualification below passes.

## 2. Canonical event representation

A five-row block is:

`P1 -> P2 -> P3 -> P4 -> D`.

For a pair of rows A,B containing five unique object identities, define the canonical position operator `T_AB` as the partial map from source extraction position to destination extraction position for identities appearing in both rows.

For the synthetic qualification all five identities survive, so `T_AB` is a full permutation on five positions.

For real Powerball, partial maps and novelty symbols are allowed; they are handled only after synthetic qualification.

Printed numerical magnitude is never used.

## 3. Composition convention

A permutation p is represented as a tuple where `p[i]` is the destination of source position i.

Composition `p o q` means p after q:

`(p o q)[i] = p[q[i]]`.

For the pretest word:

`H = T34 o T23 o T12`.

The held-out completion is `T4D`.

The completed word is:

`W = T4D o H`.

## 4. Frozen synthetic positive-control grammar

Primitive generator alphabet:

`A = (3,2,1,0,4)`

`B = (3,4,2,0,1)`

`C = (3,4,2,1,0)`

These generators are not all commuting.

For every length-three word over {A,B,C}, define:

`H = g3 o g2 o g1`.

The correct completion is the unique generator `g4 in {A,B,C}` satisfying:

`(g4 o H)[0] = 1`.

This unique-completion property has been verified symbolically before generation.

The invariant family available to the independent closure channel is frozen as:

`K_k(W) := W[0] = k`, for k in {0,1,2,3,4}.

The invariant channel may select k from DEV only by maximum completed-word support, then must remain frozen.

## 5. Synthetic rendering

Each block begins with five anonymous hidden tokens.

For every block:
- choose a length-three primitive word;
- apply g1,g2,g3 and the true completion g4;
- independently relabel the five hidden tokens with five unique random integers drawn from 1..10^9;
- emit only the five rendered rows.

The decompiler receives no generator labels, hidden-token names, or invariant truth.

The random integer magnitude has no scientific meaning.

## 6. Balanced generation

Completion classes A/B/C are sampled uniformly.

For each desired completion class, select uniformly among the length-three words whose true completion equals that class.

Frozen counts:
- DEV = 3,000 blocks;
- VAL = 1,000 blocks;
- TEST = 1,000 blocks.

Seeds:
- DEV: SHA-derived seed from `RCX-PB-GRAMMAR-0001|DEV`;
- VAL: SHA-derived seed from `...|VAL`;
- TEST: SHA-derived seed from `...|TEST`;
- NEGATIVE: SHA-derived seed from `...|NEG`.

## 7. Operation channel

The decompiler:
1. reconstructs T12,T23,T34,T4D from equality relations in rendered rows;
2. discovers the primitive alphabet from DEV signatures;
3. computes H from the observed ordered pretest operators;
4. learns a DEV lookup `H -> T4D` using majority class with deterministic lexicographic tie-break;
5. freezes it;
6. scores VAL and TEST.

No generator truth labels are supplied.

## 8. Independent invariant channel

Using DEV completed words only:
1. evaluate each frozen candidate invariant K_k for k=0..4;
2. select the k with greatest support;
3. freeze k*;
4. for a held-out H, evaluate each discovered candidate completion g by whether `K_k*(g o H)` holds;
5. if exactly one candidate satisfies it, predict that candidate;
6. otherwise mark UNIDENTIFIABLE for that block.

The invariant channel does not use the operation-channel H->completion lookup.

## 9. Dual reconstruction checksum

For VAL and TEST report:
- operation-channel completion accuracy;
- invariant-channel identifiable fraction;
- invariant-channel accuracy among all blocks, treating UNIDENTIFIABLE as wrong;
- operation/invariant prediction agreement.

A synthetic positive-control PASS requires on both VAL and TEST:
- operation accuracy >= 0.98;
- invariant accuracy >= 0.98;
- agreement >= 0.98;
- invariant identifiable fraction >= 0.98.

## 10. Representation control

Apply a second independent bijective relabeling to every rendered block.

Reconstructed operator signatures and every VAL/TEST prediction must be exactly unchanged.

Required:
- operator mismatch count = 0;
- prediction mismatch count = 0.

## 11. Order-destruction control

Without refitting the frozen operation lookup, replace each held-out composition key by the reversed-order composition:

`H_rev = T12 o T23 o T34`.

Report reversed-order completion accuracy.

PASS requires on TEST:

`accuracy_true_order - accuracy_reversed_order >= 0.20`.

This confirms that successful recovery is not reducible to the unordered primitive multiset.

## 12. Matched no-grammar negative

Construct a matched negative TEST set by permuting the true T4D completions among TEST blocks with the frozen NEGATIVE seed.

This preserves:
- TEST pretest words;
- completion-class marginal counts;
- rendered-label process.

It destroys the pretest-word -> completion dependence.

Run the frozen operation and invariant channels without refit.

Required:
- operation negative accuracy <= 0.45;
- invariant negative accuracy <= 0.45;
- dual agreement on the negative cannot be interpreted as positive if both are wrong.

If the negative exceeds 0.45, the synthetic qualification fails as insufficiently discriminating.

## 13. MDL / identifiability record

Report:
- number of distinct primitive signatures;
- number of distinct H states in DEV;
- number of H states with conflicting completion labels;
- lookup description length in bits under a fixed enumerative code;
- number of invariant candidates;
- selected invariant;
- held-out H states unseen in DEV;
- number of blocks UNIDENTIFIABLE by the invariant channel.

No unique-hidden-realization claim is allowed beyond these diagnostics.

## 14. Synthetic qualification outcome

### CONTROL_PASS
All positive, representation, order, and matched-negative gates pass on VAL and TEST.

### CONTROL_FAIL
Any required gate fails.

A CONTROL_PASS is methodological calibration only. It cannot create an EUREKA and cannot count as evidence that Powerball has such a grammar.

## 15. Historical Powerball authorization

Historical Powerball Stage H is authorized only after CONTROL_PASS.

Stage H will:
- canonicalize real four-pretest words into partial operators / novelty relations;
- infer quotient classes from behavior, not machine/set labels;
- derive operation and invariant channels independently;
- test held-out T4D operator-class prediction before any exact-number checksum;
- compare against target-only, order-destroyed, word-recombined, quotient-preserving, invariant-preserving, and fair-compiler controls.

The exact Stage-H candidate family, MDL penalty, quotient threshold, split, and PASS gates must be frozen in a separate Stage-H amendment before scoring real Powerball outcomes.

## 16. Claim boundary

A synthetic CONTROL_PASS proves only that the proposed decompiler can recover this known hidden grammar through arbitrary rendered labels and reject a matched no-grammar control.

A later historical PASS would support only a recovered anonymous transformation grammar in this lottery record.

Neither result alone proves:
- universal Recursive Observability;
- consciousness-dependent physics;
- determinism;
- Powerball exploitability;
- a universal substrate law.

EUREKA tally remains 3 unless a separately qualifying result is earned.
