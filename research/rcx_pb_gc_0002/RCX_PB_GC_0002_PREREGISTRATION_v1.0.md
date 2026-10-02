# RCX-PB-GC-0002 — Prospective Relational-Compiler Test

**Version:** 1.0  
**Freeze date:** 2026-10-02  
**Track:** Reality-Code / Powerball physical-checksum branch  
**Status:** PREREGISTRATION — LIVE OUTCOME ERA NOT YET STARTED  
**First eligible live draw:** 2026-10-03  
**EUREKA status:** NONE

## 1. Why RCX-PB-GC-0002 exists

RCX-PB-GC-0001 closed as a legitimate negative. Its finite-state, sparse low-weight GF(2) temporal-parity, and fixed moment/low-rank families produced no grammar that survived the pre-sealed gates. Those failed families are not reopened here.

RCX-PB-GC-0002 asks a narrower and cleaner question: can one **fixed, permutation-respecting relational compiler**, estimated only from already-consumed historical outcomes, assign better prospective probability to future official Powerball draws than the fair without-replacement baseline?

This is a new experiment ID with a new untouched outcome era. RCX-PB-GC-0001's 273 observable sealed draw outcomes remain excluded from training, tuning, selection, scoring, and model repair.

## 2. Prospective scientific question

Given the four official physical pretests from a draw date, does a frozen low-complexity relational model of **object membership + extraction position + within-pretest relations** improve prospective log probability of the subsequent official draw?

Printed labels are categorical object identifiers inside a physical ball set. No numerical arithmetic on printed labels is admissible.

## 3. Authoritative source and physical ordering

Primary source:
`https://cdn.powerball.com/v01/media/powerball-pre-test.pdf`

Current game matrix:
- five white balls from 1–69 without replacement;
- one Powerball from 1–26;
- current matrix began 2015-10-07.

Each usable physical block contains four ordered `Pre-test` rows followed by one official `Draw` row. `Post-test` rows are excluded.

The RCX-PB-GC-0001 v0.4 structural parser/source-gap rules remain the ingest baseline. No outcome-dependent source repair is allowed.

## 4. Historical estimation set

Coefficient estimation may use only RCX-PB-GC-0001 dates that were already consumed before its closure:

- original deterministic `development` dates; and
- original deterministic `validation` dates.

The original RCX-PB-GC-0001 `sealed_test` draw outcomes are prohibited.

Historical estimation cutoff is 2026-09-28. The 2026-09-30 outcome is not used for coefficient estimation or model selection; it is source-interface calibration only because it was already public before this preregistration.

Expected estimation targets from the qualified v0.4 corpus:
- 878 development draw targets;
- 261 validation draw targets;
- total coefficient-estimation targets = 1,139.

## 5. Frozen relational probability model

There is exactly **one** fitted model. No architecture grid and no post-fit hyperparameter search are allowed.

### 5.1 White-ball joint distribution

The five white balls are scored sequentially with a Plackett–Luce / conditional-softmax model over the remaining physical objects.

For candidate object `b` at official extraction position `j`, define five same-day pretest relational features:

1. **UNION** — 1 if `b` appeared anywhere in the 20 white pretest cells, else 0.
2. **SAME_POS** — number of the four pretests in which `b` appeared at extraction position `j`, divided by 4.
3. **PREFIX_COOCCUR** — for `j>1`, the fraction of already selected official white objects that co-occurred with `b` in at least one same-day pretest row; 0 at `j=1`.
4. **ADJ_FWD** — for `j>1`, number of pretests in which the immediately preceding official object occurred directly before `b` in pretest extraction order, divided by 4; 0 at `j=1`.
5. **ADJ_REV** — for `j>1`, number of pretests in which `b` occurred directly before the immediately preceding official object, divided by 4; 0 at `j=1`.

Let `x_j(b)` be these five features. The conditional probability is:

`P(b_j=b | prefix, pretests) = exp(beta_W · x_j(b)) / sum_remaining exp(beta_W · x_j(r))`.

This defines a normalized probability over every ordered five-white outcome.

### 5.2 Powerball distribution

For candidate Powerball object `p`:

`PB_OCCUR(p) = (# of same-day pretests whose Powerball was p) / 4`.

`P(PB=p | pretests) = exp(beta_P * PB_OCCUR(p)) / sum_1^26 exp(beta_P * PB_OCCUR(r))`.

### 5.3 Fit rule

Fit `beta_W` (5 coefficients) and `beta_P` (1 coefficient) by penalized conditional maximum likelihood on the 1,139 authorized historical targets.

Fixed L2 penalty:
`lambda = 10`.

Total fitted scalar parameter count:
`k = 6`.

No intercept is fitted because a common conditional-softmax intercept cancels inside each risk set.

No coefficient sign constraint is imposed.

Optimization is deterministic Newton/IRLS with:
- zero initialization;
- maximum 100 iterations;
- coefficient clipping to [-8,8];
- convergence tolerance 1e-10 on maximum absolute Newton step;
- deterministic step damping if any absolute Newton step exceeds 1.

