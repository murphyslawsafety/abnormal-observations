# RCX-PB-GC-0004 — Public-Record Observability Boundary Test

**Version:** 1.0  
**Freeze date:** 2026-10-03  
**Track:** Reality-Code / Powerball physical-checksum branch  
**Status:** PREREGISTERED / LOCAL-EXECUTION ONLY UNTIL GATE A RESOLVES  
**EUREKA status:** NONE

## 0. Purpose

RCX-PB-GC-0003 showed that three global layered predictive planes failed strict rolling-origin likelihood gates, and that same-day anonymous structure leaves a large exact-object equivalence class.

RCX-PB-GC-0004 asks a more basic question before another predictive model is allowed:

> Does the currently public physical record contain reproducible, past-only information that discriminates the physical objects later selected in the draw better than chance?

This is an **observability / discriminability test**, not a ticket generator.

A FAIL means the tested public-record witnesses do not justify further exact-number prediction from the same observables. It does not prove that no deeper physical state exists.

A PASS does not authorize a live prediction. It only authorizes a new experiment ID for a regime-conditioned operator grammar.

## 1. Cross-project methodological basis

Imported from Reality-Code / Unified-Code only as methodology:
- explicit equivalence classes / quotient states;
- generator/operation-first analysis;
- identifiability separated from prediction;
- ordered transformations must be tested against order-destroyed controls;
- failed representations are preserved rather than repaired.

LIFE-CODE contributes the methodological warning that hierarchy/quotient structure must survive controls; no LIFE-CODE biological result is evidence for Powerball.

No result from another project is counted as evidence that Powerball is predictable.

## 2. Historical corpus

Canonical corpus:
- official Powerball physical pretest record;
- 5/69 + 1/26 matrix;
- 2015-10-07 through 2026-09-30;
- 1,413 usable completed four-pretest + draw blocks;
- declared source gap: 2025-03-01;
- corpus SHA-256: `ffc95ec931d6c0d6ba7a92a39c4385b9a8c93e243ae8a25826c9b02e5e21048b`.

Warm-up:
- first 200 usable completed blocks initialize past-only state;
- 1,213 eligible rolling-origin targets.

At each target, only blocks strictly earlier than the target plus that target's four pretests are available to the witness score.

## 3. Outcome representation

### White objects

The outcome for Gate A is **unordered inclusion** in the five-white draw.

For each target there are:
- 5 selected physical objects;
- 64 nonselected physical objects.

Gate A does not try to predict extraction position. Its question is whether the public observables contain information about **which objects are selected at all**.

### Powerball

One of 26 physical Powerball objects is selected.

Printed labels are categorical object identifiers inside a ball set. Numeric magnitude is never a feature or tie-breaker.

## 4. Frozen witness family

Exactly three witnesses are allowed.

### W1 — ordered current-state fingerprint

For each white candidate define the ordered four-pretest state:

`F = (p1,p2,p3,p4)`

where each `pi` is:
- -1 if the candidate is absent from pretest i;
- 0..4 for its extraction position if present.

This single categorical fingerprint contains occurrence, position, persistence, displacement, and pretest order without numerical arithmetic on the printed label.

For Powerball:

`F_PB = (e1,e2,e3,e4)`

where `ei=1` if that candidate is the Powerball in pretest i and 0 otherwise.

#### Past-only hierarchical empirical hazard

For each target candidate, W1 estimates selection probability from prior candidate exposures using three nested levels:

1. global fingerprint;
2. ball-set + fingerprint;
3. machine + ball-set + fingerprint.

Let `p0=5/69` for white inclusion and `p0=1/26` for Powerball.

Global:
`pG=(SG + a0*p0)/(EG+a0)`.

Set level:
`pS=(SS + aS*pG)/(ES+aS)`.

Machine+set level:
`pR=(SR + aR*pS)/(ER+aR)`.

Frozen pseudo-exposure strengths:
- white: `a0=aS=aR=1380` candidate exposures, equivalent to 20 full 69-object draws;
- Powerball: `a0=aS=aR=520` candidate exposures, equivalent to 20 full 26-object draws.

W1 candidate score is `logit(pR)`.

No coefficient is fitted.

### W2 — past physical-object recurrence

Within the candidate's current physical ball set, use only earlier completed blocks employing that same set.

Frozen windows:
`1,4,16,64`.

For each window W:
- `cW` = number of those prior W-or-fewer official draws selecting the candidate;
- `nW` = number of available prior blocks in the window.

Smoothed rate:
- white: `rW=(cW + 4*(5/69))/(nW+4)`;
- Powerball: `rW=(cW + 4*(1/26))/(nW+4)`.

If no prior block exists, use the fair rate.

W2 score is the arithmetic mean of the four `log(rW/p0)` values.

No parameter is fitted.

### W3 — equal-weight combined witness

Within each target, transform W1 and W2 scores independently into midranks among all candidate objects, scaled to [0,1].

W3 score is:

`W3 = 0.5*rank(W1) + 0.5*rank(W2)`.

The 0.5/0.5 weights are frozen.

## 5. Primary discriminability statistic

For a target and witness, compute pairwise AUC.

### White target AUC

