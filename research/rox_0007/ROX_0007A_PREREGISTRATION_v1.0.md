# ROX-0007A — Active-vs-Fixed Confidence→Sampling→Confidence Natural Loop

**Version:** 1.0
**Freeze date:** 2026-10-05
**ROH class:** ROH-PROBE + ROH-BRIDGE
**Status:** PREREGISTERED BEFORE NUMERICAL EFFECT SCORING
**Parent synthetic control:** ROX-0002B CONTROL_PASS
**Natural source:** Kaanders et al., pinned public repository commit 2f9c697454a5e6047c4d389da135c74992f0d9f3
**Evidence ceiling:** R2 / O2 natural model-guided observation candidate
**EUREKA status:** NONE

## 1. Scientific question

In Experiment 2, does the participant's explicit initial confidence participate in an active observation loop:

`Conf1 -> self-selected evidence allocation -> Conf2`

and does the model-state -> allocation edge weaken when the experimenter, rather than the participant, controls the evidence allocation?

The Free and Fixed sessions are treated as paired natural implementations of the same abstract observation process with one crucial edge changed: agency over sampling.

## 2. Frozen source

Qualified source artifact:
- workflow run 37311209711;
- artifact 11345531906;
- artifact digest `sha256:36df146c48f101dfca84bb58f06084a05a287971b74dab432d42853a20a35657`.

Pinned files:
- `data/exp2_data_free.csv`, Git blob `292ec7235145b6fb6e90ebccda10ee94e5077d15`;
- `data/exp2_data_fixed.csv`, Git blob `0ffdd859eeaa81cb179dbdf1cc87dfb5d33dbfe5`;
- `data/exp2_variable_definitions.docx`, Git blob `ef3f9a0f86d7539be23f7cb0293b67d794784a36`.

Qualified schema:
- Free: 2,244 rows, 18 participants;
- Fixed: 2,256 rows, the same 18 participant IDs;
- both contain Conf1, Conf2, Correct1/2, RT1/2, dot counts, initial/final responses, actual sampling times, sampling length and confidence change;
- Fixed additionally contains experimenter-controlled left/right presentation times.

## 3. Subject-held-out split

Sort subject IDs by:
`SHA256("ROX-0007|SUBJECT|"+subject_id)`.

Frozen result:

DEV (10):
18,14,20,15,26,25,10,22,19,24

VAL (4):
11,7,21,2

TEST (4):
1,13,17,9

The same split applies to Free and Fixed.

No subject ID enters a predictive model.

## 4. Representation

For every trial:

- `M=Conf1`;
- `M_NEXT=Conf2`;
- `DIFF=abs(DotDifference)`;
- `LOGRT=log(1+RT1)`;
- `COR=Correct1`;
- `LEFT=1` iff Response1 is left;
- `BLOCK=Block/8`;
- `TRIAL=Trial/max_trial_within_source_file`.

### Free policy/exposure

Reconstruct from primitive left/right gaze times rather than using the author's derived DeltaSampling:

If initial choice is left:
`CHOSEN=LeftTime`, `UNCHOSEN=RightTime`.

If initial choice is right:
`CHOSEN=RightTime`, `UNCHOSEN=LeftTime`.

`A_FREE = CHOSEN-UNCHOSEN`.

`TOTAL_FREE = CHOSEN+UNCHOSEN`.

Positive A_FREE means more sampling of the initially chosen option.

### Fixed exogenous allocation

Reconstruct from experimenter presentation times:

If initial choice is left:
`CHOSEN_PLAN=Left_Presentation_Time`, `UNCHOSEN_PLAN=Right_Presentation_Time`.

If initial choice is right:
`CHOSEN_PLAN=Right_Presentation_Time`, `UNCHOSEN_PLAN=Left_Presentation_Time`.

`A_FIXED=CHOSEN_PLAN-UNCHOSEN_PLAN`.

`TOTAL_FIXED=CHOSEN_PLAN+UNCHOSEN_PLAN`.

Positive A_FIXED means the experimenter showed the initially chosen option longer.

All continuous predictors are standardized using DEV mean/SD separately within Free and Fixed; transformations freeze for VAL/TEST.

## 5. E2 — model state → observation policy

Use deterministic ridge linear regression:
- lambda 1e-3;
- intercept unpenalized.

### Free baseline F0
Predict A_FREE from:
- intercept;
- standardized DIFF;
- standardized LOGRT;
- COR;
- LEFT;
- BLOCK;
- TRIAL;
- standardized TOTAL_FREE.

### Free full F1
F1 = F0 + standardized M.

### Fixed baseline X0
Predict A_FIXED from the same abstract controls, replacing TOTAL_FREE by TOTAL_FIXED.

### Fixed full X1
X1 = X0 + standardized M.

