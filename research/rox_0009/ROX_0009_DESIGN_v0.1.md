# ROX-0009 — Advice-Seeking Natural Observer-Loop Replication

**Version:** 0.1 DESIGN CANDIDATE
**Date:** 2026-10-06
**ROH class:** ROH-PROBE + ROH-BRIDGE
**Status:** SOURCE-QUALIFICATION PHASE ONLY
**Parent control:** ROX-0002B CONTROL_PASS
**Prior natural results:** ROX-0004A and ROX-0007A closed-loop FAIL with strong partial edges
**EUREKA status:** NONE

## 0. Why this source

ROX-0004A and ROX-0007A repeatedly found evidence that an explicit pre-observation model/confidence state can affect information-seeking or sampling policy, but the full loop did not survive the frozen held-out update/destruction gates.

ROX-0009 changes the observation channel and task while preserving the abstract topology.

Preferred source:

Pescetelli, Hauperich & Yeung (2021), "Confidence, advice seeking and changes of mind in decision making", Cognition 215:104810.

Public OSF project:
`z8vay`.

The published task explicitly contains:
- an initial perceptual decision;
- initial confidence;
- a decision to seek/decline advice under free/costly conditions;
- advice content;
- a final decision;
- final confidence.

This exposes the candidate loop:

`M_t -> A_t -> Z_{t+1} -> M_{t+1}`

where:
- M_t = initial confidence;
- A_t = advice-seeking policy;
- Z_{t+1} = received advice / advice agreement relation;
- M_{t+1} = final confidence / revised belief.

## 1. Scientific target

ROX-0009 is intended as a **different observation modality** from repeated visual evidence sampling.

A later frozen test must ask whether the same abstract edge family survives:

### E2 — model-state -> observation policy
Initial confidence predicts whether advice is sought after controlling for objective difficulty, initial choice quality, condition/cost, and trial-history nuisance terms.

### E3 — observation policy -> observation
The seek decision determines whether advice becomes available.

### E4 — observation -> updated model state
Advice content, especially agreement/disagreement with the initial choice, prospectively predicts final confidence / belief revision beyond initial confidence and objective difficulty.

## 2. Strong control opportunity

If the source contains both:
- freely available / externally provided advice; and
- advice that must be actively sought or purchased,

then the exogenous-advice condition becomes an edge-broken control for M->A while preserving the advice-update pathway.

That allows the topology to be attacked as:
- endogenous policy edge;
- exogenous observation control;
- common update edge.

## 3. Cross-task bridge

ROX-0009 is scientifically useful only if the edge definitions remain abstract:

`model state -> observation policy -> observation -> updated model state`.

No Kaanders-, Mohr-, or Pescetelli-specific coefficient is imported as the grammar.

The observation modality is allowed to change:
- visual resampling in prior tests;
- social advice here.

A later bridge can count only if the same frozen topology/decision logic transfers across these modalities.

## 4. Source qualification

Before any numerical scoring:

1. enumerate OSF `z8vay` recursively;
2. preserve exact file paths, sizes, and hashes;
3. identify raw trial-level files;
4. identify participant IDs;
5. identify initial response and confidence;
6. identify advice-seeking choice;
7. identify free/cost condition;
8. identify actual advice content and agreement/disagreement;
9. identify final response and final confidence;
10. identify independent experiment/replication structure if present;
11. verify enough participants for subject-held-out splits;
12. freeze numerical models, split, penalties, and destruction controls.

If any indispensable temporal variable is absent, classify SOURCE_INSUFFICIENT without effect scoring.

## 5. Candidate natural controls after qualification

Potential controls, to be frozen only after schema inspection:
- participant-held-out DEV/VAL/TEST;
- confidence-to-seeking alignment destruction within cost/difficulty strata;
- advice-content permutation preserving advice marginals;
- exogenous/free-advice control if available;
- semantic left/right relabeling;
- target-only sufficiency;
- previous-trial advice-history control.

## 6. Evidence ceiling

A PASS can support another R2/O2 natural observation-loop instance in a different task/modality.

It does not establish O3 self-reference or universal ROH.

A cross-modal R3/R4 claim requires the **same frozen abstract topology decision rule** to transfer prospectively beyond target-only calibration.

No Powerball data enter ROX-0009.

EUREKA tally remains 3.
