# RCX-PB-XFER-0001 — Final Outcome v1.0

**Date:** 2026-10-03  
**Status:** FAIL — INDEPENDENT RECURRENCE TRANSFER DID NOT REPLICATE  
**Classification:** LEGITIMATE NEGATIVE / CROSS-APPARATUS CONTROL  
**EUREKA:** NONE  
**Cross-project EUREKA tally:** 3

## Purpose

RCX-PB-GC-0004 produced a near-threshold but formally failed Powerball recurrence component:
- W2 Powerball mean AUC = 0.5260511129;
- block z = 2.9906480753 versus frozen requirement z >= 3.0;
- 26/40 positive blocks;
- all three chronological terciles positive.

RCX-PB-XFER-0001 froze the exact same recurrence architecture and transferred it, without tuning, to an independent mechanical lottery: Texas Daily 4 Morning.

The independent apparatus is useful because the Texas Lottery publishes the actual ball set used in each of four drawing chambers and conducts at least four pre-tests before every drawing.

## Frozen transfer

Physical identity:
`(chamber_id, ball_set_id, digit)`.

Transferred score:
- same physical ball set;
- same chamber;
- prior official selections only;
- windows 1/4/16/64;
- smoothing strength 4;
- fair object probability 1/10;
- no fitted coefficient.

2013 initialized the same-set history.
2014 was the untouched evaluation era for this transfer.

## Source qualification

Official Texas source hashes:
- Daily 4 Morning pre-test CSV SHA-256:
  `6da5a5e2c3c5db14108728da3558b23a69806563b008e5fcd7292886394ca08a`
- Daily 4 Morning winning-number CSV SHA-256:
  `6da25276edac5da7c1aece3db1c145a8b377be9b2821eaf2731124d4e9a5c090`

Coverage:
- 98 initialization dates in 2013;
- 313 evaluation dates in 2014;
- 0 missing outcome/pretest date mismatches;
- 0 ambiguous used-ball-set dates;
- relabeling integrity reproduced every AUC exactly.

## Result

The transferred recurrence hypothesis failed strongly.

Pooled 2014 date-level result:
- mean AUC = **0.4792776003**
- improvement over fair 0.5 = **-0.0207223997**
- block z = **-3.9284922236**
- positive full 20-date blocks = **3/15 = 20%**

Chamber-specific mean AUC:
1. **0.4840255591**
2. **0.4889953852**
3. **0.4511892084**
4. **0.4929002485**

Chronological terciles:
1. **0.4751322751**
2. **0.5024038462**
3. **0.4603365385**

Every chamber was below 0.5 overall.

The preregistered actual-history transfer gate therefore failed before any null campaign.

## Required stop

Because the independent transfer was not a candidate replication:
- no 999-replicate null campaign is run;
- no cloud-heavy follow-up is authorized;
- the Powerball W2 near-threshold observation is **not** promoted as evidence of a generic mechanical recurrence effect;
- W2 recurrence cannot justify a new Powerball predictor.

## Interpretation

This independent failure substantially weakens the hypothesis that the RCX-PB-GC-0004 W2 near-threshold result represented a transferable same-ball-set physical recurrence law.

The Powerball near-miss remains what its original frozen protocol said it was: a FAIL.

The cross-apparatus result does not prove that all lottery apparatus dynamics are memoryless, nor that no hidden physical state exists. It does indicate that repeated selection history alone is not a reliable generic mechanical-lottery state variable under the tested architecture.

The next Powerball step should therefore not be another transformation of the same public number/pretest record.

A scientifically distinct continuation requires **new physical observables**: e.g. measured ball properties, wear state, actual ball-set inspection data, machine calibration state, environmental state, exact timing/kinematics, or equivalent independently obtained apparatus measurements.

## Audit

- preregistration frozen before evaluation scoring;
- runner SHA-256:
  `aca21e38395c43fa61d4e2e3c7203cf3c0f3dd66d6c8c51e434bdbbc134f3250`
- full result SHA-256:
  `e81bc7f910021bfe373351c51530bd69a6a982e6f7b9cdb33b1dd2cd5666f84b`
- summary SHA-256:
  `a116577e8ecc2929c3d4a94ad7d3ba29acb46c7c40cc76cec998db16acd5b98b`

EUREKA tally remains **3**.
