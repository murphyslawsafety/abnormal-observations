# ROX-0002A — Final Outcome v1.0

**Date:** 2026-10-04
**ROH class:** ROH-CONTROL
**Status:** CONTROL_FAIL
**Classification:** LEGITIMATE NEGATIVE / CLOSED-LOOP SYNTHETIC CALIBRATION
**EUREKA:** NONE
**Cross-project EUREKA tally:** 3

## Frozen execution

- workflow run: 37241519756
- job: 111551017478
- preregistration Git blob: 314c8a1a887d862ff998bf43e03f456eae74e8e4
- pre-generation clarification Git blob: 5ef2a538f77300ce5bc95dc4e3ba43220d6f9707
- runner Git blob: ea69d7bf0a82c09a1f3a430ac62c9a7ef3451b6d
- result SHA-256: 1a14e040a5733ad930684c9a1f40e78bf5f78a047b9c46385eb7f191bd957790
- artifact ID: 11317427123
- artifact digest: sha256:e0ecf2f3c7a8aab4629ed16ce9ff4f614102b66db5fd2724ba2a2903ad65d5e8

## Result

Overall:
- 9/16 final classes correct.
- CONTROL_FAIL.

Confusion:
- O0 -> O0: 4/4.
- O1 -> O1: 4/4.
- O2 -> O0: 3/4.
- O2 -> UNIDENTIFIABLE: 1/4.
- O3 -> O3: 1/4.
- O3 -> UNIDENTIFIABLE: 3/4.

Required all-O2 and all-O3 gates failed.

No O0 case was falsely classified O2/O3.

Semantic relabeling mismatch count = 0.

Every O2/O3 policy-marginal decoy failed to classify as O2/O3.

Every O3 self-model destruction control passed:
- shifted reconstructed meta-state: G3 <= 0;
- within-context permuted meta-state: G3 <= 0;
- reversed meta-state: G3 <= 0.

## Important structured result

Although the preregistered class gate failed, the four true O3 cases produced TEST G3 values:

- +51.0406390859
- +53.2036033951
- +15.7414429212
- +16.4297878686

The frozen O3 requirement was G3 > ln(100) **and** G2 > 0.

Three cases were therefore classified UNIDENTIFIABLE because the prerequisite O2/uncertainty edge did not survive, not because the second-order meta-state term was absent.

This observation is post-result diagnostic only. It does not convert the experiment to PASS.

## Interpretation

The raw sequential taxonomy O0 -> O1 -> O2 -> O3 is too rigid for the intended recursive-observer architecture.

ROX-0002A successfully distinguished:
- passive policy from record-coupled policy;
- true aligned second-order meta-state from shifted/permuted/reversed meta-state controls;
- true policy coupling from policy-marginal decoys.

But it did not reliably recover the first-order uncertainty-policy edge O2.

The next experiment must therefore test the **closed loop topology directly** rather than demand a fixed additive nesting in which O3 is only allowed after O2 crosses a separate threshold.

No thresholds or coefficients are changed under ROX-0002A.

## Required stop

ROX-0002A is closed.

No natural-domain claim, Powerball scoring, or EUREKA is authorized from this result.

A successor must receive a new experiment ID and freeze a loop-topology criterion before execution.

EUREKA tally remains 3.
