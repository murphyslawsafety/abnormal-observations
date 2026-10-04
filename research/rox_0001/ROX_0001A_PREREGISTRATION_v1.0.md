# ROX-0001A — Recursive-Observability Meta-Compiler Synthetic Qualification

**Version:** 1.0  
**Freeze date:** 2026-10-04  
**ROH class:** ROH-CONTROL  
**Status:** PREREGISTERED BEFORE GENERATION  
**Parent normal form:** ROX-0001 Recursive Observability Normal Form v0.1  
**EUREKA status:** NONE

## 1. Purpose

ROX-0001A calibrates one specific capability required before any cross-project or Powerball use:

> Can a domain-agnostic classifier distinguish ordinary observable dynamics, retained-record dependence, and true second-order observer/model dependence from matched pseudo-recursive decoys under held-out evaluation and semantic relabeling?

This is synthetic method calibration only.

## 2. Opaque case family

Generate 12 independent opaque binary dynamical cases, four each from:

- N0 — observable dynamics only;
- N3 — record-coupled dynamics;
- N4 — recursive-observer dynamics.

Each case has 8,000 time steps, split:
- DEV 0..3999;
- VAL 4000..5999;
- TEST 6000..7999.

Case names are random hashes and class labels are hidden from the inference stage.

## 3. Common observed channels

Every case exposes five anonymously named channels after a deterministic column permutation:

- current observable bit z_t;
- intervention bit a_t;
- long-memory record scalar r_t in [-1,1];
- model/self-monitor scalar m_t in [-1,1];
- next observable bit y_t=z_{t+1}.

The inference code does not receive semantic column names. It must evaluate all admissible role assignments of the four predictor columns under the frozen model family.

## 4. Generators

Intervention:
`a_t ~ Bernoulli(0.5)`.

Base logit:
`eta0 = b0 + bz*(2z_t-1) + ba*(2a_t-1)`.

Record update:
`r_{t+1}=0.94*r_t + 0.06*(2z_t-1)`.

Model update:
`m_{t+1}=0.92*m_t + 0.08*((2y_t-1)-tanh(eta_t/2))`.

### N0
`eta_t = eta0`.

### N3
`eta_t = eta0 + br*r_t`.

### N4
`eta_t = eta0 + br*r_t + bm*m_t`.

Coefficients are drawn once per case from frozen ranges:
- b0 in [-0.3,0.3];
- |bz| in [0.5,1.0];
- |ba| in [0.4,0.9];
- |br| in [0.8,1.2] for N3/N4;
- |bm| in [0.8,1.2] for N4;
with signs set by deterministic SHA bits.

Burn-in = 500 steps and is discarded before the 8,000 recorded steps.

## 5. Matched pseudo-recursive controls

For every N4 TEST segment create a decoy by circularly shifting m_t by a deterministic nonzero offset between 137 and 863 steps while leaving z,a,r,y unchanged.

This preserves the marginal distribution and autocorrelation scale of m while breaking alignment to the actual observer/model state.

## 6. Frozen inference family

For each possible assignment of two binary-like predictor columns to roles z/a and two continuous-like columns to r/m, fit three nested logistic models on DEV:

- H0: intercept + z + a + last-8 raw z/a history bits;
- H3: H0 + r;
- H4: H3 + m.

Use deterministic Newton logistic regression with L2 lambda=1e-3, zero initialization, max 100 iterations, tolerance 1e-10.

Role assignment is chosen on DEV only by minimum H0 validation codelength on a 20% tail of DEV reserved internally for role calibration, then frozen.

No semantic column names or class labels enter fitting.

## 7. Complexity penalty

For VAL/TEST compare total predictive log loss.

Define gain:
`G3 = LL(H3)-LL(H0) - 0.5*ln(N)`
`G4 = LL(H4)-LL(H3) - 0.5*ln(N)`

where LL is held-out log likelihood and N is the number of held-out observations.

The 0.5 ln(N) penalty is frozen per added scalar parameter.

## 8. Classification

On TEST:

- classify N0 when G3<=0 and G4<=0;
- classify N3 when G3>ln(100) and G4<=0;
- classify N4 when G3>0 and G4>ln(100);
- otherwise classify UNIDENTIFIABLE.

No class is selected from training fit alone.

## 9. Frozen PASS gates

CONTROL_PASS requires:

1. at least 11/12 case classes correct;
2. every true N4 case classified N4;
3. every N4 pseudo-recursive shifted-m control has G4<=0 under the frozen fitted H4 role/model;
4. arbitrary renaming/permutation of exposed column names changes no classification;
5. mean TEST log-loss of the chosen class beats H0 for N3/N4 cases;
6. no N0 case is classified N4.

## 10. Claim boundary

PASS validates only that the ROX classifier can distinguish record dependence and second-order model-state dependence in this controlled family and reject aligned-marginal pseudo-recursion.

It is not evidence that any natural system contains N4 recursion, does not increment EUREKA, and is not evidence for Powerball predictability.
