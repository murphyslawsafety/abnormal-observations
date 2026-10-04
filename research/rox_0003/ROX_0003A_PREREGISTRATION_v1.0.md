# ROX-0003A — Natural Confidence-State / Observation-Quantity Test

**Version:** 1.0
**Freeze date:** 2026-10-04
**ROH class:** ROH-PROBE
**Status:** PREREGISTERED BEFORE NATURAL EFFECT SCORING
**Parent control:** ROX-0002B CONTROL_PASS
**Natural source:** Balsdon & Philiastides 2024 / OSF 5D8NH
**Evidence ceiling:** R2 / O2 candidate only
**EUREKA status:** NONE

## 1. Question

Does one low-dimensional state extracted from the participant's accumulated observation history:

1. predict the participant's explicit confidence report; and
2. prospectively predict when the participant stops observing,

in held-out human subjects, beyond current condition, elapsed time, recent raw evidence, and signed accumulated evidence?

A positive result is a **model-guided observation candidate**. It is not O3/self-model recursion and cannot by itself establish "Observation Observing Itself" at the recursive level.

## 2. Frozen cohort

Use the 20-subject final behavioral cohort represented in the public `behaviour.csv` and raw behavioral MAT files, excluding the source-identified technical/performance subject SUB-017.

Subject identifiers:

003,004,005,006,007,008,010,011,012,013,014,015,016,018,020,021,022,023,024,025.

Deterministic SHA sort of `SHA256("ROX-0003|SUBJECT|"+id)` gives:

### DEV (10)
004,016,020,023,018,008,005,025,013,006

### VAL (5)
021,012,003,014,024

### TEST (5)
007,010,015,022,011

No subject may move between partitions.

## 3. Source locking

Required exact source hashes include:
- `preGenEvSep360.mat`: c0b506e720ae6155f6132af36958cca2673e77ffbf482bb119fc4e72354fe967
- `behaviour.csv`: 11adf1a198b057e72cd75d185fc67dad4de20c137134a4e0383dbaa68b9daed0

Each included behavioral MAT must match the source-qualification hash manifest.

No EEG or pupil data are used in ROX-0003A.

## 4. Evidence reconstruction

Use the source-provided `stimEv` 180x2 cell array.

Each cell contains 240 samples representing the full 2-second evidence stream at 120 Hz.

Flatten:
- column 1 -> indices 1..180;
- column 2 -> indices 181..360.

For participant trial i under MATLAB 1-based trial numbering:
- start from `p.trialInds[i]`;
- for odd-numbered trials, add 180;
- for even-numbered trials, do not add 180.

This reproduces the orientation flattening in the public model-fitting code.

Let the resulting 240-sample evidence sequence be `e_i(t)`.

No response, confidence, correctness, or RT enters evidence reconstruction.

## 5. Candidate observation/model state

At frame t:

`E_i(t) = sum_{k<=t} e_i(k)`

`M_i(t) = |E_i(t)|`.

M is intentionally simple: magnitude of accumulated ideal evidence.

ROX-0003A does **not** claim M is uniquely the participant's internal confidence. That interpretation is earned only if the independent explicit-confidence gate below passes.

## 6. Observation-policy representation

Convert each trial to 100-ms discrete-time risk rows.

At 120 Hz:
- one bin = 12 frames;
- maximum = 20 bins / 2 seconds.

For bin b:
- state is evaluated at frame `12*b`;
- trial remains at risk until its recorded RT bin;
- if RT < 2.0 s, the bin containing RT has `STOP=1`;
- preceding bins have `STOP=0`;
- RT >= 2.0 s is right-censored after bin 20.

Trials with nonfinite RT are excluded and logged.

## 7. Policy models

All logistic models use:
- deterministic Newton/IRLS;
- L2 lambda = 1e-3;
- unpenalized intercept;
- zero initialization;
- max 100 iterations;
- tolerance 1e-10.

