# ROX-0003 — Natural Human Reflexive-Observation Calibration

**Version:** 0.1 DESIGN CANDIDATE
**Date:** 2026-10-04
**ROH class:** ROH-PROBE + ROH-BRIDGE
**Status:** SOURCE-QUALIFICATION PHASE ONLY / NO NATURAL RESULT YET
**Parent control:** ROX-0002B CONTROL_PASS
**EUREKA status:** NONE

## 0. Purpose

ROX-0002B established that the frozen weakest-edge topology test can distinguish an intact synthetic observer loop from one-edge-broken controls when a sufficient-state representation is available.

ROX-0003 moves to the R2 gate: a real human adaptive-observation system.

The first preferred source is Balsdon, Wyart & Mamassian (2020), "Confidence controls perceptual evidence accumulation", because:
- trial-wise sequential evidence is observed;
- participants regulate when perceptual accumulation terminates;
- confidence is explicitly measured;
- the published analysis argues that Type-II/confidence processing moderates Type-I evidence accumulation;
- data and model code are publicly archived on OSF.

This experiment is a reanalysis under the frozen ROX topology framework, not a claim that the published effect is new.

## 1. Natural loop candidate

Map the task into:

- M_t — metacognitive/confidence state inferred from the evidence available up to sample t;
- A_t — continue/stop accumulation policy or equivalent bound-crossing action;
- Z_{t+1} — next available evidence sample when accumulation continues;
- M_{t+1} — updated metacognitive/confidence state after the additional sample.

Candidate loop:

`M_t -> A_t -> Z_{t+1} -> M_{t+1}`.

This is an O2/model-guided observation candidate. It is not automatically O3 self-model recursion.

## 2. Source-side state rule

ROX-0003 will not use the authors' fitted confidence parameters as truth labels.

Before scoring, the state estimator must be frozen from the task's observable evidence stream only.

Candidate state families to be frozen after schema inspection but before outcome scoring:
- Bayesian posterior correctness probability from the published stimulus likelihoods;
- predictive-state / causal-state compression of the evidence history;
- capacity-matched raw-evidence-history control.

The final state family and all thresholds require a preregistration amendment after source schema qualification and before numerical scoring.

## 3. Required natural edges

The natural test must support all applicable edges prospectively on held-out trials:

### H1 — model-to-policy
M_t improves prediction of continue/stop policy beyond raw evidence/history controls.

### H2 — policy-to-observation
The policy changes which evidence becomes available/integrated next. For self-paced stopping this is tested through the observed continuation boundary, not by claiming the physical stimulus generator itself depends on the participant.

### H3 — observation-to-model-update
The next evidence sample changes the estimated confidence/model state in the predicted direction and improves held-out model-update likelihood.

### H4 — closed-loop advantage
The intact factorization outperforms every one-edge-broken decoy under held-out codelength.

## 4. Controls

Required:
- confidence/model-state time shift;
- within-condition state permutation;
- action/policy marginal-preserving permutation;
- next-evidence reassignment preserving stimulus marginals;
- raw-history capacity-matched baseline;
- participant-ID removal/permutation control;
- semantic relabeling;
- target-only sufficiency.

A published confidence-information-seeking association is not by itself an ROX PASS.

## 5. Split

Subject-level split is preferred to avoid within-person leakage:

- DEV subjects: deterministic SHA partition;
- VAL subjects: deterministic SHA partition;
- TEST subjects: deterministic SHA partition.

If the archived data cannot support a subject-held-out split, the experiment becomes UNIDENTIFIABLE under this version rather than silently changing to trial-level random splits.

## 6. Evidence ceiling

A PASS can establish only:

> In one real human adaptive-observation task, a frozen observer-state representation participates in a prospectively supported closed observation-policy loop under matched controls.

This is R2 candidate evidence.

It does not establish:
- a universal ROH;
- O3 self-model recursion;
- consciousness-dependent physics;
- Powerball predictability.

## 7. Cross-domain next gate

If ROX-0003 passes, the same abstract loop signature and frozen decision logic must transfer to a nonhuman natural system under a new experiment ID.

The rhesus-monkey adaptive-information-seeking paradigm of Tu, Pani & Hampton (2015) is a preferred biological replication target if trial-level data can be obtained with auditable provenance.

## 8. Source qualification

Before any numerical scoring:
1. enumerate the OSF data archive;
2. preserve file names, sizes, and hashes;
3. identify trial-level behavioral files and column schema;
4. identify whether subject IDs and evidence-sequence data are present;
5. determine whether the natural loop is actually identifiable from the archive;
6. freeze the numerical preregistration.

No natural outcome is declared during source qualification.

EUREKA tally remains 3.
