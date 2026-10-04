# RCX-PB-ROH-0001 — Recursive Observer-State / Gauge-Compiler Test

**Version:** 0.1 DESIGN CANDIDATE  
**Date:** 2026-10-04  
**ROH class:** ROH-PROBE + ROH-BRIDGE  
**Status:** NOT FROZEN / NO DRAW SCORING AUTHORIZED  
**EUREKA status:** NONE

## 0. Why the level changes again

RCX-PB-GRAMMAR-0001 still treated the anonymous partition produced by four pretests as the state and the draw as a fifth partition extension.

That is one level too low for the cross-project Recursive Observability hypothesis.

The deeper object is not the partition itself. It is the **observer-generated record that creates and updates the partition**, and the symmetry-breaking compiler that maps an abstract observer state back to concrete labeled objects.

The Powerball number labels are gauge-like coordinates. A label-invariant grammar can constrain abstract equivalence classes, but cannot legitimately single out one exact label while all labels remain symmetry-equivalent.

Therefore exact-number prediction requires a second structure:

> a prospectively recoverable observer-state / record process that breaks label symmetry without using label magnitude.

This experiment asks whether that structure exists in the observation history itself.

## 1. Core ontology

Let:
- `B` = abstract anonymous observer state;
- `Y` = concrete labeled realization;
- `G=S_69 x S_26` = arbitrary within-channel relabeling group;
- `q:Y->B` = quotient map removing arbitrary labels;
- `R_t` = retained observation record up to time t;
- `C_t` = predictive observer-state / causal-state class inferred from R_t.

A substrate-level grammar acts on B.

An exact-number compiler additionally needs a symmetry-breaking map from the abstract state into a concrete fiber of labelings.

The candidate mechanism is not weight/weather/machine metadata. It is:

`past observation record -> predictive equivalence class -> next observation -> updated record`.

That is the literal testable form of "observation observing itself" available in this dataset.

## 2. Observation alphabet

For every physical white-ball identity and every completed event row, encode only how that identity was observed:

- `0` = not selected in the row;
- `P1..P5` = selected at extraction position 1..5.

For Powerball:
- `0` = not selected;
- `P` = selected.

Printed label magnitude is never used.

Machine/set/weather/weight are excluded from discovery.

The same physical identity across historical rows is used only as a persistent coordinate so that its own observation record can be followed through time.

## 3. Record state

For object b before target event t, define its past record:

`R_t(b) = (..., o_{t-3}(b), o_{t-2}(b), o_{t-1}(b))`.

The raw record is not itself the model.

Two past records are equivalent when they imply statistically indistinguishable distributions over future observation words under a frozen predictive-equivalence test.

This creates causal/predictive states:

`R ~ R' iff P(Future | R) approximately equals P(Future | R')`.

The decompiler must infer these states from training history.

## 4. Observer-state hierarchy

Exactly four memory scales are tested:

- C1: previous observation only;
- C2: previous 4 observations;
- C3: previous 16 observations;
- C4: previous 64 observations.

At each scale, histories are first represented anonymously by:
- selection/nonselection;
- extraction-position category;
- run length since last observation;
- observation count in the window;
- ordered recurrence pattern.

No printed-number arithmetic is allowed.

The experiment searches for the coarsest predictive partition of these histories that preserves held-out future distributions.

## 5. Gauge / symmetry-breaking question

At any target event, many physical labels may be equivalent under the current anonymous within-day state.

A valid exact-label compiler exists only if past observer-state C_t splits those otherwise anonymous labels into prospectively different future-observation distributions.

Primary gauge-breaking statistic:

`I_label = held-out log-likelihood gain from C_t within an anonymous role class`.

This is evaluated only among labels that are otherwise identical under the current anonymous pretest partition.

If `I_label <= 0`, the observer record has not broken the label symmetry and no exact-number compiler is justified.

## 6. Source-domain learning before draw transfer

The model is learned first from **pretest-to-pretest observation transitions only**.

Within each date, use:
- P1 -> P2;
- P1,P2 -> P3;
- P1,P2,P3 -> P4

as source-domain transitions.

Official draw rows are not used for representation selection or source-state discovery.

The source task asks:

