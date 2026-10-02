# RCX-PB-GC-0001 — Execution Amendment v0.4

**Date frozen:** 2026-10-01
**Scope:** source-ingest/availability semantics only. v0.1 remains the controlling scientific question, admissible model families, null families, primary scores, and pass gates; v0.3 remains controlling for FWER, deterministic null seeds, model-selection objective, stability, and transfer gates.
**Status:** PRE-SCORING LOCK. This amendment is frozen before any sealed official draw outcome is opened for model discovery, selection, thresholding, or repair.

## 1. Reason
Full-corpus qualification of the official current-matrix Powerball pre-test PDF exposed typographic metadata defects and at least one absent expected event in the published source. They are source-quality problems, not evidence for the hypothesis. The pipeline must preserve them without either silently correcting them or allowing harmless typography to block the entire experiment.

## 2. Physical event blocks are primary
Execution A parses the source in printed order. An event block is the ordered sequence of all included Pre-test rows terminated by its official Draw row. Post-test rows remain excluded.

A usable block requires exactly four parseable Pre-test rows and one parseable Draw row. This criterion is applied before reading any draw outcome for scientific scoring.

## 3. Nonsemantic token normalization
For Pre-test rows only, the Power Play field may be represented by an empty field, "-", "--", or "---". All are normalized to the same missing/not-applicable token while the raw line is retained and an anomaly is logged when the source spelling differs from "--".

Date typography may be normalized only without consulting ball outcomes:
- MM/DDYY -> MM/DD/YY when uniquely calendar-valid;
- MM/DD-YY -> MM/DD/YY when uniquely calendar-valid;
- a malformed row date may inherit its block date when the other block rows and source order uniquely identify the event.

Raw date tokens are always retained.

## 4. Block-date normalization
The Draw-row date is the provisional block date when calendar-valid. If it is not an expected Powerball draw date for the frozen matrix schedule, the block may be mapped to a different date only when source order provides a unique answer: exactly one expected draw date lies strictly between the preceding and following usable block dates. The raw printed date is retained and the normalization is logged.

If individual row dates disagree with the canonical block date, they are preserved as raw metadata and normalized only at the event-index layer; no ball, machine, set, sequence, or outcome field changes.

## 5. Published-source missingness
An expected draw date with no usable official physical event block is never imputed. It is recorded as SOURCE_UNAVAILABLE and excluded symmetrically from:
- development/validation fitting;
- sealed reconstruction targets;
- forward-only evaluation;
- every matched-null replicate.

The SHA date assignment is still computed for the unavailable date and reported, so missingness cannot be hidden by the split.

A source-unavailable date is not a blocking parser error when the omission is established before scientific scoring and the same exclusion mask is frozen for all real and null executions. Instead the corpus status is QUALIFIED_WITH_SOURCE_MISSINGNESS.

This does **not** satisfy a literal complete-corpus claim. Any eventual PASS must explicitly report the coverage deficit, and the v0.1 requirement for independent held-out-era or live prospective replication remains mandatory before a high-confidence Reality-Code milestone.

## 6. Blocking conditions
Qualification still blocks scoring for:
- ambiguous event-row tokenization;
- a candidate Draw row whose type cannot be established without reading/using its outcome;
- duplicate white labels within one row;
- white/PB labels outside the matrix ranges;
- nonmonotonic/ambiguous block-date assignment;
- more than one possible expected date for a date repair;
- inconsistent split assignment inside a canonical block;
- any hidden/manual data correction.

Hardware or ball-set changes and source-unavailable blocks remain explicit audit records, never silent repairs.

## 7. Claim boundary
This amendment changes no causal hypothesis and creates no EUREKA. It is a data-quality/estimability rule frozen before scoring.
