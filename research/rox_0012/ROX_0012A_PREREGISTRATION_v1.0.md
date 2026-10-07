# ROX-0012A — Quantum Measurement-Backaction / Regime Calibration

**Version:** 1.0
**Freeze date:** 2026-10-07
**ROH class:** ROH-CONTROL + ROH-BRIDGE
**Status:** PREREGISTERED BEFORE PROJECT SCORER EXECUTION
**Source:** Zhang et al. 2026, Quantum Zeno effect in the spatial evolution of a single atom
**Zenodo:** 10.5281/zenodo.19690318
**Evidence ceiling:** known-physics calibration only
**EUREKA status:** NONE
**Canonical EUREKA tally:** 6

## 1. Purpose

Calibrate the ROX measurement-as-transformation architecture against a real quantum system in which measurement strength and frequency are experimentally varied.

This is not a discovery test of the quantum Zeno effect.

## 2. Frozen source subset

Use only the experimental arrays embedded in the source-supplied Figure 3 script.

Measurement strengths are the 15 reported optical powers normalized by the maximum reported power.

Three measurement-frequency conditions:
- N=5 pulses;
- N=10 pulses;
- N=15 pulses.

Outcome:
- final atomic loss probability.

Do not use source simulation arrays for PASS scoring.

## 3. Backaction gate B1

For each N separately require:

1. the no-measurement/zero-strength point has larger loss than the strongest-measurement point;
2. Spearman rank correlation between normalized strength and loss is negative;
3. the mean loss over strengths >=0.6 is lower than the mean loss over strengths in (0,0.6).

All three N conditions must pass.

## 4. Frequency gate B1F

At every nonzero measurement strength where the three curves share the same strength, score the ordering:

P_loss(N=15) <= P_loss(N=10) <= P_loss(N=5).

Required:
- ordering holds at >= 11/14 nonzero strengths;
- at the strongest measurement strength, N=15 loss < N=10 loss < N=5 loss.

This tests whether more frequent physical measurements produce stronger suppression under matched strength.

## 5. Fixed regime gate B4

The source reports a crossover near normalized measurement strength 0.6.

Treat 0.6 as a published calibration boundary, not a discovered project boundary.

For each N:
- fit ordinary least-squares slope of loss vs strength on points 0 < I < 0.6;
- fit ordinary least-squares slope on points I >= 0.6.

Required:
- low-regime slope < 0;
- abs(high_slope) < abs(low_slope).

At least 2/3 N conditions must pass.

This gate only checks whether the source data reproduce the published weak-to-strong measurement crossover under a simple fixed diagnostic.

## 6. Measurement-as-transformation classification

### BACKACTION_REGIME_CALIBRATION_PASS

Requires B1, B1F, and B4 all pass.

Maximum claim:

> In this established quantum system, changing physical measurement strength and frequency changes subsequent state evolution, and the strength-response relation exhibits a weaker-slope strong-measurement regime beyond the published crossover.

### CONTROL_FAIL

Any gate fails.

## 7. Untested claims

ROX-0012A does not test:
- consciousness;
- whether a human reads the result;
- M∘T versus T∘M direct reversed-order noncommutativity;
- cross-domain universality;
- observation-induced masking of a recoverable hidden grammar;
- Powerball predictability.

These require separate experiments.

## 8. Audit caveat

The publication and supporting scripts are known prior art and some effect values were visible during source qualification.

Therefore ROX-0012A is explicitly a method calibration, not blind validation and not eligible for a new EUREKA.

Canonical EUREKA tally remains 6.
