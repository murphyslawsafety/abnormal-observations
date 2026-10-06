# ROX-0011A — Natural Zebrafish Closed Sensorimotor-Observation Loop

**Version:** 1.0
**Freeze date:** 2026-10-06
**ROH class:** ROH-PROBE + ROH-BRIDGE
**Status:** PREREGISTERED BEFORE NUMERICAL EDGE SCORING
**Parent control:** ROX-0002B CONTROL_PASS
**Source:** Stytra example_imaging.zip, Zenodo 1692080
**Evidence ceiling:** natural N3 / closed active-observation architecture; not O3 self-model recursion
**EUREKA status:** NONE

## 1. Question

Does a real vertebrate closed-loop preparation support the frozen topology:

`M_t -> A_t -> Z_t -> M_{t+1}`

where:
- `M_t` is a low-dimensional calcium-imaging state derived prospectively from brain fluorescence;
- `A_t` is motor vigour;
- `Z_t` is the recorded visual-feedback velocity;
- `M_{t+1}` is the next calcium-imaging state?

The experiment must also distinguish the intact closed-loop edge from open-loop periods in the same animal.

## 2. Source lock

Download exactly:
`https://zenodo.org/records/1692080/files/example_imaging.zip?download=1`

Published MD5 required:
`eb6dc08c900aff6112f0d3bb4d06be82`.

Qualified source facts:
- Huc:GCaMP6f larval zebrafish, age 7 dpf;
- protocol duration 240 s;
- imaging frame time 495.28 ms;
- image stack shape 485 x 300 x 175;
- behavior log: 34,078 rows;
- motor estimator log: 9,752 rows with `vigour`;
- stimulus log: 9,752 rows with actual visual velocity, scheduled base velocity, closed-loop gain, and fish-swimming flag;
- stimulus metadata explicitly labels the stimulus `closed loop 1D`.

Source qualification artifacts:
- run 37526106432, artifact 11442078159;
- decoded-source artifact 11442810328;
- decoded-source digest `sha256:5cfd0bae9cac69ce721ebf46c84ecff01b79f713559755bc3918848272af03e2`.

## 3. Time alignment

Define nominal imaging frame times:

`t_i = i * 0.49528 s`, i=0..484.

For every transition i -> i+1, aggregate estimator/stimulus rows whose recorded `t` lies in:

`[t_i, t_{i+1})`.

A transition is eligible only when:
- at least one estimator row and one stimulus row fall in the interval;
- all required values are finite.

No time offset is fitted from outcomes.

## 4. Temporal splits

Using source-frame time only:

- DEV: source frame time < 80 s;
- VAL: 80 <= source frame time < 160 s;
- TEST: source frame time >= 160 s.

An edge is used only if both source frame i and target frame i+1 lie in the same split.

No transition crosses a split boundary.

## 5. Neural-state representation

No ROI or neuron identity is selected from outcomes.

For every imaging frame:
1. crop nothing;
2. average nonoverlapping 10 x 5 pixel blocks, converting 300 x 175 into a 30 x 35 = 1,050-dimensional coarse fluorescence vector;
3. using DEV frames only, subtract each feature's DEV mean and divide by DEV SD; constant features receive SD=1;
4. fit PCA/SVD on standardized DEV frames only;
5. retain exactly the first 3 principal-component scores.

Call this 3-vector `M_t`.

The PCA transform freezes before VAL/TEST.

Report:
- variance explained by PC1/PC2/PC3 on DEV;
- singular values;
- effective rank;
- condition diagnostics.

No biological cell-type interpretation is attached to a component.

## 6. Frame-level action and observation

For interval i:

`A_i = log(1 + mean(vigour))`.

Stimulus quantities:
- `Z_i = mean(closed loop 1D_vel)`;
- `B_i = mean(closed loop 1D_base_vel)`;
- `G_i = mean(closed loop 1D_gain)`;
- `F_i = mean(closed loop 1D_fish_swimming)`.

Define:
- CLOSED transition iff `G_i >= 0.5`;
- OPEN transition iff `G_i < 0.5` and `B_i <= -5`;
- PAUSE otherwise.

PAUSE transitions may enter E2/E4 baseline fitting but are excluded from the closed-vs-open E3 gate.

## 7. Regression engine

All models are deterministic ridge Gaussian regressions:
- lambda = 1e-3;
- intercept unpenalized;
- coefficients fit on DEV only;
- DEV residual variance freezes for VAL/TEST likelihood;
- continuous predictors standardized by DEV mean/SD;
- no VAL/TEST tuning.

Gaussian held-out log likelihood is used.