For every selected white object s and nonselected object n:
- 1 if score(s) > score(n);
- 0.5 if tied;
- 0 if score(s) < score(n).

Average over the 5x64 = 320 selected/nonselected pairs.

Fair expectation = 0.5.

### Powerball target AUC

Compare the selected Powerball against each of the 25 nonselected candidates using the same 1 / 0.5 / 0 rule.

Average over 25 pairs.

Fair expectation = 0.5.

AUC is used because Gate A asks only whether the observables discriminate selected from nonselected physical objects. It does not assume a calibrated exact-ticket probability model.

## 6. Past-only update rule

For each target after warm-up:

1. all W1 hazard tables and W2 object histories contain only earlier completed blocks;
2. score all current candidate objects from the target's four pretests;
3. compute white and Powerball target AUCs from the official outcome;
4. only after scoring, update W1 exposure/selection counts and W2 histories with the completed target;
5. advance.

No future block may enter a target score.

## 7. Actual-history cheap screen

The screen is evaluated separately for:
- W1-white;
- W2-white;
- W3-white;
- W1-PB;
- W2-PB;
- W3-PB.

For each component report:
- mean target AUC;
- mean improvement `AUC-0.5`;
- chronological full 30-target block means;
- fraction of full 30-target blocks with mean AUC > 0.5;
- three chronological tercile means;
- block-level z statistic:
  `z = (mean(block_AUC)-0.5)/(sd(block_AUC)/sqrt(B))`,
  where B is the number of full nonoverlapping 30-target blocks.

A component becomes a **Gate-A candidate** only if all are true:

1. mean AUC > 0.5;
2. block-level z >= 3.0;
3. at least 60% of full 30-target blocks have mean AUC > 0.5;
4. all three chronological terciles have mean AUC > 0.5;
5. no future-leakage or representation-integrity failure.

If **no** component becomes a Gate-A candidate, RCX-PB-GC-0004 stops as FAIL and no null simulation is run.

This is intentionally conservative to avoid spending cloud resources on weak signals.

## 8. Representation-integrity controls

Before interpreting the actual-history screen:

### Consistent within-set relabeling

Apply deterministic bijective relabelings independently within each physical ball set and rerun the score.

Every target AUC must be invariant to tolerance `1e-12`.

### Serialization invariance

Changing file serialization while preserving:
- date order;
- pretest event order;
- extraction positions;
- physical set/machine identifiers

must not change scores.

Failure is an implementation FAIL.

## 9. Cheap matched-null screen

Run only if at least one actual-history component is a Gate-A candidate.

Use 99 deterministic replicates for each required null family.

The statistic is the **maximum z among the six frozen components** that also satisfies the sign/block/tercile conditions.

Null families:

N1 — fair without-replacement white outcome + fair Powerball, preserving all pretests, date, machine, and set schedules.

N2 — outcome chronology shuffle within the same white/PB ball-set regime where possible; singleton/small regimes use the nearest parent set-conditioned pool under a frozen deterministic rule.

N3 — pretest-to-draw reassignment within comparable machine+set regimes, preserving date and hardware marginals.

N4 — reverse the four pretest event order while keeping outcomes fixed.

N5 — independently permute physical-object identities between dates within each ball set, destroying persistent object state while preserving same-date pretest structure and draw marginal counts.

N6 — outcome-only permutation within ball-set regimes preserving empirical marginal object frequencies while destroying current-pretest coupling.

Deterministic seed:
`int(SHA256("RCX-PB-GC-0004|NULL|" + family + "|" + replicate)[0:16],16)`.

Per-family empirical p:
`p=(1 + #null_max_z >= observed_max_z)/100`.

All six families must have `p <= 0.05` to authorize a new successor experiment.

RCX-PB-GC-0004 itself still does not become a predictive model.

## 10. PASS / FAIL

### OBSERVABILITY_SIGNAL

All:
- at least one actual-history Gate-A candidate;
- representation-integrity controls pass;
- all six 99-replicate null families have empirical p <= 0.05.

Interpretation ceiling:
the tested public physical record contains reproducible discriminative information about later selected physical objects under the frozen witness family.

### FAIL

Any:
- no actual-history Gate-A candidate;
- representation-integrity failure;
- any required null family p > 0.05.

Interpretation:
the tested public observables / witness family do not establish reproducible selected-object information sufficient to justify another exact-number predictor from this record.

### UNIDENTIFIABLE

Required grouping/provenance prevents a valid null or target statistic without changing the frozen protocol.

## 11. Successor rule

If OBSERVABILITY_SIGNAL:
- close RCX-PB-GC-0004;
- open a new experiment ID for a regime-conditioned, order-sensitive operator grammar;
- freeze that predictive grammar independently before execution.

If FAIL:
- do not continue algebraic prediction searches on the same public variables under this branch;
- the next scientifically distinct path requires genuinely new physical observables or a separately justified measurement source.

## 12. EUREKA boundary

RCX-PB-GC-0004 cannot create an EUREKA.

A positive observability result is a methodological signal only. A predictive claim requires a separately frozen model, historical replication, matched full-pipeline nulls, and later prospective replication.

Cross-project EUREKA tally remains 3 unless an independently qualifying result occurs elsewhere.
