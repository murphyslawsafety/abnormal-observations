# ROX-0001A — Final Outcome v1.0

**Date:** 2026-10-04  
**ROH class:** ROH-CONTROL  
**Status:** CONTROL_FAIL  
**Classification:** LEGITIMATE NEGATIVE / SYNTHETIC METHOD CALIBRATION  
**EUREKA:** NONE  
**Cross-project EUREKA tally:** 3

## Frozen execution

- workflow run: 37218565056
- job: 111484037854
- preregistration Git blob: aadb730cc3481de7a2ceeb3c47cf226624ba4846
- pre-generation clarification v1.0.2 Git blob: fcb55edfdc23dbd65175f1f3a246fe65775408c0
- runner Git blob: 67d648f6cac7d41bbcfa5e279398ce89ce977f17
- result SHA-256: 11cb7129d4bf7d79308e3fb405071c7d63e8d8f4862771d9fade608ee6a487c6
- artifact ID: 11309425500
- artifact digest: sha256:9f5935e2ef77123f1059649ee9a153788baf0b1ec61e9d954f4ad29892f98a1a

## Result

The frozen classifier correctly classified **5/12** opaque cases.

Confusion summary:
- N0 -> N0: 4/4
- N3 -> N3: 1/4
- N3 -> N0: 2/4
- N3 -> UNIDENTIFIABLE: 1/4
- N4 -> N4: 0/4
- N4 -> N0: 3/4
- N4 -> UNIDENTIFIABLE: 1/4

Required gate "every true N4 classified N4" failed.

No N0 case was falsely classified N4.

All four shifted-model pseudo-recursive controls had nonpositive G4, so the control successfully rejected the deliberately broken second-order alignment, but it lacked sensitivity to the true N4 cases under the frozen generator/model family.

## Interpretation

ROX-0001A does **not** validate the proposed raw nested-logistic detector for recursive observer state.

The result is particularly useful because it separates two issues:
- specificity was acceptable against the frozen pseudo-recursive controls;
- sensitivity to genuine recursive-model dependence was inadequate.

This experiment may not be repaired by changing coefficients, thresholds, memory depth, or role assignment after reveal.

A successor requires a new experiment ID and a representation-level correction.

## Prior-art implication

The next representation should not reinvent first-order predictive states. Predictive equivalence classes of histories are already formalized in computational mechanics / epsilon-machines, and predictive-state representations provide an established observable-state framework.

The unresolved ROH-specific target is therefore the dynamics of the **observer/measurement map itself**: whether a system's model of its own predictive state or uncertainty prospectively changes what it observes or how it acts, beyond a capacity-matched non-reflexive control.

## Boundary

This synthetic failure is not evidence against or for a universal Recursive Observability architecture in nature.

No Powerball scoring is authorized from ROX-0001A.

EUREKA tally remains 3.
