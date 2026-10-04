# ROX-0002B — Reflexive Loop-Topology Recovery

**Version:** 0.1 DESIGN CANDIDATE
**Date:** 2026-10-04
**ROH class:** ROH-CONTROL + ROH-BRIDGE
**Status:** NOT FROZEN / NOT EXECUTED
**EUREKA status:** NONE

## 0. Correction from ROX-0002A

ROX-0002A failed because it imposed a serial additive taxonomy:
record -> uncertainty -> self-model.

The true synthetic O3 cases nevertheless showed strong second-order meta-state gains while the separately reconstructed uncertainty edge often failed.

Therefore ROX-0002B does not require O3 to pass through a scalar O2 threshold.

The target is now the **closed dependency topology**.

## 1. Candidate observer loop

Recover the directed relation:

`history -> predictive state S_t`

`S_t -> model-quality/meta-state M_t`

`M_t -> observation/action policy A_{t+1}`

`A_{t+1} -> information channel / observation Z_{t+1}`

`Z_{t+1} -> updated S_{t+1}, M_{t+1}`.

A reflexive loop requires prospective support for the complete directed cycle, not merely one correlated state variable.

## 2. Edge tests

Each edge is scored by held-out conditional codelength gain against a capacity-matched control.

E1 — predictive-state edge:
past observations predict S/update structure.

E2 — meta-policy edge:
M_t improves prediction of A_{t+1} beyond raw history + S_t.

E3 — policy-observation edge:
A_{t+1} changes the conditional observation distribution / information quality beyond matched policy-marginal controls.

E4 — observation-update edge:
Z_{t+1} improves prediction of the next S/M update under the frozen state estimator.

E5 — closure edge:
the inferred loop predicts held-out joint transitions better than every one-edge-broken decoy.

No single edge can create PASS.

## 3. Reflexive destruction controls

Construct decoys preserving all node marginals and first-order autocorrelation while breaking exactly one edge at a time:

- M->A broken;
- A->Z broken;
- Z->state-update broken;
- temporal loop order reversed;
- whole-loop time shift;
- semantic relabeling.

The full-loop score must fall under every broken-edge decoy.

## 4. Topology score

Let Delta_e be the held-out penalized codelength gain for edge e.

Define:

`L_loop = min(Delta_E2, Delta_E3, Delta_E4)`.

The minimum is used deliberately: a claimed closed loop is only as strong as its weakest indispensable edge.

Also report E1 and E5 separately.

A synthetic candidate advances only if:
- E2,E3,E4 each > ln(100);
- E5 > ln(100);
- every one-edge-broken decoy has L_loop <= 0;
- relabeling invariance passes;
- the same frozen detector rejects passive and memory-only controls.

## 5. Why this is closer to ROH

This tests a topology:

`model of observation -> choice of observation -> new observation -> updated model`.

It does not require the loop to be expressed as one scalar uncertainty variable or one additive regression hierarchy.

That is the operational structure closest to the cross-project phrase:

`OBSERVATION OBSERVING ITSELF`.

## 6. Natural-domain boundary

Only after synthetic qualification may the same topology detector be frozen and transferred to a real adaptive-observation dataset.

A natural PASS must beat:
- raw-history controls;
- first-order predictive-state controls;
- policy-marginal controls;
- one-edge-broken controls;
- target-only calibration.

Human/animal metacognition can calibrate the architecture but does not establish universality.

## 7. Powerball boundary

Powerball remains excluded from fitting or proving the recursive loop.

Only a later frozen cross-domain grammar may be mapped into Powerball as a hostile blind checksum.

EUREKA tally remains 3.