> does past observation record + current anonymous state predict the next pretest observation better than a fair without-replacement observer?

Only a source model that survives historical held-out pretest transitions may be frozen for transfer to the official draw.

## 7. Source-domain controls

Required before any draw scoring:

1. arbitrary within-set relabeling invariance;
2. history destruction: permute each object's past observation record while preserving current anonymous pretest state;
3. time reversal of the observer record;
4. memory-depth destruction;
5. fair without-replacement compiler;
6. target-only sufficiency control.

A candidate source state must beat all applicable controls under held-out dates.

## 8. Nontrivial source-to-draw transfer

Only after source qualification:

- freeze predictive-state partition;
- freeze transition kernel;
- freeze compiler;
- then score historical draw rows in strict rolling origin.

No draw outcome may alter the state partition or kernel.

The transfer question is:

> does a predictive state inferred entirely from the observer's own earlier observation process reduce uncertainty in the later official draw?

This is the Resonance/Unified nontrivial-transfer requirement applied to observer state.

## 9. Exact-label compiler

For a target draw position:

1. compute the current anonymous within-day role for every remaining object;
2. group objects that are indistinguishable under that anonymous role;
3. within each group, use frozen predictive observer-state C_t to assign relative hazards;
4. normalize over all remaining objects;
5. score the official selected object.

The anonymous grammar and observer-state compiler are therefore separate layers:

`abstract role grammar x observer-record state -> concrete label probability`.

If the observer-state layer supplies no held-out within-role gain, exact labels remain UNIDENTIFIABLE.

## 10. Dual reconstruction

A predictive observer state is not accepted from likelihood alone.

Independent invariant channel:
- construct transition matrices among inferred causal states;
- derive stationary/state-flow invariants, recurrent-class structure, and predictive-equivalence stabilizers;
- reconstruct admissible state merges/splits from these invariants;
- require agreement with the prediction-derived partition.

Failure of mutual reconstruction rejects the observer-state interpretation.

## 11. Explicit recursive-observation gate

To count specifically as support for the ROH recursive layer, not merely memory:

A model using the observer's **own past prediction/state partition** must prospectively improve the next observation beyond a capacity-matched model using the same raw history but no state-of-state summary.

That is:

`Model(history, current state, previous inferred observer-state)`

must beat

`Model(history, current state)`

on held-out transitions under a frozen complexity penalty.

Without this second-order gain, the result is memory/feedback only, not "observation observing itself."

## 12. Outcome classes

### DIRECT_OBSERVER_STATE
Past observation record alone yields a stable predictive state and exact-label symmetry breaking.

### RECURSIVE_OBSERVER_STATE
Second-order observer-state feedback adds prospective information beyond raw-history control.

### ABSTRACT_ONLY
Anonymous grammar transfers, but label symmetry remains unbroken. Exact numbers are not identifiable.

### NO_OBSERVER_STATE
No stable predictive state beats fair/history-destroyed controls.

### UNIDENTIFIABLE
Multiple state partitions remain observationally equivalent.

## 13. Live-number boundary

No live Powerball line is authorized unless historical draw transfer demonstrates:

- positive source-domain qualification;
- positive within-role gauge-breaking gain;
- independent invariant reconstruction;
- matched null survival;
- strict historical rolling-origin exact-label likelihood improvement;
- a deterministic one-line compiler frozen before a future draw.

If those gates are met, a new live experiment ID will precommit exactly one line before the draw.

## 14. Why this is a deeper test

Previous branches asked what the balls, roles, or partitions were doing.

This branch asks:

> what state is created by the history of observation itself, and can that state alter/predict what becomes observable next?

That is the first Powerball architecture aimed directly at the Recursive Observability hypothesis rather than using it only as interpretation.

## 15. Immediate next step

Before freezing v1.0:
1. quantify pretest-only predictive-state identifiability;
2. measure gauge freedom within anonymous role classes;
3. test whether observer-history states reduce that freedom on held-out pretest transitions;
4. synthesize a positive recursive-observer control and a matched memory-only decoy;
5. freeze the exact state-merging criterion, complexity penalty, and source qualification threshold.

No official draw outcomes are to be used during those steps.

EUREKA tally remains 3.
