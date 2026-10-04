# ROX-0002A — Closed Observer-Loop Synthetic Qualification

**Version:** 1.0
**Freeze date:** 2026-10-04
**ROH class:** ROH-CONTROL
**Status:** PREREGISTERED BEFORE SYNTHETIC GENERATION
**Parent:** ROX-0002 Reflexive Observation Closure Bridge v0.1
**EUREKA status:** NONE

## 1. Purpose

ROX-0002A calibrates a detector for a different object than ROX-0001A.

ROX-0001A tried to classify supplied record/model channels and failed sensitivity. ROX-0002A instead reconstructs the observer's state from the observable history itself and asks whether that reconstructed state prospectively changes the next observation policy.

The target loop is:

`observation history -> predictive state -> uncertainty / self-model state -> measurement policy -> next observation -> updated predictive state`.

This is synthetic method calibration only.

## 2. Observable process

Each opaque case exposes only, per trial:

- context symbol `c_t in {0,1,2,3}`;
- measurement-policy bit `a_t in {0,1}`;
- observed binary result `z_t in {0,1}`.

The hidden physical binary state `y_t`, generator class, latent outcome probabilities, and the generator's internal uncertainty/meta-state are not supplied to the inference stage.

If `a_t=1`, the observation channel is high fidelity:
`P(z_t=y_t)=0.95`.

If `a_t=0`, the channel is low fidelity:
`P(z_t=y_t)=0.70`.

Thus the observer's policy changes the information quality of what it observes next.

## 3. Hidden environment

There are four contexts.

For each context, a hidden Bernoulli probability is drawn from the frozen set:
`{0.20,0.35,0.65,0.80}`
under a deterministic per-case permutation.

Every 500 trials, exactly one context undergoes a deterministic complement change:
`theta -> 1-theta`,
with the changed context selected by the case seed.

This creates recurrent model mismatch and recovery periods without exposing change points to the learner.

Each case contains:
- burn-in = 500;
- recorded trials = 12,000.

Splits:
- DEV = first 6,000;
- VAL = next 3,000;
- TEST = final 3,000.

## 4. Generator-side observer model

The synthetic observer maintains decayed Beta counts independently for each context.

Initialize:
`alpha_c=beta_c=1`.

Before trial t in context c:
`p_t=alpha_c/(alpha_c+beta_c)`.

Frozen forgetting:
`rho=0.985`.

After observing z_t:
`alpha_c <- rho*alpha_c + z_t`
`beta_c <- rho*beta_c + (1-z_t)`.

Generator uncertainty:
posterior variance
`u_t = alpha_c*beta_c / ((alpha_c+beta_c)^2*(alpha_c+beta_c+1))`.

Generator self-monitor state:
`m_{t+1}=0.94*m_t + 0.06*|z_t-p_t|`.

m is initialized at 0.5.

## 5. Four generator classes

Exactly four classes, four independent cases each.

### O0 — passive policy
`P(a_t=1)=q_case`,
with q_case drawn deterministically from [0.25,0.55].
No dependence on record, uncertainty, or self-monitor state.

### O1 — record-coupled policy
`logit P(a_t=1)=b0 + b1*(2*z_{t-1}-1) + b2*I(c_t=c_{t-1})`.

No u or m dependence.

### O2 — model-guided observation
`logit P(a_t=1)=b0 + bu*U_t`,
where U_t is the standardized within-case uncertainty state.

No m dependence.

### O3 — reflexive observer
`logit P(a_t=1)=b0 + bu*U_t + bm*M_t`,
where M_t is the standardized self-monitor state.

Coefficient magnitudes:
- |b1|,|b2| in [0.7,1.1];
- |bu| in [1.2,1.8];
- |bm| in [1.2,1.8].

Signs are deterministic SHA-derived bits.

Intercept b0 is solved before generation by bisection on a 2,000-step pilot using the same environment seed so that the expected high-fidelity measurement rate lies between 0.30 and 0.50. The pilot is discarded and regenerated from the initial state with the solved intercept.

