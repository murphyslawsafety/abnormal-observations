# RCX-PB-GC-0003 — Layered Quotient / Transformation-Grammar Walk-Forward Test

**Version:** 1.0  
**Freeze date:** 2026-10-03  
**Track:** Reality-Code / Powerball physical-checksum branch  
**Status:** PREREGISTRATION / ARCHITECTURE FROZEN / EXECUTION NOT YET LAUNCHED  
**EUREKA status:** NONE

## 0. Scientific role

RCX-PB-GC-0001 and RCX-PB-GC-0002 tested representations close to the observable layer. RCX-PB-GC-0001 closed with no surviving grammar. RCX-PB-GC-0002H subsequently evaluated the fixed RCX-PB-GC-0002 relational model against 273 previously untouched historical outcomes and failed its frozen historical-holdout gate (combined LLR = -1.1024497215 nats; e-value = 0.3320566402).

RCX-PB-GC-0003 does **not** repair either failed model.

Its purpose is to test a deeper representation hierarchy motivated by the mature Reality-Code methodology:

1. recover a generator / transformation description before asking for the compiled observable;
2. infer invariants independently and require agreement with the operation-derived grammar;
3. represent observational equivalence explicitly rather than assuming a unique hidden realization;
4. report prediction and identifiability separately;
5. treat exact observable outputs as a downstream checksum, not the discovery substrate.

LIFE-CODE motivates testing hierarchy / quotient structure rather than a flat exact-symbol dictionary, but no LIFE-CODE result is counted as evidence for Powerball. The bridge is methodological only.

## 1. Question

Does the physical Powerball pretest-to-draw process contain a low-complexity, relabeling-robust latent state / transformation grammar that:

- is recoverable from past physical blocks only;
- predicts later draws under strict rolling-origin simulation;
- is independently supported by an invariant / closure channel;
- survives hardware and ball-set regime changes;
- beats full-pipeline matched nulls after accounting for representation search?

If not, this experiment rejects the tested deeper representations without asserting that every conceivable hidden physical state is absent.

## 2. Observable and latent layers

The experiment treats the system as a compiler with distinct layers.

### L0 — rendered phenotype
Official ordered draw:
- five white printed labels;
- one Powerball printed label.

L0 is the final checksum. Arithmetic on printed labels is prohibited.

### L1 — physical object layer
Object identity:
- `(white_ball_set_id, printed_label)`;
- `(powerball_ball_set_id, printed_label)`.

Context:
- machine IDs;
- ball-set IDs;
- date;
- event sequence;
- extraction position;
- pretest/draw event type.

Printed labels are categorical object identifiers only.

### L2 — local quotient / role layer
For each same-day four-pretest block, each physical object is represented by its structural role under arbitrary within-set relabeling:
- four-row occurrence pattern;
- extraction-position incidence pattern;
- same-row co-occurrence relations;
- directed adjacency relations;
- recurrence / survival between ordered pretests.

Objects with identical structural roles belong to the same local equivalence class / orbit.

### L3 — temporal object-state layer
For a physical object that persists within the same set, its past-only state contains a fixed dyadic hierarchy of role history:
- immediately previous usable block;
- trailing 4 blocks;
- trailing 16 blocks;
- trailing 64 blocks.

Each scale is computed only from dates strictly earlier than the target. No future observations enter a target state.

The hierarchy is frozen at 1 / 4 / 16 / 64. It is not tuned after scoring.

### L4 — transformation-grammar layer
A daily block is a sequence of physical states. Candidate operations describe how object-role classes transform from:
- pretest 1 -> pretest 2;
- pretest 2 -> pretest 3;
- pretest 3 -> pretest 4;
- pretest 4 -> draw.

The grammar is learned from prior completed blocks only.

### L5 — invariant / closure layer
Independently from the operation fit, a completed five-row block is summarized by relabeling-invariant closure statistics:
- row-overlap cardinalities;
- recurrence multiplicity histogram;
- position-preserving overlap counts;
- directed adjacency survival counts;
- white-object unique-count trajectory;
- Powerball recurrence class;
- anonymous co-occurrence graph degree sequence;
- anonymous co-occurrence graph Laplacian spectrum through the first four nontrivial ordered eigenvalues, with missing dimensions zero-padded.

The invariant channel learns the past distribution / low-rank manifold of these summaries within eligible hardware regimes.

No numerical function of the printed labels is permitted.

## 3. Dual reconstruction requirement

Two channels are fit independently on the same past-only training history.

### Operation channel O
Estimate the conditional transition grammar from pretest states to the next row / draw state.

### Invariant channel I
Estimate how a candidate draw completes the current four-pretest block relative to the learned closure / invariant manifold.

For target date d, both channels produce normalized sequential conditional distributions over the remaining white objects and over the Powerball object.

The combined channel is the equal-weight geometric pool:

`log P_C = 0.5 log P_O + 0.5 log P_I - log Z`

at each sequential choice.

The 0.5 / 0.5 weights are frozen and never tuned.

