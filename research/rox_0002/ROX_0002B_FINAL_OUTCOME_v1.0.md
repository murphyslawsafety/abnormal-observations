# ROX-0002B — Final Outcome v1.0

**Date:** 2026-10-04
**ROH class:** ROH-CONTROL
**Status:** CONTROL_PASS
**Classification:** SYNTHETIC LOOP-TOPOLOGY CALIBRATION
**EUREKA:** NONE
**Cross-project EUREKA tally:** 3

## Frozen execution

- workflow run: 37243585611
- job: 111556974494
- preregistration Git blob: 3ee3a8880568e7272c9bfed60e4cc280d5e124d2
- runner Git blob: 69a62611b5b8d1a76064bb2140fe2c613007842a
- result SHA-256: 2ff971936376090cd2ae7bb78ea72e1348c1c9848ad9fc024af68458800b1c33
- artifact ID: 11318641001
- artifact digest: sha256:d69fe43025bef443252cf4684c5dca87145ff630d98d960d3ecd41b831d88197

## Result

ROX-0002B passed every frozen gate.

- 16/16 opaque cases correctly classified.
- 4/4 intact reflexive loops classified LOOP.
- 12/12 one-edge-broken generators identified correctly.
- 0 broken-edge cases falsely classified LOOP.
- 0 representation-flip classification mismatches.
- all targeted one-edge destruction controls drove the corresponding held-out edge score below zero.
- every one-step closure shift destroyed the Z -> M' closure edge.

The four intact LOOP TEST weakest-edge scores were:
- 902.9156 nats;
- 1247.4473 nats;
- 1220.0858 nats;
- 1222.6226 nats.

For the first intact case, for example:
- M -> A edge: +1207.7514 nats;
- A -> Z edge: +1908.7316 nats;
- Z -> M' edge: +902.9156 nats.

Targeted destruction of those same edges gave:
- M -> A destroyed: -1455.2611 nats;
- A -> Z destroyed: -2894.6817 nats;
- Z -> M' destroyed: -1199.8433 nats;
- one-step closure shift: -1147.8289 nats.

The same qualitative result held in every intact-loop case.

## What this establishes

Methodologically, the frozen weakest-edge topology score can distinguish:

`model state -> observation policy -> observation -> updated model state`

from matched systems in which exactly one indispensable edge is absent.

This is a substantially better calibration target than the failed additive scalar hierarchies ROX-0001A and ROX-0002A.

## What this does not establish

This is a synthetic sufficient-state calibration.

It does not show that:
- a natural system contains the loop;
- observation is fundamental to existence;
- consciousness is required;
- the loop is universal;
- Powerball contains the loop;
- Powerball is predictable.

The next gate is R2: a real natural system must support the same closed topology under held-out tests and edge-broken controls, with its sufficient-state representation justified independently.

No EUREKA is awarded.

EUREKA tally remains 3.
