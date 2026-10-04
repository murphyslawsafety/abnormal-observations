# ROX-0001 — Prior-Art Reconciliation and Level Correction v0.1

**Date:** 2026-10-04  
**Status:** ARCHITECTURE CORRECTION / NOT A RESULT  
**EUREKA status:** NONE

## 1. Why another correction is required

ROX-0001A showed that a naive nested predictor of raw record-state and model-state channels is not a reliable detector of recursive observation.

More importantly, external prior art shows that the lower layer we had begun calling "observer state" is already a mature mathematical object.

Computational mechanics defines **causal states** as equivalence classes of past histories that induce the same conditional distribution over futures. Those states are minimal sufficient statistics for prediction.

Predictive-state representations similarly define state in terms of predictions of future observable tests rather than hidden coordinates.

Therefore the project must not claim novelty for:
- grouping histories by future predictive equivalence;
- minimal predictive-state recovery;
- observable-state representations defined by future tests.

Those are established frameworks and should be used as foundations/controls.

## 2. Corrected ROH-specific target

The unresolved target is one level higher:

> Does the system's inferred model of its own predictive/observational state prospectively change the **observation map, measurement policy, intervention policy, or admissible transformation** itself?

Call:
- `S_t` = first-order causal/predictive state;
- `A_t` = observation/measurement action or map selected at t;
- `U_t` = uncertainty/model-quality variable derived from the system's own predictive model.

Ordinary predictive-state dynamics:
`S_t -> future observations`.

Recursive-observer dynamics require a loop such as:
`S_t -> U_t -> A_{t+1} -> observation_{t+1} -> S_{t+1}`.

The observer's own model therefore changes what is observed next.

This is not equivalent to memory alone.

## 3. Relation to active inference / epistemic action

Active-inference frameworks already formalize agents that select actions/policies partly according to expected information gain or uncertainty reduction.

ROX must therefore distinguish:
- recovery of a known active-sensing architecture;
- from any stronger claim of a universal substrate-level recursive-observation law.

A successful ROX experiment in an adaptive agent would initially be a known-family recovery unless the cross-domain transfer itself adds genuinely new structure.

## 4. New proof object

The next decompiler should reconstruct a **closed observer loop**:

`history -> predictive state -> model uncertainty -> observation/action policy -> new observation -> updated predictive state`.

The falsifiable object is the loop topology and its transfer, not a scalar "recursion score".

## 5. Required matched control

For every candidate recursive observer, compare with a process that has:
- identical observation marginals;
- identical action/measurement marginals;
- matched first-order predictive-state complexity;
- but observation/action choices are decoupled from model uncertainty or self-model state.

A recursive claim requires prospective advantage over this matched non-reflexive control.

## 6. Powerball consequence

Powerball does not obviously contain an adaptive observation policy at the public-record level.

Therefore Powerball should not be used to prove the specifically recursive ROH layer.

It may still serve later as a hostile blind checksum for a cross-domain grammar, but only after that grammar is earned elsewhere.

Trying to force N4 recursion directly out of Powerball would be another representation error.

## 7. Updated target hierarchy

1. Use established causal-state / predictive-state mathematics for Q/R.
2. Recover transformation/composition and invariant closure as before.
3. Test whether inferred uncertainty/model state changes the observation/intervention map.
4. Require source-to-target transfer of that closed loop.
5. Only then revisit Powerball as an external blind compiler/checksum problem.

EUREKA tally remains 3.
