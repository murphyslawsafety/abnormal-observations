# ROX-0011 — Natural Closed-Loop Zebrafish Sensorimotor Bridge

**Version:** 0.1 DESIGN CANDIDATE
**Date:** 2026-10-06
**ROH class:** ROH-PROBE + ROH-BRIDGE
**Status:** SOURCE-QUALIFICATION PHASE ONLY
**Parent control:** ROX-0002B CONTROL_PASS
**EUREKA status:** NONE

## 0. Why this source is at the right level

ROX-0011 moves to a real vertebrate system in which the observation loop is physically closed by the experiment itself.

Preferred source:
Stytra example imaging dataset, Zenodo record 1692080.

The public dataset contains:
- larval zebrafish behavior;
- calcium imaging;
- a visual grating controlled in closed loop by the fish's own swimming.

The system therefore exposes the operational loop:

`neural/internal state -> motor action -> visual feedback -> updated neural/internal state`.

Unlike trajectory-only chemotaxis, action-dependent sensory feedback is explicit and synchronized with a measured internal neural state.

## 1. Candidate ROH mapping

Subject to schema qualification:

- `M_t`: low-dimensional neural state inferred from calcium activity before motor action;
- `A_t`: swim/motor output;
- `Z_{t+1}`: action-dependent visual feedback / virtual-environment update;
- `M_{t+1}`: neural state after the feedback.

Candidate topology:

`M_t -> A_t -> Z_{t+1} -> M_{t+1}`.

This is the same abstract loop calibrated by ROX-0002B, but with a radically different physical implementation.

## 2. Scientific target

A later frozen numerical test must establish, prospectively on held-out temporal blocks:

### E2 — neural/model state -> motor policy
Past-only neural state improves prediction of the next motor output beyond:
- recent motor history;
- current visual stimulus;
- capacity-matched behavior-only controls.

### E3 — motor policy -> next sensory observation
Motor output changes the next visual feedback under the closed-loop controller.

This edge may be partly task-structural but must be verified from recorded signals rather than assumed from prose.

### E4 — sensory observation -> neural-state update
The action-contingent visual feedback improves prediction of the next neural state beyond:
- previous neural state;
- motor action;
- raw temporal history.

### Closure
The intact factorization must beat:
- neural-state time shifts;
- motor/feedback decoupling;
- feedback replay/permutation controls;
- one-edge-broken decoys.

The weakest indispensable edge determines the loop score.

## 3. State-discovery rule

The natural source does not supply a "self-model" label.

Therefore the initial neural state representation must be:
- learned on DEV only;
- low complexity;
- frozen before VAL/TEST;
- reported with rank/identifiability diagnostics.

Candidate state reduction families may include PCA/SVD or predictive-state compression, but the exact family must be frozen after schema qualification and before effect scoring.

No neural component may be selected because it correlates favorably with TEST behavior.

## 4. Evidence ceiling

Even a clean PASS initially supports a natural **closed sensorimotor observation loop**.

It does not yet establish O3/self-model recursion.

O3 requires an additional prospective variable that represents the observer's own prediction/error/model relation and contributes beyond ordinary neural state and history.

If the source exposes prediction-error or mismatch epochs, those can motivate a later separately frozen O3 test.

## 5. Cross-domain significance

A zebrafish PASS would be materially different from the human information-seeking line:
- different species;
- different observation modality;
- different physical action;
- directly closed action-to-sensory feedback;
- measured neural dynamics.

The only allowed shared structure is the frozen topology:
`state -> observation policy/action -> observation -> state update`.

## 6. Source qualification

Before numerical scoring:

1. download exactly `example_imaging.zip` from Zenodo record 1692080;
2. verify published MD5 `eb6dc08c900aff6112f0d3bb4d06be82`;
3. record SHA-256;
4. enumerate every archive file;
5. identify synchronized behavioral, stimulus/feedback, and calcium-imaging products;
6. inspect schemas/dimensions without computing edge effects;
7. verify enough temporal samples for DEV/VAL/TEST;
8. determine whether motor output and visual feedback are separate recorded channels;
9. freeze the state estimator, splits, edge scorers, complexity penalties, and destruction controls.

If a necessary channel is absent, classify SOURCE_INSUFFICIENT without effect scoring.

## 7. Powerball boundary

No Powerball data enter ROX-0011.

Powerball remains a later hostile blind checksum after independent cross-domain architecture is earned.

EUREKA tally remains 3.
