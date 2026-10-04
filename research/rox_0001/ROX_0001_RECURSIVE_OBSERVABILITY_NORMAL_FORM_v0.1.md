# ROX-0001 — Recursive Observability Normal Form v0.1

**Date:** 2026-10-04  
**ROH class:** ROH-BRIDGE + ROH-CONTROL  
**Status:** FORMAL CANDIDATE / NOT YET A UNIVERSAL LAW  
**EUREKA status:** NONE

## 1. Purpose

This file defines the first domain-agnostic normal form to be tested across LIFE-CODE, Reality-Code / Reality-Decompiler, ENERGY-CODE, Gravity-Code, Observer-Code, Unified-Code, Resonance-Code, Balance-Code, and later blind targets.

It is not inferred from Powerball.

Powerball is explicitly excluded from fitting this normal form.

## 2. Typed state

A candidate system is represented by:

- `X_t`: latent or maximally resolved physical/system state;
- `Q_t`: observer/measurement quotient map;
- `Z_t = Q_t(X_t)`: observable equivalence-class state;
- `G_t`: admissible transformation/operator at step t;
- `R_t`: retained record/ledger available to later updates;
- `M_t`: model state, when present, representing predictive structure including possible information about Q/G/R;
- `I`: invariant/stabilizer family constraining admissible transformations.

## 3. Minimal update equations

The candidate normal form is:

`Z_t = Q_t(X_t)`

`R_{t+1} = U_R(R_t, Z_t)`

`G_t = U_G(Z_t, R_t, M_t)`

`X_{t+1} = G_t(X_t)`

`Q_{t+1} = U_Q(Q_t, R_{t+1}, M_t)`

`M_{t+1} = U_M(M_t, Z_t, R_{t+1}, Q_{t+1})`

Any component may be absent in a lower-order system.

The equations are structural, not claims that every domain literally uses discrete time or deterministic maps. Stochastic kernels and continuous-time analogues are allowed if they preserve the dependency graph.

## 4. Five nested architecture classes

### N0 — Observable dynamics
Only `Z_t -> Z_{t+1}` is identifiable.

### N1 — Quotient transformation
A deeper state / equivalence structure and induced transformation are identifiable:

`Q o G = Phi_G o Q`.

### N2 — Closure grammar
Operation/composition structure and invariant/stabilizer structure mutually constrain one another.

### N3 — Record-coupled observation
A retained record `R_t` changes later admissible transformations and/or the observer quotient.

### N4 — Recursive observer
A model state `M_t` contains information about the observer/model relation itself and prospectively changes later observation/transformation beyond a capacity-matched non-reflexive control.

The universal Recursive Observability Hypothesis specifically requires evidence beyond N2. N1/N2 alone are not self-observation.

## 5. Composition and order

For composable operators A,B:

- composition relation `C(A,B)=AB`;
- order-sensitive structure exists when `AB` and `BA` are operationally distinguishable;
- commutator/holonomy signatures are representation-independent only when preserved under the allowed equivalence/conjugacy map.

A domain may be commutative; noncommutativity is not mandatory.

The meta-grammar predicts when order is relevant, not that order must always matter.

## 6. Dual reconstruction condition

A candidate N2+ architecture must satisfy both:

### Operation channel
Recover `G_O` from interventions, transitions, compositions, or equivalent operational data.

### Invariant channel
Recover `G_I` from independently inferred invariants/stabilizers/closure constraints.

Require:

`d(G_O,G_I) <= epsilon_G`

and

`d(I(G_O), I_data) <= epsilon_I`.

A predictive model without dual closure remains N0/N1 evidence only.

## 7. Quotient / identifiability condition

Two hidden realizations are equivalent when every authorized future probe gives the same outcome distribution.

The decompiler must report:
- unique hidden realization;
- equivalence class/orbit only;
- or unidentifiable.

It may not invent a concrete hidden state when only an orbit is identified.

## 8. Ledger condition

A ledger `R` is legitimate only when:
- direct closure fails;
- adding one prospectively measured/inferred low-complexity state restores held-out closure;
- the update rule is frozen before held-out evaluation;
- the ledger is not a disguised domain/date/label identifier;
- complexity savings exceed the ledger description cost.

## 9. Recursive-observer condition

N4 requires a prospective second-order comparison.

Compare:

`H0: P(Z_{t+1}|history, Z_t, R_t)`

against

`H1: P(Z_{t+1}|history, Z_t, R_t, M_t)`

where `M_t` is itself a frozen model/summary of the observer/model relation, not merely another raw-history feature.

N4 support requires:
- H1 improves held-out predictive codelength after complexity penalty;
- the gain survives model-of-model destruction controls;
- raw-history capacity-matched H0 cannot reproduce the gain;
- the effect transfers to a second unrelated natural domain under the same abstract relation.

## 10. Cross-domain mapping

A domain adapter may map local variables into the typed signature, but the mapping must be:
- frozen before held-out target scoring;
- invariant to semantic relabeling;
- minimal under description length;
- nontrivial relative to a target-only learner.

The source grammar cannot use domain names as features.

## 11. Meta-grammar candidate

The first candidate cross-domain grammar is the dependency/closure structure:

`Q -> Z`
`(Z,R,M) -> G`
`G -> X'`
`(R,Z) -> R'`
`(Q,R',M) -> Q'`
`(M,Z,R',Q') -> M'`

with independent invariant constraints on G/composition.

This graph is the object to falsify or support.

No stronger ontology is assumed.

## 12. Powerball boundary

Powerball cannot contribute to fitting this normal form.

Only after the meta-grammar survives leave-one-domain-out tests on non-Powerball domains may a frozen adapter map Powerball pre-draw structure into the normal form.

Exact numbers additionally require a prospectively identifiable symmetry-breaking compiler from quotient state to concrete labels.

## 13. Evidence ladder

- formal coherence of this normal form: R0 candidate;
- synthetic discrimination: required R1;
- real-domain held-out recovery: R2;
- unrelated-domain replication: R3;
- nontrivial source-to-target transfer: R4;
- prospective second-order observer-state gain: R5;
- universal-candidate review: R6.

No stage may be skipped.

## 14. Current status

This file defines the candidate architecture only.

It creates no EUREKA and does not establish that nature uses this normal form.

Cross-project EUREKA tally remains 3.
