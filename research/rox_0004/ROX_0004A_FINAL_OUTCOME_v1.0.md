# ROX-0004A — Final Outcome v1.0

**Date:** 2026-10-05
**ROH class:** ROH-PROBE + ROH-BRIDGE
**Status:** FAIL — CLOSED LOOP NOT REPLICATED UNDER FROZEN GATES
**Classification:** LEGITIMATE NEGATIVE WITH STRONG PARTIAL NATURAL EDGE
**EUREKA:** NONE
**Cross-project EUREKA tally:** 3

## Frozen execution

- workflow run: 37310059685
- job: 111762979744
- preregistration Git blob: df8c54732dc7e47639b456cf706b3ec9990a2ccc
- scorer Git blob: 502c1b31ea204cc33d272d1228e0b18169d7da95
- qualified source artifact: 11318997318
- source artifact digest: sha256:256e8f7c8c8cfaee22276bafd0108d25227a861c9b9aae2bceca390c6b6ce066
- result SHA-256: 84ae33b25203ac39afbc14d878202bfbaa5c41fa8837ff00d90cc4375a7fb52b
- result artifact: 11345795015
- result artifact digest: sha256:8a1ce48d58904bb1dee7ecff976f6e0396d7d1da6c55075e9fe68400a5919716

## Strong replicated M -> A edge

Initial explicit confidence robustly predicted the decision to seek additional observation beyond the frozen objective/task controls in both independent experiments.

Experiment 1:
- DEV confidence coefficient: -1.4915
- VAL penalized gain: +161.5032 nats
- TEST penalized gain: +325.3699 nats
- confidence-alignment destruction TEST gain: -227.9765 nats

Experiment 2:
- DEV confidence coefficient: -1.1191
- VAL penalized gain: +234.6772 nats
- TEST penalized gain: +264.5983 nats
- confidence-alignment destruction TEST gain: -175.8818 nats

Thus lower explicit confidence prospectively predicts greater information-seeking in held-out subjects under two distinct confidence-manipulation environments, and destroying the trial-wise confidence-policy alignment reverses the evidence.

This is real natural evidence for the model-state -> observation-policy edge. It is not novel relative to the source literature and is not an EUREKA.

## Structural A -> Z edge

PASS.

The source task and the data agree exactly:
- SEEK delivers a second perceptual presentation and yields a second response/confidence;
- GIVE RESPONSE withholds the second presentation and records second response/confidence as source-missing.

There were zero structural violations.

This is task architecture, not independent ROH evidence.

## Z -> M' proxy edge

FAIL under the frozen proxy.

Experiment 1:
- VAL gain: -0.5655 nats
- TEST gain: +5.5327 nats
- destruction TEST gain: -15.1099 nats

Experiment 2:
- VAL gain: +3.1155 nats
- TEST gain: -3.9375 nats
- destruction TEST gain: -15.7594 nats

The preregistered requirement was > ln(100)=4.6052 on both VAL and TEST in both experiments. It failed.

## Representation integrity

PASS to numerical precision.

Maximum primary-gain change under consistent left/right representation flip was about 2.3e-13 nats.

## Interpretation

ROX-0004A cannot claim a replicated closed observer loop.

However, it cleanly establishes that the failure is not at the first model-guided observation edge. The M -> A edge is strong, independently replicated, held-out, representation-stable, and destroyed by alignment controls.

The weak point is the chosen Z -> M' proxy. In this source, the external second stimulus composition is largely predetermined by the initial trial construction, while the participant's stochastic internal sensory evidence is not recorded. Final response correctness / response revision is therefore an incomplete proxy for the new observation that updates confidence.

That proxy failure may not be repaired under ROX-0004A.

## Successor requirement

The next natural source should expose:
- initial confidence;
- information-seeking policy;
- whether extra information was actually sampled;
- final decision and final confidence on both seek and non-seek trials;
- preferably variable information cost and/or information content.

This permits a direct difference-in-update test rather than inferring the missing sensory sample.

ROX-0004A is closed.

EUREKA tally remains 3.
