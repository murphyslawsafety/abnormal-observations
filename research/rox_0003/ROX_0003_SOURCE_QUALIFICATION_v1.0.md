# ROX-0003 — Natural Human Source Qualification v1.0

**Date:** 2026-10-04
**Status:** SOURCE_QUALIFIED / NO NATURAL EFFECT SCORED
**ROH class:** ROH-PROBE + ROH-BRIDGE
**Source:** Balsdon & Philiastides (2024), Nature Communications 15:9089
**OSF DOI:** 10.17605/OSF.IO/5D8NH
**EUREKA status:** NONE

## 1. Qualification outcome

PASS for source accessibility and structural sufficiency to design a held-out natural observer-policy test.

No hypothesis/effect statistic has been computed under ROX-0003.

## 2. OSF project structure

The public OSF project resolves to:
- root node 5d8nh — Perceptual efficiency in the face of volatile sensory evidence;
- child d7ea8 — Raw Data;
- child gky5a — Analysis Code.

Recursive inventory found 45 public files.

Important payloads:
- /behaviour.csv — 914,753 bytes;
- /raw_data.zip — 5,009,232,151 bytes;
- /Behaviour/behaviourAnalysis.m;
- /Behaviour/Model/preGenEvSep360.mat;
- confidence-control model fitting and simulation code;
- EEG/pupil analysis code.

Source-inventory workflow:
- run 37244162006
- job 111558618583
- artifact 11317814519
- artifact digest sha256:9e12850f032210e2a48cd9e012f5540d293e8fa006d296eb31c0e34bc96353d7

## 3. Trial-level CSV

Qualified behaviour.csv SHA-256:
`11adf1a198b057e72cd75d185fc67dad4de20c137134a4e0383dbaa68b9daed0`.

It contains:
- 18,000 rows;
- 20 subject identifiers;
- 900 trials per included subject;
- condition ID;
- starting/ending mean evidence parameters;
- starting/ending concentration parameters;
- orientation;
- response;
- correctness;
- reaction time.

The published paper independently states that the study's analyzed sample contains 20 participants.

## 4. Raw behavioral MAT subset

The 5.0-GB public archive was indexed using HTTP range access; the full archive was not downloaded.

Central-directory inventory:
- 177 members;
- 21 non-Tobii behavioral MAT files were extracted individually;
- each behavioral MAT is approximately 0.26–1.85 MB;
- large Tobii payloads were not extracted.

Behavioral-subset workflow:
- run 37244395215
- job 111559287597
- artifact 11318502746
- artifact digest sha256:02a31c027a2f7e14f4737d4bfa80b0e37b1b5ae3d780a324bb5a3330d845fe2

The main behavioral MAT schema includes:
- `data.data`: 900 x 10;
- `confDat.conf`: 1 x 900;
- `confDat.confRT`: 1 x 900;
- `p.trialInds`: 1 x 900;
- `p.trialFlips`: 900 x 240;
- source timing configuration at 120 Hz and maximum stimulus duration 2 s.

The analysis code identifies the behavioral variables as:
1. condition;
2. muStart;
3. muEnd;
4. kappaStart;
5. kappaEnd;
6. orientation;
7. response;
8. correct;
9. RT
under MATLAB indexing/comment conventions used in that code, with confidence held separately in `confDat.conf`.

The source analysis comments identify SUB-009, SUB-017, and SUB-019 as excluded for performance/technical reasons; only SUB-017 has a small non-Tobii behavioral MAT in the extracted archive subset. The prepublished/public summary CSV contains the final 20-subject analyzed cohort.

## 5. Evidence source

Qualified `preGenEvSep360.mat` SHA-256:
`c0b506e720ae6155f6132af36958cca2673e77ffbf482bb119fc4e72354fe967`.

It contains:
- `stimEv`: 180 x 2 cell array;
- `stimEvA`: 180 x 2;
- `stimEvB`: 180 x 2;
- `evVar`: 180 x 2.

Each inspected cell is a 1 x 240 double vector, matching the 120-Hz, 2-second stimulus horizon.

The authors' model-fitting code maps participant `p.trialInds` onto a 360-trial flattened evidence matrix by using the second 180-row half on alternating trials. This gives an auditable source-defined mapping from each recorded trial to its full pre-generated evidence stream.

## 6. What is observable for ROX

The archive therefore exposes enough information to build, without EEG:
- a complete trial-level evidence trajectory;
- participant stopping time / amount of evidence sampled;
- explicit post-decision confidence;
- response/correctness;
- randomized/intermixed evidence-quality condition;
- source-defined trial/evidence mapping.

This is sufficient to preregister a conservative natural test of model-state / confidence-related control of observation quantity.

It is **not** sufficient by itself to claim O3/reflexive self-model recursion, because explicit confidence is reported after the stop action and the online internal confidence state is not directly observed.

The maximum initial natural claim is therefore O2 / model-guided observation candidate evidence.

## 7. Boundary

Source qualification is not an effect test and creates no EUREKA.

No natural-data statistic may be scored until a numerical ROX-0003 preregistration and scorer are frozen.

Cross-project EUREKA tally remains 3.
