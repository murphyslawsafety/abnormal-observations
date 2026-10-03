# RCX-PB-GC-0004 — Observability Boundary + Regime-Conditioned Operator Test

**Version:** 0.1 DESIGN CANDIDATE  
**Date:** 2026-10-03  
**Status:** NOT FROZEN / NOT EXECUTED  
**Purpose:** successor direction after RCX-PB-GC-0003 global layered representations failed strict rolling-origin gates.

## 1. Why this experiment is different

RCX-PB-GC-0003 established two important negatives:

1. global object / quotient / grammar operation channels were all below fair baseline over 1,213 strict rolling-origin targets;
2. same-day anonymous quotient structure leaves a median candidate equivalence class of about 50 objects.

That creates two distinct possibilities that should not be mixed:

- **missing observability:** the public pretest record does not contain enough information to discriminate the later exact physical objects;
- **wrong conditioning:** predictive structure exists only inside apparatus / ball-set regimes or ordered machine-state transitions and is erased by global pooling.

RCX-PB-GC-0004 is designed to distinguish those possibilities before spending compute on another full predictive search.

## 2. Gate A — observability boundary

Question:

Does the public historical record contain reproducible information about which physical objects will be selected beyond the fair baseline after conditioning on all currently authorized causal observables?

Authorized observables:
- physical object identity within ball set;
- four ordered pretests;
- extraction positions;
- machine IDs;
- white and Powerball set IDs;
- past-only 1/4/16/64 object history;
- ordered transition matrices between consecutive pretests;
- regime age / number of prior uses;
- source-order gaps and regime changes.

Forbidden:
- arithmetic on printed labels;
- future observations;
- jackpot size, human ticket behavior, or post-draw variables.

Gate A is an **information / discriminability test**, not a ticket generator.

It should compare:
- correct pretest-to-draw pairing;
- regime-matched draw reassignment;
- within-set identity destruction;
- pretest-order destruction;
- fair simulated draws.

If no reproducible conditional information survives matched nulls, STOP. Do not build a live predictor from this public record.

## 3. Gate B — regime-conditioned operator grammar

Only if Gate A detects surviving information.

Instead of one global grammar, fit a hierarchy:

- G0: global operator;
- G1: machine-pair conditioned;
- G2: white-set / Powerball-set conditioned;
- G3: full machine + set regime;
- G4: within-regime latent-state operator inferred from the ordered four-pretest transition word.

All local operators shrink toward their parent operator with a fixed predeclared shrinkage rule. No regime is allowed a free unconstrained fit.

The primary question is whether conditioning reduces held-out rolling-origin log loss **and** transfers correctly to later uses of the same apparatus state.

## 4. Ordered operator representation

For each pair of rows A->B, construct a 5x5 partial physical-object transition matrix:

`M_AB[i,j]=1` when the same physical object appears at position i in A and position j in B, else 0.

From the ordered pretests construct:
- M12;
- M23;
- M34;
- compositions M12*M23 and M23*M34;
- three-step composition M12*M23*M34;
- direct overlap operators M13, M24, M14;
- composition residuals such as ||M12*M23-M13||_F;
- position-displacement statistics for surviving objects;
- order-reversal controls.

These are physical-position relations. They do not use printed-label arithmetic.

A candidate draw creates M4D and a completed operator word. The candidate is scored by how well M4D completes the past-learned regime-conditioned operator grammar.

## 5. Noncommutative / order-sensitive diagnostic

Motivated by the broader project's order-sensitive transformation work, test whether:

`Score(M12,M23,M34) != Score(M34,M23,M12)`

under the correct physical sequence.

Order sensitivity is evidence only if:
- correct-order performance exceeds reversed-order performance prospectively in historical walk-forward;
- the same effect does not appear under matched nulls;
- it replicates across more than one apparatus/set regime.

This is a methodological bridge only. ENERGY-CODE / geometric-pumping results are not evidence that Powerball must contain such structure.

## 6. Compute discipline

No cloud-heavy null campaign until Gate A survives a cheap actual-history screen.

Proposed ladder:
1. local / low-cost exact historical corpus qualification;
2. Gate A actual-history walk-forward;
3. 99-replicate matched-null screen only if Gate A is positive;
4. Gate B regime-conditioned operator race only if Gate A survives;
5. 999-replicate full-pipeline nulls only if Gate B passes all raw gates;
6. live experiment only after a separate freeze.

## 7. Claim boundary

A PASS would not prove a universal Reality-Code.

It would establish only that the public physical lottery record contains reproducible conditional information, and possibly that this information is apparatus/regime/order dependent.

A FAIL at Gate A would be especially informative: it would indicate that continued exact-number prediction from the currently available public observables is not scientifically justified, and that deeper prediction would require genuinely new physical measurements rather than more algebra on the same record.

## 8. Current state

DESIGN CANDIDATE ONLY.

Do not execute until:
- Gate-A statistic;
- exact representation;
- nulls;
- sample-size rules;
- shrinkage rule;
- thresholds;
- multiplicity correction;
- code;
- SHA freeze

are fully specified.