## 6. Inference-side reconstructed states

The inference stage receives only c,a,z.

It reconstructs a predictive model using the same **family**, but not hidden generator states:

- decayed Beta counts by context;
- rho = 0.985;
- p_hat before each observation;
- `u_hat` = Beta posterior variance;
- `m_hat` = EWMA absolute predictive error with decay 0.94.

These formulas are frozen because ROX-0002A is a family-calibration control. Natural-domain experiments must independently justify their state estimator.

Standardization of u_hat and m_hat uses DEV mean/SD only, then freezes for VAL/TEST.

## 7. Capacity-matched history baseline

The passive/history model H1 contains:

- intercept;
- context one-hot (3 df);
- previous 8 observation bits;
- previous 8 policy bits;
- previous 4 context-same indicators;
- current context x previous observation interactions (3 df).

No u_hat or m_hat.

This is the capacity-matched non-reflexive baseline for the synthetic family.

Nested models:

- H1: history baseline;
- H2: H1 + u_hat;
- H3: H2 + m_hat.

All are deterministic L2 logistic regressions:
- lambda = 1e-3;
- zero initialization;
- max 100 Newton iterations;
- tolerance 1e-10.

Fit on DEV only.

## 8. Held-out gains and classification

On TEST:

`G2 = LL(H2)-LL(H1)-0.5*ln(N)`.

`G3 = LL(H3)-LL(H2)-0.5*ln(N)`.

Frozen classes:

- O0/O1-family = G2<=0 and G3<=0;
- O2 = G2>ln(100) and G3<=0;
- O3 = G2>0 and G3>ln(100);
- otherwise UNIDENTIFIABLE.

O0 versus O1 is scored separately from the raw-history coefficients:
O1 requires the fitted history-only model H1 to beat an intercept+context-only comparator H0 by >ln(100) after a BIC-style 0.5*k*ln(N) penalty for the additional history terms. Otherwise classify O0.

Thus final classification is:
- if G2<=0 and G3<=0: choose O1 only if history-gain gate passes, else O0;
- if O2 rule: O2;
- if O3 rule: O3;
- else UNIDENTIFIABLE.

## 9. Reflexive destruction controls

For every true O3 case, without refitting H1/H2/H3:

1. circularly shift m_hat in TEST by a deterministic 257..997 trial offset;
2. permute m_hat within context using a deterministic seed;
3. reverse the TEST m_hat sequence.

Each control recomputes G3 using the frozen H3 coefficients.

Required:
all three control G3 values <= 0 for every true O3 case.

## 10. Policy-marginal decoy

For every O2/O3 case create a matched decoy TEST policy sequence by permuting a_t within context while preserving:
- context counts;
- policy marginals within context;
- observations z_t unchanged.

Run the frozen scoring pipeline without refit.

Required:
the decoy must not classify O2/O3.

## 11. Representation controls

Semantic renaming of contexts and policy labels must not change the final class when values are consistently relabeled and the inference reconstruction is rerun.

Required mismatch count = 0.

## 12. PASS gates

CONTROL_PASS requires all:

1. >=15/16 final classes correct;
2. all four O3 cases classified O3;
3. all four O2 cases classified O2;
4. no O0 case classified O2/O3;
5. every O3 reflexive-destruction control has G3<=0;
6. every O2/O3 policy-marginal decoy fails O2/O3 classification;
7. semantic relabeling mismatch count = 0;
8. mean TEST held-out log likelihood of the selected class exceeds H1 for true O2/O3 cases.

Any failed gate => CONTROL_FAIL.

## 13. Claim boundary

CONTROL_PASS validates only this synthetic closed-loop decompiler family.

It does not establish recursive observation in nature, does not prove the Recursive Observability Hypothesis, does not increment EUREKA, and does not authorize Powerball prediction.

EUREKA tally remains 3.
