# RCX-PB-GC-0002H — Historical Sealed Shadow Test

**Version:** 1.0  
**Freeze date:** 2026-10-03  
**Parent model:** RCX-PB-GC-0002 fitted model v1.0  
**Status:** FROZEN BEFORE OPENING RCX-PB-GC-0001 SEALED OUTCOMES  
**EUREKA status:** NONE

## 1. Purpose

RCX-PB-GC-0002H answers the user's immediate question: can the already-frozen RCX-PB-GC-0002 relational compiler be tested now against genuinely unseen historical outcomes instead of waiting only for future live draws?

Yes. RCX-PB-GC-0001 preserved 273 observable `sealed_test` draw outcomes that were never used for RCX-PB-GC-0002 feature design, coefficient fitting, model selection, calibration scoring, or live scoring. This experiment spends that historical holdout exactly once.

RCX-PB-GC-0002H is a separate historical shadow experiment. It does **not** modify RCX-PB-GC-0002's live prospective protocol.

## 2. Why this is not identical to a future live test

The 273 sealed dates are chronologically interleaved with RCX-PB-GC-0002's 1,139 DEV+VAL training dates. Therefore the fixed v1.0 coefficients may have been estimated using nonsealed dates that occurred later in calendar time than some sealed targets.

Accordingly:
- the primary test is a valid **out-of-sample historical holdout** test of a frozen model;
- it is not described as a literal forward-in-time prediction experiment;
- the untouched live era beginning 2026-10-03 remains the independent prospective replication layer.

## 3. Frozen model

Use exactly:
- model file `RCX_PB_GC_0002_FITTED_MODEL_v1.0.json`;
- model SHA-256 `7831729fc8ba4fc385e8956961572f1e5ca8fc289c57ded77ef49fe49b441b87`;
- white coefficients:
  - 0.036658719381303634
  - -0.2682660520633799
  - -0.0014716493326463003
  - -0.011346583343222588
  - -0.0761784442374437
- Powerball coefficient:
  - 0.07030726814782846
- same features, same normalization, same fair baseline, and same scoring equations as RCX-PB-GC-0002.

No fitting, tuning, or feature changes are allowed in RCX-PB-GC-0002H.

## 4. Sealed evaluation set

Use every observable RCX-PB-GC-0001 `sealed_test` target from the qualified v0.4 corpus.

Expected:
- scheduled sealed dates = 274;
- declared source-unavailable sealed date = 2025-03-01;
- observable sealed targets = 273.

No target may be removed because of its outcome.

## 5. Reveal boundary

Before execution:
1. freeze this preregistration;
2. freeze the evaluator code and hash;
3. verify the parent model hash.

Only then may the evaluator read `vault/SEALED_TRUTH.json`.

The evaluator may emit aggregate statistics and per-date LLR contributions after reveal, but no post-reveal model change is permitted.

## 6. Primary score

For each sealed date d:

`LLR_d = log P_model(draw_d | same-day pretests) - log P_fair(draw_d)`.

Aggregate:

`LLR_total = sum_d LLR_d`.

`log10(E_total) = LLR_total / ln(10)`.

Also report:
- white-only LLR;
- PB-only LLR;
- number and fraction of dates with positive LLR;
- maximum single-date positive contribution;
- maximum single-date negative contribution;
- cumulative LLR by chronological quartile;
- nine consecutive nonoverlapping 30-target block LLRs, plus the final 3-target remainder.

## 7. Frozen interpretation classes

### HISTORICAL_SIGNAL
All:
1. `E_total >= 10,000` (LLR >= ln 10,000);
2. at least 6 of the 9 full 30-target blocks have positive LLR;
3. no single date contributes more than 25% of total positive LLR;
4. model/source/evaluator hashes verify.

### FAIL
Either:
- `E_total < 1` (LLR_total < 0); or
- integrity/hash failure.

### INCONCLUSIVE
Everything else.

These thresholds are fixed before reveal.

## 8. Claim boundary

A HISTORICAL_SIGNAL would mean only that the already-frozen relational compiler generalized to a previously untouched historical holdout better than the fair conditional baseline under the frozen scoring rule.

It would not by itself establish live predictability, a guaranteed lottery advantage, a universal Reality-Code law, or an EUREKA.

RCX-PB-GC-0002's prospective live Block A remains required for an independent future-outcome test.