Failure to converge is `UNIDENTIFIABLE`; no alternate optimizer may be introduced inside RCX-PB-GC-0002.

## 6. Freeze before the live era

Before 2026-10-03:
1. execute the frozen fit once;
2. record all six coefficients;
3. record training-source hash;
4. hash the training code;
5. hash the fitted model JSON;
6. freeze the live scorer and its hash.

After this freeze, coefficients, features, normalization, and scoring code cannot change.

## 7. Live prospective era

Primary Block A consists of the first **30 consecutive usable scheduled Powerball draws beginning 2026-10-03**.

A date is usable only if the authoritative physical record supplies four parseable pretests and one official draw under the frozen parser. If the source omits a physical block, the date is logged `SOURCE_UNAVAILABLE` and the horizon extends until 30 usable draws are accumulated.

There is no outcome-based early stopping.

Checkpoints at 10 and 20 usable draws are descriptive only. The primary decision is at 30 usable draws.

## 8. Pre-draw publication status

The physical pretests occur before the official draw, but this experiment does not assume that MUSL publishes them publicly before the official result.

For each live date, record one of:

- `LIVE_PREDICTION_COMMITTED` — the authoritative source exposed all four pretests before the official 10:59 p.m. ET draw, and the complete model probability artifact was SHA-256 committed before the draw;
- `PROSPECTIVE_FROZEN_MODEL_ONLY` — the model was frozen before the era, but the authoritative pretest record was not publicly available early enough to commit a pre-draw probability artifact.

Only the first status supports a literal pre-draw prediction claim. Both statuses may contribute to the frozen-model prospective conditional-likelihood test because the model itself is fixed and the pretests physically precede the draw.

## 9. Primary score

For usable date `d`, let:

`LR_d = P_model(ordered five whites, PB | same-day pretests) / P_fair(ordered five whites, PB)`.

The fair baseline is:

`P_fair = 1 / [(69*68*67*66*65)*26]`.

Cumulative log likelihood ratio:

`LLR_N = sum_{d=1..N} log(LR_d)`.

Prospective e-value:

`E_N = exp(LLR_N)`.

Because the alternative distribution and scoring rule are frozen before the live outcomes, `E_N` is the primary sequential evidence statistic under the fair conditional-null model.

Numerical reporting must preserve both `LLR_N` and `log10(E_N)=LLR_N/ln(10)` to avoid overflow.

## 10. Frozen Block-A decision classes

At 30 usable draws:

### PROSPECTIVE_SIGNAL
All must hold:
1. `E_30 >= 100` (equivalently `LLR_30 >= ln(100)`);
2. each consecutive 10-draw block has positive cumulative LLR;
3. no single draw contributes more than 50% of positive total `LLR_30`;
4. source/model hashes remained unchanged;
5. no draw was removed because of its outcome.

### FAIL
Any of:
- `E_30 < 1`;
- model/source integrity failure not attributable to a declared source outage;
- any post-freeze scientific model change.

### INCONCLUSIVE
Everything else.

These classes are fixed before the live era.

## 11. Replication / EUREKA boundary

Block A cannot create an EUREKA by itself.

If Block A is `PROSPECTIVE_SIGNAL`, the exact same frozen model continues without refitting for a second independent 30-usable-draw Block B.

EUREKA review is permitted only if:
- Block A independently has `E >= 100`;
- Block B independently has `E >= 100`;
- combined `E >= 10,000`;
- both blocks satisfy the three-positive-10-draw-subblock rule;
- source integrity is intact;
- prior-art review finds the result not already explained by a known lottery/mechanical sampling artifact.

Even then, the maximum initial claim is a replicated prospective physical-dependence signal in this apparatus/process. It is not a claim that Powerball is generally predictable, that future jackpots can be guaranteed, or that Reality-Code is universally established.

## 12. Shadow diagnostics

These are secondary and cannot rescue the primary score:

1. white-only LLR;
2. PB-only LLR;
3. deterministic within-set label-permutation shadow scorer;
4. same feature model with pretest row order deterministically permuted;
5. coefficient-zero fair baseline check.

A shadow result cannot promote a failed primary result.

## 13. No-repair rule

After the first eligible live draw begins, RCX-PB-GC-0002 permits:
- bug fixes that provably do not change any previously committed probability and are versioned as operational corrections;
- source-format parser repairs only if they are outcome-blind and the old/new parse equivalence on all prior live dates is demonstrated.

It forbids:
- adding/removing features;
- changing lambda;
- refitting coefficients;
- changing the fair baseline;
- changing decision thresholds;
- excluding an unfavorable draw;
- using RCX-PB-GC-0001 sealed outcomes for repair or selection.

## 14. Relationship to RCX-PB-GC-0001

RCX-PB-GC-0001 remains closed and negative. Its untouched sealed outcomes remain untouched.

RCX-PB-GC-0002 is a distinct prospective experiment. Its evidentiary value comes from the new outcome era beginning 2026-10-03, not from recycling the prior sealed historical test set.
