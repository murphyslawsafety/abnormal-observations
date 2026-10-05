# ROX-0004A — Explicit Confidence→Observation-Policy→Updated-Confidence Natural Loop Test

**Version:** 1.0  
**Freeze date:** 2026-10-05  
**ROH class:** ROH-PROBE + ROH-BRIDGE  
**Status:** PREREGISTERED BEFORE NUMERICAL EFFECT SCORING  
**Parent synthetic control:** ROX-0002B CONTROL_PASS  
**Natural source:** Van Marcke & Desender (2025), OSF m5a4x  
**Evidence ceiling:** R2 / O2 model-guided observation candidate  
**EUREKA status:** NONE

## 1. Question

Does the explicit pre-policy confidence state participate in a held-out closed observation loop in two independent human experiments:

`M_t (initial confidence) -> A_t (seek information) -> Z_{t+1} (second observation) -> M_{t+1} (final confidence)`?

This is not an O3/self-model claim. The maximum outcome is O2/model-guided observation candidate support.

## 2. Frozen source bundle

Use the qualified ROX-0004 source artifact:
- workflow run 37245533479;
- artifact 11318997318;
- artifact digest `sha256:256e8f7c8c8cfaee22276bafd0108d25227a861c9b9aae2bceca390c6b6ce066`;
- 49 Experiment-1 subject CSV files;
- 49 Experiment-2 subject CSV files;
- source task code and published analysis code.

Main-task rows are exactly those with `running == "main"`.

Experiment 1 maps source subject 56887 to subject 5 exactly as the source analysis does.

No author-level behavioral exclusion is imported. Rows are included when all variables required for the relevant edge are finite/valid under the source coding.

## 3. Frozen subject splits

Subjects are SHA-sorted by `SHA256("ROX-0004A|EXPx|SUBJECT|"+id)`.

### Experiment 1
DEV (29): 24,9,1,23,21,2,39,25,10,4,31,12,14,50,15,48,32,34,46,28,22,27,44,37,3,20,6,35,47  
VAL (10): 30,45,5,29,8,17,13,18,41,49  
TEST (10): 16,33,40,11,26,38,19,7,36,42

### Experiment 2
DEV (29): 46,42,48,49,10,44,24,3,14,22,7,25,11,36,6,4,34,17,45,38,26,37,23,18,12,15,35,1,13  
VAL (10): 29,32,31,9,20,27,21,40,50,30  
TEST (10): 8,19,28,43,5,39,47,16,33,2

No subject may move partitions.

## 4. Generic representation shared by both experiments

Map each experiment into the same abstract variables:

- `TASK=1` for letter, 0 for color;
- `MANIP=1` for positivefb in Experiment 1 and easy in Experiment 2; 0 otherwise;
- `DIFF=abs(dotsLeft-dotsRight)/80`;
- `LOGRT=log(1+rt)`;
- `COR=initial correctness`;
- `RIGHT=1` if initial response is right / source key n, 0 otherwise;
- `BLOCK=block-5`;
- `TRIAL=withinblocktrial/100`;
- `M=cj`, initial confidence on the source 1..6 scale;
- `SEEK=1` iff `info_choice=="see again"`.

All continuous standardization uses DEV mean/SD separately within each experiment and is frozen for VAL/TEST.

No subject ID enters a predictive model.

## 5. E2: model-state → observation-policy edge

Fit deterministic L2 logistic regression on DEV only.

Solver:
- Newton/IRLS;
- lambda 1e-3;
- unpenalized intercept;
- zero initialization;
- maximum 100 iterations;
- tolerance 1e-10.

### P0 control
Features:
- intercept;
- TASK;
- MANIP;
- standardized DIFF;
- standardized LOGRT;
- COR;
- RIGHT;
- BLOCK;
- TRIAL;
- TASK×DIFF.

### P1 model-state
P1 = P0 + standardized initial confidence M.

Held-out gain:
`G_MA = LL(P1)-LL(P0)-0.5*ln(N)`.

Required in **both experiments**:
- VAL `G_MA > ln(100)`;
- TEST `G_MA > ln(100)`;
- DEV confidence coefficient < 0, because lower confidence should increase SEEK.

## 6. E3: observation-policy → new-observation edge

This edge is task-structural rather than inferred statistically.

