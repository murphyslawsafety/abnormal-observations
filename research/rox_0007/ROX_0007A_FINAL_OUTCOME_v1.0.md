# ROX-0007A — Final Outcome v1.0

**Date:** 2026-10-05
**ROH class:** ROH-PROBE + ROH-BRIDGE
**Status:** FAIL — ACTIVE LOOP NOT STABLE ACROSS FROZEN HELD-OUT SPLITS
**Classification:** LEGITIMATE NEGATIVE / NATURAL HUMAN LOOP TEST
**EUREKA:** NONE
**Cross-project EUREKA tally:** 3

## Frozen execution

- workflow run: 37311753683
- job: 111768583584
- preregistration Git blob: 04fc824c5173b150ffd9057cdad7d37ecf2cc8a4
- scorer Git blob: 5a4e04ad1496aeb9bb169281ad46cb5b6cf9f080
- qualified source artifact: 11345531906
- source artifact digest: sha256:36df146c48f101dfca84bb58f06084a05a287971b74dab432d42853a20a35657
- result SHA-256: 954b639abf3ba9d2039fcb0424afb454d0baa99a4c75dc4d398be0d23581c699
- result artifact: 11345657441
- result artifact digest: sha256:90749d4cbbf20a93765b95decd544ad547c18c54f443abc4e5c36cf83c830a42

## Test result

ROX-0007A failed the preregistered replication gates.

### Active model-state -> sampling edge

DEV direction was as predicted:
- confidence coefficient: +0.08719.

TEST supported the edge:
- G_FREE(TEST) = +11.8628 nats.

VAL did not:
- G_FREE(VAL) = -5.0837 nats.

### Exogenous fixed-sampling control

Confidence did not explain experimenter-assigned presentation bias:
- G_FIXED(VAL) = -3.5333;
- G_FIXED(TEST) = -4.0978.

This is qualitatively consistent with an agency-specific effect, but the active Free edge itself did not replicate in VAL.

Agency contrast:
- VAL = -1.5504 nats;
- TEST = +15.9606 nats.

### Sampling -> subsequent confidence edge

DEV direction was positive:
- allocation coefficient: +0.03911.

TEST supported the edge:
- G_UPDATE(TEST) = +8.7796 nats.

VAL did not:
- G_UPDATE(VAL) = -7.1529 nats.

Fixed exogenous allocation was nonpredictive in the diagnostic:
- VAL = -3.1460;
- TEST = -3.1560.

### Destruction controls

The frozen destruction gates failed:
- D_MA TEST = +4.8985 nats, required <=0;
- D_ZM TEST = +7.9569 nats, required <=0.

Therefore the apparent TEST signal is not specific enough under the preregistered controls.

### Representation integrity

PASS.

All left/right reflection gain differences were <=1.14e-13 nats.

## Interpretation

The experiment cannot support O2_ACTIVE_LOOP_SUPPORT.

It contains an interesting TEST-only pattern:
- active confidence -> sampling positive;
- exogenous fixed allocation nonpredictive;
- active sampling -> later confidence positive.

But the same pattern failed the independently frozen VAL subjects, and the alignment-destruction controls did not collapse the TEST gains below zero.

That pattern is preserved as exploratory only and cannot be promoted.

## Representation lesson

The repeated instability of trial-level scalar confidence/allocation tests suggests the deeper observer object may not be the trial summary:

`Conf1 -> aggregate sampling bias -> Conf2`.

A more faithful ROH probe should operate at the **observation-action microdynamics** themselves, where each observation can change the next sensing action and therefore the next observation.

ROX-0007A is closed. No threshold or split repair is allowed.

EUREKA tally remains 3.