A representation cannot advance on combined performance alone. Historical promotion requires:
- O cumulative LLR > 0;
- I cumulative LLR > 0;
- C cumulative LLR > 0.

This is the operational dual-reconstruction checksum.

## 4. Three frozen representation planes

The complete search contains exactly three planes.

### P1 — OBJECT
Uses L1 + L3 temporal physical-object state. No local quotient canonicalization.

### P2 — QUOTIENT
Uses L2 anonymous local role / orbit state and L5 invariants. Cross-date object identity is removed except for hardware/set regime membership.

### P3 — GRAMMAR
Uses L2 + L3 + L4 + L5 and the O/I dual-reconstruction rule.

No fourth plane, neural latent representation, label-arithmetic family, polynomial-on-label family, or post-hoc feature dictionary may be introduced under RCX-PB-GC-0003.

A new representation requires a new experiment ID.

## 5. Historical source

Authoritative source:
`https://cdn.powerball.com/v01/media/powerball-pre-test.pdf`

Current matrix:
- 5/69 white;
- 1/26 Powerball;
- matrix start 2015-10-07.

Use the qualified structural ingest rules inherited from RCX-PB-GC-0001 v0.4:
- four ordered Pre-test rows followed by one Draw;
- Post-test excluded;
- source anomalies retained and logged;
- no outcome imputation;
- declared source gap 2025-03-01 remains a hard observation gap.

Historical cutoff for RCX-PB-GC-0003:
**2026-09-30 inclusive.**

All historical outcomes are now considered development-grade for this experiment because the architecture was designed after prior Powerball experiments. No historical date is described as a pristine untouched confirmation set.

## 6. Strict rolling-origin simulator

A target draw is eligible only after at least 200 earlier usable completed draw blocks exist.

For each eligible historical target d:

1. training data = usable completed blocks with date < d only;
2. fit / update each frozen representation plane using only that past;
3. expose the four same-day pretests for d;
4. produce a normalized probability distribution for the ordered five-white draw and Powerball;
5. produce one deterministic model ticket from the combined distribution by sequential maximum conditional probability;
6. reveal the historical official draw;
7. record the score;
8. update the past-only state;
9. advance to the next date.

No observation dated >= d can affect the model used to score d.

The historical simulator is therefore a pseudo-prospective rolling-origin test, not a live prospective experiment.

## 7. Deterministic tie handling

A structural representation may assign equal probability to multiple physically distinct objects.

Ties are not broken by numeric label magnitude.

For scoring, equal candidates retain equal probability.

For the one-ticket simulator only, ties are resolved by deterministic SHA ordering:

`SHA256("RCX-PB-GC-0003|TIE|" + target_date + "|" + ball_set_id + "|" + categorical_object_id)`.

This rule is outcome-blind and frozen before execution.

Identifiability reports the number of tied / observationally equivalent exact tickets implied by the representation.

## 8. Primary score

For target d:

`LLR_d = log P_model(official ordered draw | past, current pretests) - log P_fair(official ordered draw)`.

Fair baseline:

`P_fair = 1 / [(69*68*67*66*65)*26]`.

For each O, I, and C channel report:
- cumulative LLR;
- mean LLR per target;
- log10 e-value equivalent;
- 30-target block LLRs;
- positive-target fraction;
- maximum single-target positive contribution;
- maximum single-target negative contribution.

The e-value interpretation is descriptive in the adaptive historical search stage; confirmatory significance comes from the full-pipeline null campaign.

## 9. Exact-ticket checksum metrics

The deterministic one-ticket simulation reports:
- number of exact 5+PB matches;
- 5-white matches;
- 4+PB;
- 4-white;
- 3+PB;
- 3-white;
- 2+PB;
- 1+PB;
- PB-only;
- distribution of number of white matches.

These are secondary checksum metrics. They cannot rescue a failed primary likelihood test.

No historical payout dollars are used as a model-selection metric.

## 10. Identifiability metrics

Every plane must report:
- effective rank / singular spectrum of its fitted state representation;
- condition number where defined;
- number of distinct latent states / equivalence classes;
- median and p90 size of candidate-object equivalence classes;
- median and p90 number of exact ordered tickets tied at maximum model probability;
- entropy reduction from fair baseline;
- stability of latent classes under 200 moving-block bootstrap resamples if the plane reaches Stage 2.

Excellent predictive fit with broad non-identifiability is not promoted as unique hidden-code recovery.

## 11. Hardware / set transfer

For every machine or ball-set transition with:
- at least 100 earlier usable targets before first appearance; and
- at least 20 usable targets after first appearance,

freeze the pretransition fitted grammar and score the first 20 posttransition targets without scientific refit.

Report these transfer targets separately.

A plane fails the transfer requirement if its mean combined LLR over eligible transfer targets is <= 0.

If no transition satisfies the sample requirements, the transfer gate is UNIDENTIFIABLE rather than PASS.

## 12. Representation robustness

Because the proposed deeper architecture is relational, these transformations should not alter scientific performance materially:

