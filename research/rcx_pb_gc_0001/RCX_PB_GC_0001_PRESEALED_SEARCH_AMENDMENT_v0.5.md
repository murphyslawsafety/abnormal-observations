# RCX-PB-GC-0001 — Pre-Sealed Search Amendment v0.5

**Date frozen:** 2026-10-02  
**Status:** FROZEN BEFORE ANY MOMENT/LOW-RANK FAMILY EXECUTION.  
**Scope:** closes the remaining pre-sealed model-search space after the sparse GF(2) branch failed its frozen validation gate. It does not change the v0.1 scientific question, deterministic DEV/VAL/SEALED date assignment, source corpus, null families, FWER rule, sealed isolation, or claim boundary.

## 1. Validation-use boundary

The sparse GF(2) branch consumed the validation split only after its candidate set and selection rule were frozen. It failed validation and is permanently closed.

The validation split is therefore treated from this point onward strictly as a **model-selection layer**, as originally intended by v0.1, not as an independent confirmation layer. The untouched sealed-test split remains the first outcome layer capable of supporting an independent historical reconstruction claim.

No later claim may describe validation as independent confirmation.

## 2. No open-ended post-validation fishing

Exactly one remaining family is authorized after this amendment: the fixed moment / low-rank temporal-operator family below.

If this family produces no DEV candidate satisfying its frozen advancement rule, or if all DEV-advancing candidates fail validation, RCX-PB-GC-0001 model discovery ends with no surviving grammar. No additional model family, feature dictionary, neural learner, polynomial search, or hand-built rule may be added to this experiment after that failure.

Any later architecture requires a new experiment ID and a new untouched outcome era.

## 3. Object representation

Printed ball labels remain categorical object identifiers within physical ball sets. No arithmetic on printed label values is used.

For each candidate object and each physical pretest block, derive only incidence moments from the four ordered pretests.

White-ball per-block moment vector:
- C = total pretest occurrence count / 4
- T1 = sum of centered/scaled pretest coordinate t over occurrences / 4, with t = [-1, -1/3, +1/3, +1]
- P1 = sum of centered/scaled extraction-position coordinate p over occurrences / 4, with p = [-1, -1/2, 0, +1/2, +1]
- T2 = sum t^2 over occurrences / 4
- P2 = sum p^2 over occurrences / 4
- TP = sum t*p over occurrences / 4

Powerball per-block moment vector:
- C
- T1
- T2
using the same four pretest coordinates.

Previous/next block features are included only when the corresponding ball-set ID equals the current block's set ID. A declared source-unavailable scheduled date breaks adjacency.

## 4. Fixed temporal operator dictionary

For each base moment m with previous/current/next values (m-, m0, m+), define:

- R1 / DC: (m- + m0 + m+) / 3
- R2 adds slope: (m+ - m-) / 2
- R3 adds curvature: (m- - 2*m0 + m+) / 4

Temporal ranks searched: r in {1,2,3}.

Forward compilation uses the exact same fitted coefficients and operator definitions with m+ set to zero. Coefficients are never refit for forward scoring.

## 5. Fixed event-moment bases

Three nested bases are searched:

- B1: white {C}; PB {C}
- B3: white {C,T1,P1}; PB {C,T1}
- B6: white {C,T1,P1,T2,P2,TP}; PB {C,T1,T2}

Combined scalar parameter count k is:
- B1: 2*r
- B3: 5*r
- B6: 9*r

No intercept is needed in conditional-choice scoring because a common intercept cancels inside each risk set.

## 6. Fitting grid

For each (basis, temporal rank), fit separate white and PB conditional-logit coefficient vectors by penalized maximum likelihood on training draws.

L2 penalty grid:
lambda in {0.1, 1, 10, 100}.

The penalty is used only for coefficient estimation. Model selection remains governed by held-out log-score improvement and the frozen MDL complexity term.

No hyperparameter is changed after execution.

## 7. DEV evaluation

Use the same three chronological expanding-window DEV folds already frozen for the previous DEV scans:
- first 40% -> next 20%
- first 60% -> next 20%
- first 80% -> final 20%

For every candidate report:
- global held-out log-score improvement over the fair without-replacement baseline;
- forward held-out log-score improvement using the same global-fitted coefficients with future block features zeroed;
- each fold separately;
- MDL penalty 0.5*k*ln(N_DEV)/N_DEV.

DEV advancement requires all:
1. mean global raw improvement > 0;
2. mean global improvement minus MDL > 0;
3. mean forward raw improvement > 0;
4. all three global fold improvements > 0;
5. all three forward fold improvements > 0.

At most the three highest-scoring DEV candidates advance to validation, ordered by global score-minus-MDL, then forward raw improvement, then lower k, then lexical model ID.

## 8. Validation rule

Before validation execution, the exact advancing candidate IDs, basis/rank/lambda values, fitting code blob SHA, and validation runner blob SHA must be frozen in a new search manifest.

Fit each candidate once on all 878 DEV targets. Score on all 261 validation targets without refitting.

Validation advancement requires:
- validation global raw improvement minus 0.5*k*ln(261)/261 > 0; and
- validation forward raw improvement > 0.

If multiple pass, select by validation global score-minus-MDL, then forward raw improvement, then lower k, then lexical model ID.

If none pass, model discovery for RCX-PB-GC-0001 ends.

## 9. Full-pipeline null requirement

If and only if a candidate survives validation, every required v0.1 matched-null family must rerun the **entire historical search path**, including:
- causal-state DEV search/pruning;
- sparse GF(2) DEV search and global compilation;
- GF(2) validation selection/failure logic;
- this moment/low-rank DEV grid and validation selection.

The observed candidate may not be tested against nulls in isolation. This preserves the look-elsewhere correction for the adaptive pre-sealed search history.

## 10. Claim boundary

A DEV or validation success is not a Powerball predictability claim and is not an EUREKA. Sealed reconstruction, full-pipeline matched nulls, stability, hardware transfer, forward-only held-out performance, and independent future/live replication remain controlling gates.
