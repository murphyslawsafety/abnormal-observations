# RCX-PB-GC-0004 — Final Outcome v1.0

**Date:** 2026-10-03  
**Status:** FAIL — NO GATE-A CANDIDATE  
**Classification:** LEGITIMATE NEGATIVE / OBSERVABILITY SCREEN  
**EUREKA:** NONE  
**Cross-project EUREKA tally:** 3

## What was tested

RCX-PB-GC-0004 asked whether the currently public Powerball physical record contains reproducible, past-only information that discriminates physical objects later selected in the draw better than chance.

The test used:
- 1,413 completed historical blocks through 2026-09-30;
- 200-block warm-up;
- 1,213 strict rolling-origin targets;
- three frozen witnesses:
  - W1 ordered current-state fingerprint;
  - W2 past same-set physical-object recurrence over 1/4/16/64 windows;
  - W3 equal-weight rank combination;
- separate white-ball and Powerball AUC statistics;
- deterministic within-set relabeling integrity control.

## Integrity

PASS.

Consistent within-set relabeling reproduced every target AUC exactly:
- maximum absolute difference: 0.0;
- tolerance: 1e-12.

## White-ball results

- W1 ordered fingerprint:
  - mean AUC = **0.5017119229**
  - block z = **0.6743**
  - positive 30-target blocks = **20/40**
  - FAIL.

- W2 same-set recurrence:
  - mean AUC = **0.5055660037**
  - block z = **1.2850**
  - positive blocks = **22/40**
  - first tercile below 0.5
  - FAIL.

- W3 combined:
  - mean AUC = **0.5059434254**
  - block z = **1.3986**
  - positive blocks = **24/40**
  - first tercile below 0.5
  - FAIL.

## Powerball results

- W1 ordered fingerprint:
  - mean AUC = **0.4910469909**
  - block z = **-1.6223**
  - FAIL.

- W2 same-set recurrence:
  - mean AUC = **0.5260511129**
  - block z = **2.9906480753**
  - positive blocks = **26/40 = 65%**
  - all three chronological terciles > 0.5
  - **FAIL because the preregistered z threshold was 3.0.**

- W3 combined:
  - mean AUC = **0.5179884584**
  - block z = **1.9475**
  - positive blocks = **21/40**
  - FAIL.

## Required stop

The preregistration required at least one Gate-A component to satisfy all:
- mean AUC > 0.5;
- block z >= 3.0;
- >=60% positive 30-target blocks;
- all three chronological terciles > 0.5;
- representation integrity pass.

No component passed all gates.

Therefore:
- no 99-replicate matched-null screen is authorized;
- no cloud workflow is launched;
- no predictive successor is authorized from RCX-PB-GC-0004;
- no live ticket experiment is authorized.

This saves cloud compute as intended.

## Important near-threshold observation

W2 Powerball recurrence was the strongest component:
- AUC = 0.52605;
- z = 2.99065;
- 65% positive blocks;
- all three terciles positive.

Because the frozen threshold was z >= 3.0, this remains a **FAIL**, not a signal promotion.

It may be preserved as an exploratory near-threshold observation, but RCX-PB-GC-0004 cannot be repaired, threshold-shifted, or null-tested after reveal.

Any follow-up must use a new experiment ID and an independent evidentiary strategy rather than reclassifying this result.

## Interpretation

Within the frozen witness family, the public record did not establish enough selected-object information to justify another exact-number predictor.

This does not prove:
- that no deeper physical state exists;
- that apparatus/regime-conditioned information is impossible;
- that additional physical measurements would be uninformative;
- that all possible representations are exhausted.

It does mean continued algebraic prediction searches on the same public variables require a scientifically distinct justification.

## Audit

- corpus SHA-256: `ffc95ec931d6c0d6ba7a92a39c4385b9a8c93e243ae8a25826c9b02e5e21048b`
- runner SHA-256: `fcf2f8163f9158747bf1ec1348626ebb29b0f8cfbfcbefc26225c4dde17bc838`
- full result SHA-256: `63964bae4777c52b3c82bb430db0802c370e9fe2ed4d41e9d2a289e0ab08b945`
- summary SHA-256: `8a122bd6c35366309a80d8ce72cfaab21a0450e51f0322629a36935a1b724da0`

EUREKA tally remains **3**.
