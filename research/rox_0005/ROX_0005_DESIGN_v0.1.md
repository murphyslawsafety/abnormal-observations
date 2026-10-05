# ROX-0005 — Direct Natural Observation-Update Loop

**Version:** 0.1 DESIGN CANDIDATE  
**Date:** 2026-10-05  
**ROH class:** ROH-PROBE + ROH-BRIDGE  
**Status:** SOURCE-QUALIFICATION PHASE ONLY  
**Parent synthetic control:** ROX-0002B CONTROL_PASS  
**Prior natural result:** ROX-0004A FAIL with strong replicated M->A edge  
**EUREKA status:** NONE

## 0. Why this source

ROX-0004A showed that explicit confidence robustly predicts information seeking in held-out human subjects across two independent manipulations, but the chosen post-observation proxy was not sufficient to close the loop.

ROX-0005 requires a task where both seek and no-seek trials proceed to a final decision and final confidence report.

Preferred source:

Mohr, Ince & Benwell (2024), "Information search under uncertainty across transdiagnostic psychopathology and healthy ageing", Translational Psychiatry 14:353, public OSF project `wamgt`.

Published task architecture:
1. initial perceptual choice;
2. initial confidence;
3. opportunity to seek helpful information at an explicit cost;
4. seek -> stimulus shown again; no-seek -> matched empty display;
5. all trials proceed to final choice;
6. all trials proceed to final confidence.

This exposes the natural loop more directly:

`M_t -> A_t -> Z_{t+1} -> M_{t+1}`

with a no-information control arm on every trial.

## 1. Primary scientific target

The frozen successor must test all three empirical links without using the paper's fitted model as truth:

### E2 — M -> A
Initial confidence predicts information-seeking policy beyond objective accuracy, stimulus difficulty, cost, reward valence, age/demographic nuisance terms, and response time where available.

### E3 — A -> Z
Seeking deterministically exposes a second perceptual observation while not seeking exposes the matched empty interval.

### E4 — Z -> M'
Final confidence changes more, and in the predicted useful direction, on seek trials than on matched no-seek trials after controlling for initial confidence and initial task state.

Because final confidence exists on **both** branches, E4 can be tested as an actual information-update contrast instead of a proxy.

## 2. Stronger update target

Primary update outcome candidate:

`DeltaM = final_confidence - initial_confidence`.

Primary treatment:
`SEEK`.

A direct update model should compare:

`DeltaM ~ initial state + cost + valence + difficulty + initial correctness + SEEK`

and a richer model with the interaction:

`SEEK × initial_uncertainty`.

The exact model family and sign gates are not frozen until source schema is qualified.

Secondary, separately frozen checksum:
- improvement in final accuracy on seek versus no-seek trials conditional on initial state.

## 3. Closed-loop criterion

A later numerical preregistration must require:
- held-out M->A gain;
- task-structural A->Z integrity;
- held-out A/Z->M' gain over a no-seek baseline;
- one-edge-broken destruction controls;
- subject-held-out scoring;
- representation invariance.

The weakest indispensable edge determines the loop result.

## 4. Natural-source advantages

This dataset is especially useful because:
- N≈908, much larger than ROX-0004;
- information-seeking cost is experimentally manipulated;
- reward valence is manipulated;
- final choice and confidence are collected regardless of whether information is sought;
- seek/no-seek therefore supplies a natural matched observation/no-observation contrast.

## 5. Evidence ceiling

A clean PASS can support R2/O2 natural model-guided observation with a direct observation-update contrast.

It cannot by itself establish O3 self-model recursion or universal ROH.

O3 would require an explicit model-of-model variable or equivalent second-order state that prospectively changes observation policy beyond initial confidence and first-order state.

## 6. Source qualification

Before numerical scoring:
1. enumerate OSF `wamgt` recursively;
2. hash all candidate raw-data and analysis files;
3. identify trial-level subject IDs;
4. verify initial choice, initial confidence, seek choice, cost, reward valence, final choice, final confidence;
5. verify seek/no-seek second-presentation coding;
6. verify enough subjects for subject-held-out splits;
7. freeze a numerical preregistration and scorer.

If any core temporal variable is absent, classify SOURCE_INSUFFICIENT.

No Powerball data enter ROX-0005.

EUREKA tally remains 3.
