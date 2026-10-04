# ROX-0004 — Explicit Confidence→Information-Seeking→Updated-Confidence Natural Loop

**Version:** 0.1 DESIGN CANDIDATE
**Date:** 2026-10-04
**ROH class:** ROH-PROBE + ROH-BRIDGE
**Status:** SOURCE-QUALIFICATION PHASE ONLY / NO NATURAL RESULT YET
**Parent control:** ROX-0002B CONTROL_PASS
**Prior natural result:** ROX-0003A FAIL
**EUREKA status:** NONE

## 0. Why this source is better matched

ROX-0003A used a task in which confidence was reported after the observation-stopping decision. The online model/confidence state therefore had to be inferred. Its simple preregistered mapping failed.

ROX-0004 moves to a paradigm with the temporal order required by the loop itself.

Preferred natural source:

Van Marcke & Desender (2025), "Context-dependent role of confidence in information-seeking", Cognition 263:106219, DOI 10.1016/j.cognition.2025.106219, public OSF project m5a4x.

The published test phase has the order:
1. initial perceptual decision;
2. explicit initial confidence;
3. choose whether to seek additional information / see the stimulus again;
4. if requested, receive a new perceptual sample;
5. final decision and final confidence.

This exposes an empirical loop closely aligned with:

`M_t -> A_t -> Z_{t+1} -> M_{t+1}`.

## 1. Scientific target

ROX-0004 does not ask merely whether low confidence correlates with information seeking.

It asks whether the same explicit pre-policy observer/model state participates in a closed held-out loop:

- E2: initial confidence/model state predicts information-seeking policy beyond objective-performance/task controls;
- E3: information-seeking policy determines whether new evidence is observed;
- E4: receiving the new evidence changes the subsequent confidence/model state relative to matched controls;
- closure: the intact three-edge factorization outperforms one-edge-broken decoys.

This is the first intended natural application of the topology calibrated by ROX-0002B.

## 2. Two-experiment structure

The source includes two preregistered experiments using different manipulations:
- Experiment 1: comparative-feedback manipulation of prior confidence beliefs;
- Experiment 2: training-difficulty manipulation.

ROX-0004 should treat them as separate natural environments.

Preferred use:
- DEV/architecture calibration: Experiment 1 only;
- held-out natural replication: Experiment 2 under an unchanged abstract edge definition.

No parameter estimated from Experiment 2 may be used to redefine the loop topology.

## 3. Evidence ceiling

A clean PASS across both experiments could support:
- R2 natural single-domain closed-loop recovery; and
- a narrow within-paradigm replication across two distinct confidence manipulations.

It would **not** yet satisfy R3 unrelated-domain replication because both experiments are human perceptual/metacognitive tasks.

It would not establish a universal Recursive Observability law.

## 4. Required controls

Before scoring, numerical preregistration must freeze:

- objective difficulty/performance controls for E2;
- initial-choice/RT controls where available;
- condition/manipulation controls;
- information-seeking cost or task context controls if present;
- E4 comparison that separates mere regression-to-the-mean from update after new evidence;
- confidence-label permutation;
- policy-marginal-preserving permutation;
- final-confidence reassignment;
- condition-preserving one-edge-broken controls;
- subject-held-out or experiment-held-out scoring;
- complexity penalties.

A simple replication of the paper's reported mediation is not enough.

## 5. O3 boundary

Even if the explicit confidence loop passes, this is initially O2/model-guided observation evidence.

O3/reflexive observer requires evidence that a model of the observer/model relation itself adds prospective information beyond explicit confidence and first-order task state.

ROX-0004 must not relabel O2 as O3.

## 6. Source qualification

Before any natural scoring:
1. enumerate OSF m5a4x recursively;
2. identify raw trial-level files for both experiments;
3. preserve exact hashes;
4. verify the temporal variables initial confidence -> information-seeking choice -> final confidence are present;
5. verify subject IDs and condition/manipulation labels;
6. freeze numerical preregistration and scorer.

If the archive does not contain the required temporal variables, classify SOURCE_INSUFFICIENT and stop.

No Powerball data may enter ROX-0004.

EUREKA tally remains 3.