Fit **DEV subjects only**. Coefficients freeze before VAL and TEST.

### H0 — history/control model

Features:
- intercept;
- 19 time-bin indicators;
- 8 condition indicators;
- current 100-ms evidence-block sum;
- previous three 100-ms evidence-block sums, zero before available;
- signed accumulated evidence E(t).

H0 therefore receives elapsed time, experimental condition, local evidence history, and signed accumulated evidence.

### H1 — candidate model-guided policy

H1 = H0 + `M(t)=|E(t)|`.

Primary held-out policy gain:

`G_policy = LL(H1)-LL(H0)-0.5*ln(N_rows)`.

Required:
- VAL G_policy > ln(100);
- TEST G_policy > ln(100);
- DEV fitted coefficient on M is positive.

## 8. Explicit confidence-validation gate

For every trial, define stopping frame:

`tau = clip(ceil(RT*120),1,240)`.

Define:
`M_stop = |E(tau)|`.

Fit on DEV trials only two Gaussian linear models for reported `confDat.conf`.

### C0
- intercept;
- 8 condition indicators;
- RT;
- correctness;
- response side.

### C1
C0 + M_stop.

DEV residual variance for each model is frozen when evaluating VAL/TEST Gaussian log likelihood.

Confidence gain:

`G_conf = LL(C1)-LL(C0)-0.5*ln(N_trials)`.

Required:
- VAL G_conf > ln(100);
- TEST G_conf > ln(100);
- DEV M_stop coefficient positive.

If this gate fails, M is not promoted as a confidence/model state even if it predicts stopping.

## 9. Alignment-destruction controls

Run on TEST with all fitted coefficients frozen.

### D1 — policy-state alignment destruction
Within each TEST subject, condition, and time bin, deterministically permute M values among at-risk trial rows.

Recompute H1 likelihood with permuted M.

Required penalized gain over H0:
`G_policy_D1 <= 0`.

### D2 — confidence-state alignment destruction
Within each TEST subject and condition, deterministically permute M_stop across trials.

Recompute C1 likelihood against observed confidence.

Required:
`G_conf_D2 <= 0`.

Seeds derive from SHA256 of experiment ID, control, subject, condition, and time bin where applicable.

## 10. Evidence-sign representation control

Create a second complete analysis with every source evidence sequence multiplied by -1 before state construction.

Retrain DEV models and rescore VAL/TEST.

Because M is magnitude-based and response-direction variables are included only as controls, primary G_policy and G_conf must agree with the original analysis to absolute tolerance <=1e-8.

Failure is REPRESENTATION_FAIL.

## 11. Natural outcome classes

### O2_CANDIDATE_SUPPORT

All:
1. VAL and TEST policy gain > ln(100);
2. VAL and TEST confidence-validation gain > ln(100);
3. both DEV M coefficients positive;
4. D1 and D2 gains <=0;
5. evidence-sign representation control passes.

Interpretation ceiling:

> One low-dimensional accumulated-observation state both tracks explicit confidence and prospectively constrains observation quantity in held-out human subjects under the frozen model family.

This is R2 candidate evidence for model-guided observation, not O3 recursion.

### FAIL

Any required gate fails.

### UNIDENTIFIABLE

Source mapping or numerical execution cannot be completed without changing the frozen protocol.

## 12. What a PASS does not establish

Even O2_CANDIDATE_SUPPORT would not show:
- a universal Recursive Observability law;
- that confidence is the unique causal state;
- second-order self-model recursion;
- consciousness-dependent physics;
- Powerball predictability.

A successful ROX-0003A would authorize a separately frozen natural replication/transfer test under the same abstract state->policy relation.

## 13. No post-hoc repair

After scoring begins, do not change:
- subject split;
- 100-ms binning;
- evidence mapping;
- M definition;
- feature sets;
- penalties;
- ln(100) thresholds;
- destruction controls;
- representation tolerance.

A revised architecture requires a new experiment ID.

EUREKA tally remains 3.