1. arbitrary bijective relabeling of white object labels within each ball set;
2. arbitrary bijective relabeling of Powerball labels within each set;
3. serialization/order changes that preserve declared event order and extraction positions.

For P2/P3, relabeling must reproduce target probabilities to numerical tolerance <= 1e-12.

P1 is allowed to track categorical object identity but cannot use numeric magnitude. Relabeling IDs consistently through history must leave its likelihood invariant to <= 1e-12.

Violation is an implementation / representation failure.

## 13. Wrong-grammar controls

For each surviving plane:
- use a grammar from a nonmatching hardware regime;
- reverse the four pretest event order while preserving within-row extraction positions;
- destroy within-row directed adjacency while preserving per-row object membership.

A proposed grammar must perform worse under these wrong-grammar controls than under the correct representation.

## 14. Matched full-pipeline nulls

Null generation preserves the historical hardware/date schedule and runs the **entire three-plane selection pipeline**, not only the final winner.

N1 — fair without-replacement white + fair Powerball draws.

N2 — draw chronology shuffled within comparable hardware / ball-set regimes.

N3 — draw-to-pretest reassignment within comparable regimes while preserving date and hardware marginals.

N4 — pretest event order destroyed within date.

N5 — within-set physical-object identities permuted independently between dates, destroying persistent object state while preserving same-date incidence.

N6 — outcome-only null preserving empirical marginal object frequencies within ball-set regimes but destroying pretest-to-draw coupling.

The observed statistic for multiplicity control is the maximum qualifying combined LLR per target across P1/P2/P3.

## 15. Compute-budget ladder

Cloud resources are deliberately gated.

### Stage 0 — qualification
No model race.
- reproduce source;
- verify cutoff;
- construct layered states;
- verify no future leakage;
- verify relabeling invariance;
- run fair-baseline unit tests.

If Stage 0 fails, stop.

### Stage 1 — actual-history walk-forward
Run exactly P1/P2/P3 on the real historical rolling-origin sequence.

A plane advances only if all are true:
- O cumulative LLR > 0;
- I cumulative LLR > 0;
- C cumulative LLR > 0;
- at least 60% of full nonoverlapping 30-target blocks have C LLR > 0;
- no one target contributes > 20% of all positive C LLR;
- eligible hardware/set transfer mean C LLR > 0, or transfer is formally UNIDENTIFIABLE;
- representation robustness passes.

If no plane advances: STOP RCX-PB-GC-0003. No null campaign.

### Stage 2 — cheap null screen
Only advancing planes participate.
Run 99 deterministic replicates for N1-N6 with the full selection pipeline.

If the empirical max-statistic p-value is > 0.05 for any required null family: STOP.

### Stage 3 — confirmatory null campaign
Only if Stage 2 survives:
run 999 deterministic replicates per N1-N6.

Per-family empirical p:
`p=(1+#null_stat>=observed_stat)/1000`.

Holm-Bonferroni across six families at familywise alpha = 0.01.

All six required null families must survive.

No 9,999-replicate campaign is authorized unless Stage 3 passes and a later live-readiness package independently justifies the added resolution.

## 16. Historical readiness gate for a live experiment

RCX-PB-GC-0003 does not itself authorize purchasing a ticket.

A later live experiment may be frozen only if:
1. a plane survives Stages 0-3;
2. O, I, and C each remain positive;
3. all six full-pipeline null families pass corrected alpha 0.01;
4. representation robustness passes;
5. identifiability is reported;
6. transfer is positive or explicitly UNIDENTIFIABLE rather than silently ignored;
7. one exact deterministic ticket-generation rule is frozen;
8. the complete historical pipeline, source, model, code, hashes, and failed candidates are preserved.

The live experiment must receive a new ID and use future draws that have not been used in any model selection.

## 17. EUREKA boundary

RCX-PB-GC-0003 historical success cannot create an EUREKA.

A live result would require its own preregistration and repeated independent prospective replication before any EUREKA review.

Even a successful live result would initially support only a reproducible predictive dependency in the observed apparatus/process. It would not by itself establish:
- a universal Reality-Code;
- determinism of all physical events;
- a simulation hypothesis;
- supernatural causation;
- a guaranteed lottery-winning method.

## 18. Failure interpretation

A failure of RCX-PB-GC-0003 falsifies the tested layered representations:
- categorical physical-object state;
- anonymous local quotient/orbit state;
- the frozen transformation grammar;
- the frozen invariant/closure dictionary;
- their fixed dual-reconstruction combination.

It does not falsify every conceivable deeper representation of reality.

## 19. Cross-project evidence boundary

Reality-Code, LIFE-CODE, Observer-Code, Unified-Code, ENERGY-CODE, and this Powerball line remain scientifically distinct.

The imported elements are methodological:
- generator-first decompilation;
- explicit quotient/equivalence classes;
- dual reconstruction from operations and invariants;
- hierarchy-aware representation;
- identifiability reporting;
- wrong-grammar / transfer controls.

No result from another project is counted as evidence that Powerball is predictable.