For adding k scalar coefficients on N held-out transitions, complexity penalty:

`0.5 * k * ln(N)`.

## 8. E2 — neural state -> motor action

Baseline E2-0 predicts A_i from:
- intercept;
- A_{i-1};
- A_{i-2};
- Z_{i-1};
- B_i;
- G_i.

Full E2-1 adds:
- M_t PC1, PC2, PC3.

Held-out gain:

`G_E2 = LL(E2-1)-LL(E2-0)-0.5*3*ln(N)`.

Required:
- VAL `G_E2 > ln(100)`;
- TEST `G_E2 > ln(100)`.

## 9. E3 — motor action -> sensory observation

Baseline E3-0 predicts Z_i from:
- intercept;
- B_i;
- G_i.

Full E3-1 adds:
- A_i;
- A_i * G_i.

Fit on DEV active transitions (CLOSED + OPEN).

Score separately:

`G_E3_closed` on CLOSED held-out transitions;
`G_E3_open` on OPEN held-out transitions.

Required in both VAL and TEST:
- CLOSED `G_E3_closed > ln(100)`;
- OPEN `G_E3_open <= 0`.

This is the recorded endogenous-vs-exogenous feedback gate.

## 10. E4 — sensory observation -> neural-state update

Multivariate outcome:
`M_{t+1}` (3 PCs).

Baseline E4-0:
- intercept;
- M_t PC1..PC3;
- A_i;
- B_i;
- G_i.

Full E4-1 adds:
- Z_i.

Fit one ridge regression per output PC on DEV.

Freeze each DEV residual variance.

Held-out total log likelihood is summed over the three outputs.

Gain:

`G_E4 = LL(E4-1)-LL(E4-0)-0.5*3*ln(N)`.

Required:
- VAL `G_E4 > ln(100)`;
- TEST `G_E4 > ln(100)`.

## 11. Closed-loop score

For each held-out split:

`L_LOOP = min(G_E2, G_E3_closed, G_E4)`.

A natural loop candidate requires every indispensable edge independently positive under its frozen gate.

No strong edge can rescue a failed edge.

## 12. Edge-destruction controls

Use fitted DEV models without refit.

### D_E2
Circularly shift the TEST neural-state sequence by 37 imaging frames while preserving all non-neural predictors.

Required:
`G_E2_destroyed <= 0`.

### D_E3
On CLOSED TEST transitions, circularly shift A_i by 31 eligible CLOSED transitions while preserving B,G,Z.

Required:
`G_E3_closed_destroyed <= 0`.

### D_E4
Within TEST schedule strata defined by rounded (B_i,G_i), deterministically permute Z_i.

Required:
`G_E4_destroyed <= 0`.

Seeds/order are deterministic from `ROX-0011A` and the edge name.

## 13. Representation control

Horizontally reflect every imaging frame before the same 10 x 5 block averaging, then refit the DEV PCA and all DEV models.

Because reflection is a coordinate permutation rather than a biological intervention, all primary VAL/TEST gains must match the original analysis to absolute tolerance <= 1e-6 nats.

Mismatch => REPRESENTATION_FAIL.

## 14. Outcome classes

### NATURAL_CLOSED_LOOP
All:
- E2 VAL/TEST pass;
- E3 CLOSED VAL/TEST pass;
- E3 OPEN VAL/TEST <=0;
- E4 VAL/TEST pass;
- D_E2, D_E3, D_E4 pass;
- representation control passes;
- neural rank/conditioning diagnostics are finite.

Maximum claim:

> In this real closed-loop zebrafish preparation, a prospectively frozen low-dimensional neural state predicts motor action, motor action controls the next sensory stream only in closed-loop epochs, and the realized sensory stream predicts the next neural state under held-out temporal blocks and edge-destruction controls.

This is natural closed sensorimotor-observation architecture. It is not O3 self-model recursion.

### FAIL
Any required gate fails.

### UNIDENTIFIABLE
The source cannot support the frozen computation without protocol alteration.

## 15. No repair

After scoring begins, do not alter:
- frame timing;
- split boundaries;
- block size;
- PCA dimension;
- regression features;
- penalties;
- thresholds;
- CLOSED/OPEN definitions;
- destruction offsets/strata;
- representation control.

A revision requires a new experiment ID.

## 16. EUREKA boundary

Even NATURAL_CLOSED_LOOP does not automatically create EUREKA-004.

A stronger cross-domain milestone requires transfer of the same abstract loop logic to an independent natural implementation beyond target-only calibration, and O3/R5 requires second-order observer/model feedback.

Cross-project EUREKA tally remains 3.
