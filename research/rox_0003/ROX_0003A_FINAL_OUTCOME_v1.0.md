# ROX-0003A — Final Outcome v1.0

**Date:** 2026-10-04
**ROH class:** ROH-PROBE
**Status:** FAIL
**Classification:** LEGITIMATE NEGATIVE / NATURAL HUMAN R2-O2 CANDIDATE TEST
**EUREKA:** NONE
**Cross-project EUREKA tally:** 3

## Frozen execution

- workflow run: 37245192297
- job: 111561579644
- preregistration Git blob: 0d64f6cfc9d44cd2c8f716e1a5d64a5c240bb696
- scorer Git blob: 693cc61675b0fbae985fb38f7a1270d4f6f8042b
- result SHA-256: f9be7e3d9ac0be5c3ecb29b485296d0f223974bc609b68c89ee8bfde6258eb51
- artifact ID: 11318354419
- artifact digest: sha256:3f8c03e0f85148183679ecbff8fd76dac6f7dce47650502821c2e5fc68e00eb1

## Frozen natural source

Balsdon & Philiastides (2024), public OSF project 5D8NH.

Frozen subject split:
- DEV: 004,016,020,023,018,008,005,025,013,006
- VAL: 021,012,003,014,024
- TEST: 007,010,015,022,011

Trials:
- DEV: 9,000
- VAL: 4,500
- TEST: 4,500

Candidate state:
`M(t)=|sum_{k<=t} e(k)|`

The state was defined before effect scoring and was intended as a deliberately simple accumulated-observation magnitude.

## Result

### Observation-policy gate

DEV M coefficient:
- **+0.0767462**

VAL:
- G_policy = **-2.4346091 nats**

TEST:
- G_policy = **-9.7067955 nats**

Both frozen held-out policy gates required G > ln(100).

Therefore the candidate M state did **not** improve held-out stopping-policy prediction beyond elapsed time, condition, current/recent evidence, and signed accumulated evidence.

### Explicit-confidence validation gate

DEV M coefficient:
- **-0.0332824**

VAL:
- G_conf = **-92.4745966 nats**

TEST:
- G_conf = **+35.3384043 nats**

The confidence state failed because:
- DEV coefficient had the wrong sign under the preregistered criterion;
- VAL was strongly negative;
- VAL and TEST did not replicate one another.

Therefore M cannot be promoted as the participant's confidence/model state under ROX-0003A.

### Destruction controls

The alignment-destruction controls behaved correctly:

- D1 policy-state destruction: **-15.0940314 nats**
- D2 confidence-state destruction: **-12.2307219 nats**

Representation control:
- flipping every evidence sign changed none of the four primary gains;
- maximum absolute gain difference = **0.0**.

These controls validate implementation/representation behavior but cannot rescue the failed natural state hypothesis.

## Interpretation

ROX-0003A falsifies the specific natural mapping:

`observer/model state = absolute signed accumulated ideal evidence`

as a cross-subject state that simultaneously tracks explicit confidence and adds held-out stopping-policy information beyond the frozen controls in this task.

This is not evidence against recursive observability in general.

It is a representation-level failure.

The task's explicit confidence is reported after the stopping decision, so ROX-0003A also had an inherent temporal limitation for a direct closed-loop test: the candidate online state was inferred rather than directly observed before policy selection.

## Successor rule

Do not repair ROX-0003A by changing the state function, subject split, threshold, or controls.

The scientifically cleaner successor is a natural paradigm where:
1. an observer/model state such as confidence is measured **before** the decision to acquire additional information;
2. that decision directly determines whether a new observation occurs;
3. the new observation is followed by an updated decision/model report.

That temporal order directly instantiates the topology calibrated by ROX-0002B:

`M_t -> A_t -> Z_{t+1} -> M_{t+1}`.

A new experiment ID is required.

## Claim boundary

No R2 support is awarded from ROX-0003A.

No EUREKA is awarded.

Powerball remains excluded from theory fitting.

Cross-project EUREKA tally remains **3**.