The public experiment code specifies:
- if SEEK, a second presentation is delivered and second response/confidence are queried;
- if GIVE RESPONSE, a matched fixation interval is shown and second response/confidence are recorded as -99.

Data-integrity gate:
- every eligible SEEK main row must have valid `resp2,cj2`;
- every eligible non-SEEK main row must have source-missing `resp2,cj2=-99`.

Any violation is STRUCTURE_FAIL.

This edge is counted as task architecture, not independent evidence for ROH.

## 7. E4: new observation → updated model-state edge

Use SEEK rows only.

Outcome:
`M_NEXT = cj2`.

Pre-observation baseline U0:
- intercept;
- standardized initial confidence M;
- TASK;
- MANIP;
- standardized DIFF;
- standardized LOGRT;
- COR;
- RIGHT;
- BLOCK;
- TRIAL.

Post-observation additions U1:
- `COR2` = final correctness;
- `CHANGED` = 1 iff final response differs from initial response.

Fit ordinary ridge linear regression on DEV SEEK rows:
- lambda 1e-3;
- unpenalized intercept.

Freeze DEV residual variance separately for U0/U1 and use Gaussian held-out log likelihood.

Held-out gain:
`G_ZM = LL(U1)-LL(U0)-0.5*2*ln(N_seek)`.

Required in both experiments:
- VAL `G_ZM > ln(100)`;
- TEST `G_ZM > ln(100)`.

No coefficient-sign gate is imposed because response revision can legitimately have context-dependent direction.

## 8. Closed-loop score

For each experiment:

`L_LOOP = min(G_MA_TEST, G_ZM_TEST)`.

The experiment has a natural closed-loop candidate only when both edges independently pass and E3 structure passes.

The two experiments are treated as independent manipulation environments. The same abstract representation, model families, penalties, and thresholds are used in both. Numeric coefficients are fitted separately on each experiment's DEV subjects.

## 9. Edge-destruction controls

Run on TEST only with fitted coefficients frozen.

### D_MA
Within each subject × TASK × MANIP stratum, deterministically permute M across eligible main rows.

Recompute P1 likelihood.

Required:
`G_MA_D <= 0`
in each experiment.

### D_ZM
Within each subject × TASK × MANIP stratum among SEEK rows, jointly permute `COR2,CHANGED` pairs.

Recompute U1 likelihood.

Required:
`G_ZM_D <= 0`
in each experiment.

Seeds are SHA-derived from experiment ID, source experiment, edge, subject, task, and manipulation.

## 10. Representation control

Construct a left/right-flipped copy:
- swap dotsLeft/dotsRight and dotsLeftExtra/dotsRightExtra;
- flip initial and final response side labels consistently;
- correctness remains unchanged.

Retrain DEV and rescore.

Primary gains `G_MA` and `G_ZM` on VAL/TEST must agree with the original analysis to absolute tolerance <=1e-8.

Mismatch => REPRESENTATION_FAIL.

## 11. Outcome classes

### O2_LOOP_REPLICATED

All:
1. E2 passes VAL and TEST in Experiment 1;
2. E4 passes VAL and TEST in Experiment 1;
3. E2 passes VAL and TEST in Experiment 2;
4. E4 passes VAL and TEST in Experiment 2;
5. E3 structural integrity passes in both;
6. both D_MA controls <=0;
7. both D_ZM controls <=0;
8. representation control passes.

Interpretation ceiling:

> Explicit pre-policy confidence participates in a replicated natural observation-policy loop: confidence constrains whether additional evidence is sampled, the policy gates additional observation, and post-observation state variables improve prediction of the updated confidence state in held-out subjects across two different confidence manipulations.

This is R2/O2 candidate evidence only.

### FAIL
Any required gate fails.

### UNIDENTIFIABLE
Source mapping or execution cannot be completed without altering the frozen protocol.

## 12. No post-hoc repair

After scoring begins, do not alter:
- splits;
- variable mapping;
- model features;
- penalties;
- thresholds;
- destruction strata;
- representation control;
- loop definition.

A revised architecture requires a new experiment ID.

## 13. EUREKA boundary

Even O2_LOOP_REPLICATED does not itself increment EUREKA.

A stronger milestone requires transfer of the same frozen abstract loop to an unrelated natural domain beyond target-only calibration, and O3 requires a genuine second-order self-model contribution.

Cross-project EUREKA tally remains 3.