Fit Free and Fixed models independently on DEV only.

Freeze DEV residual variance separately for each model and score Gaussian held-out log likelihood.

For set S:

`G_FREE(S)=LL(F1)-LL(F0)-0.5*ln(N_S)`.

`G_FIXED(S)=LL(X1)-LL(X0)-0.5*ln(N_S)`.

Agency contrast:

`G_AGENCY(S)=G_FREE(S)-G_FIXED(S)`.

Required:
- VAL G_FREE > ln(100);
- TEST G_FREE > ln(100);
- VAL G_AGENCY > ln(100);
- TEST G_AGENCY > ln(100);
- VAL and TEST G_FIXED <= ln(100);
- DEV coefficient on M in F1 > 0.

This tests whether higher initial confidence prospectively predicts stronger confirmatory evidence allocation specifically when allocation is participant-controlled.

## 6. E4 — observation allocation → updated model state

Primary test uses Free trials.

### U0
Predict M_NEXT from:
- intercept;
- standardized M;
- standardized DIFF;
- standardized LOGRT;
- COR;
- LEFT;
- BLOCK;
- TRIAL;
- standardized TOTAL_FREE.

### U1
U1 = U0 + standardized A_FREE.

Fit on DEV Free trials only using ridge linear regression with lambda 1e-3 and unpenalized intercept.

Freeze DEV residual variance for U0/U1.

Held-out gain:

`G_UPDATE(S)=LL(U1)-LL(U0)-0.5*ln(N_S)`.

Required:
- VAL G_UPDATE > ln(100);
- TEST G_UPDATE > ln(100);
- DEV coefficient on A_FREE > 0.

Positive direction means greater confirmatory sampling predicts higher subsequent confidence after initial confidence and task-state controls.

## 7. Fixed observation-update diagnostic

Apply the same U0/U1 family in Fixed, replacing TOTAL_FREE with TOTAL_FIXED and A_FREE with A_FIXED.

Report but do not use for the primary PASS gate.

This diagnostic asks whether externally imposed confirmatory exposure also predicts the second confidence state.

## 8. Closed-loop score

For S in {VAL,TEST}:

`L_LOOP(S)=min(G_FREE(S), G_AGENCY(S), G_UPDATE(S))`.

Required:
- VAL L_LOOP > ln(100);
- TEST L_LOOP > ln(100).

The weakest indispensable held-out edge controls the result.

## 9. Edge-destruction controls

Run on TEST with all fitted coefficients frozen.

### D_MA
Within each TEST participant, deterministically permute Conf1 across Free trials.

Recompute F1 likelihood.

Required:
`G_FREE_D_MA <= 0`.

### D_ZM
Within each TEST participant, deterministically permute A_FREE across Free trials.

Recompute U1 likelihood.

Required:
`G_UPDATE_D_ZM <= 0`.

Seeds:
`SHA256("ROX-0007A|CONTROL|"+edge+"|"+subject)`.

No refitting is allowed.

## 10. Representation control

Create a complete left/right-reflected representation before feature construction:
- swap DotNumberLeft and DotNumberRight;
- swap LeftTime and RightTime;
- swap Left_Presentation_Time and Right_Presentation_Time;
- flip Response1 left↔right;
- flip Response2 left↔right.

Retrain DEV models and rescore.

Because the primary variables are choice-relative rather than coordinate-relative, all primary VAL/TEST gains must agree with the original analysis to absolute tolerance <=1e-8.

Failure => REPRESENTATION_FAIL.

## 11. Outcome classes

### O2_ACTIVE_LOOP_SUPPORT

All:
1. VAL and TEST E2 Free pass;
2. VAL and TEST agency contrast pass;
3. Fixed E2 remains <=ln(100) on VAL and TEST;
4. DEV Free confidence coefficient >0;
5. VAL and TEST E4 pass;
6. DEV Free allocation coefficient >0;
7. VAL and TEST L_LOOP >ln(100);
8. D_MA <=0;
9. D_ZM <=0;
10. representation control passes.

Maximum interpretation:

> In held-out human subjects, explicit initial confidence predicts self-directed confirmatory evidence allocation when sampling is active but not when allocation is exogenous, and the resulting active allocation predicts the subsequent confidence state beyond initial confidence and task-state controls.

This is R2/O2 candidate support for a natural model-guided observation loop.

### FAIL
Any required gate fails.

### UNIDENTIFIABLE
Source or numerical execution cannot complete without changing this frozen protocol.

## 12. Boundaries

A PASS is not O3/self-model recursion and does not establish universal ROH.

A PASS may authorize a new, separately frozen cross-domain transfer test. Powerball remains excluded from fitting.

No post-hoc change to features, split, signs, penalties, thresholds, controls or source representation is permitted under ROX-0007A.

EUREKA tally remains 3.
