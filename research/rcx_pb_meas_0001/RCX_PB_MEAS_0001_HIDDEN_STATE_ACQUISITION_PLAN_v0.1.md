# RCX-PB-MEAS-0001 — Hidden Physical-State Acquisition Plan

**Version:** 0.1 DESIGN CANDIDATE  
**Date:** 2026-10-03  
**Status:** NO MODEL / NO PREDICTION / NO CLOUD EXECUTION  
**Purpose:** identify the next scientifically distinct observability layer after repeated failures of public-record-only Powerball architectures.

## 1. Why the branch changes here

The current public Powerball corpus contains:
- date;
- machine IDs;
- ball-set IDs;
- ordered pretests;
- official draw results.

RCX-PB-GC-0001 through 0004 and the independent RCX-PB-XFER-0001 control did not establish a transferable predictive dependency from those observables.

The independent recurrence transfer was especially informative:
- the Powerball W2 near-threshold recurrence effect failed to reproduce in Texas Daily 4;
- the transferred 2014 Daily 4 mean AUC was 0.4792776003;
- block z was -3.92849;
- all four chamber means were below 0.5.

Therefore the next branch must not be another algebraic rearrangement of the same public variables.

## 2. Evidence that deeper apparatus state actually exists

Official lottery documentation states that Powerball:
- has multiple white and red ball sets;
- randomly selects the sets used for a drawing;
- changes balls when wear warrants;
- periodically weighs and X-rays the balls;
- stores balls and machines securely;
- uses them under independent-auditor supervision.

Those measurements define physical state variables that are not present in the current public pretest corpus.

This does **not** mean they predict draws. It means the existing dataset is a projection that omits known measured apparatus state.

## 3. Target hidden-state variables

### Tier A — ball physical state
Highest priority.

Per physical ball object:
- measured mass / weight;
- measurement uncertainty / tolerance;
- measurement date;
- X-ray inspection result;
- shell / density / internal-defect observations if recorded;
- surface wear / scuff / damage classification;
- diameter / roundness if recorded;
- replacement date;
- reason for replacement;
- cumulative draw / pretest use count;
- ball-set certification status.

Object key:
`(color, ball_set_id, printed_label, effective_date)`.

### Tier B — machine physical state

Per drawing machine:
- machine serial / asset identifier;
- maintenance and service dates;
- blower / air-pressure calibration;
- vacuum / extraction calibration;
- chamber service / cleaning;
- part replacement;
- calibration certificates;
- malfunction / retest history;
- machine-selection record.

### Tier C — exact event timing / procedure

Per pretest and official draw:
- timestamp to the highest recorded resolution;
- elapsed mixing time;
- extraction intervals;
- loading order;
- order and timing of machine activation;
- retest reason;
- ball-set selection timestamp;
- machine selection timestamp;
- any procedural exception.

### Tier D — environmental state

If recorded:
- room temperature;
- humidity;
- barometric pressure;
- HVAC state;
- static-control state;
- electrical supply / equipment state.

### Tier E — kinematic observation

If archived:
- high-frame-rate or original-resolution pretest video;
- official draw video with reliable frame timing;
- machine-start frame;
- ball-release frames;
- exit timing;
- visible collision / flow state.

## 4. Data acquisition priority

### Priority 1 — official records request

Request historical records from MUSL and/or member lotteries for:
1. ball weighing logs;
2. X-ray / inspection logs;
3. ball replacement / wear logs;
4. machine maintenance / calibration logs;
5. exact ball-set and machine-selection logs;
6. pretest / draw procedure logs and timestamps;
7. retest / failed-pretest records;
8. environmental logs if maintained.

Ask for machine-readable exports where possible.

Do not request proprietary source code, security credentials, access-control details, or information that could compromise physical lottery security. The scientific target is historical measured state.

### Priority 2 — audit / certification records

Seek:
- independent auditor reports;
- certification tolerances;
- test procedures;
- equipment validation records;
- public board / procurement documents specifying machine and ball tolerances.

### Priority 3 — archived video

Acquire only public or lawfully provided historical footage.

The goal is physical-state reconstruction, not interference with a live drawing.

## 5. Minimum useful acquisition

Do not restart predictive modeling merely because one new field is obtained.

A measurement source becomes scientifically usable only if it includes:

- an explicit object / machine identifier;
- timestamp or effective date;
- at least 100 completed historical draw blocks or an equivalently informative longitudinal record;
- enough repeated use of the same physical objects or machines to support held-out transfer;
- provenance strong enough to hash and freeze.

## 6. First experiment after acquisition

The first post-acquisition test is **not a lottery-ticket model**.

It asks:

> Can the richer measured physical state reconstruct or explain pretest-to-draw transformation structure better than the public-record representation?

Required architecture:
1. infer transition / generator structure from the measured physical state;
2. infer preserved invariants independently;
3. require dual reconstruction / closure;
4. report identifiability;
5. test held-out future historical blocks;
6. test wrong-machine / wrong-set / wrong-time controls;
7. compare against a public-record-only baseline;
8. freeze before any live outcome.

Only if that test passes does exact-number prediction become scientifically justified again.

## 7. Reality-Code bridge

This acquisition plan directly follows the mature Reality-Code lesson:

`excellent observable reconstruction != unique hidden realization`.

A rendered draw result may be compatible with many hidden physical states. The correct next move is therefore to expand observability, not continuously increase model complexity on the same projected state.

Imported methodology:
- generator-first recovery;
- explicit equivalence classes;
- dual operation/invariant reconstruction;
- parameter identifiability;
- scale / regime transfer;
- wrong-grammar controls.

No Reality-Code result is treated as evidence that Powerball is predictable.

## 8. LIFE-CODE bridge

The LIFE-CODE contribution is methodological only:
- hierarchy may matter;
- a flat exact dictionary can fail even when higher-level structure remains possible;
- quotient interpretations must survive prevalence and spatial / contextual controls.

Accordingly, new lottery physical measurements should be represented hierarchically:
- individual ball state;
- ball-set state;
- machine state;
- event state;
- environmental context;
- compiled draw outcome.

No biological result is imported as lottery evidence.

## 9. Stop rule

Until a genuinely new physical measurement source is obtained:

- no RCX-PB-GC-0005 public-record predictor;
- no live Powerball monitoring;
- no ticket recommendation;
- no additional null campaign;
- no cloud-heavy Powerball search.

This preserves compute for the other active LIFE-CODE / Reality-Code experiments.

## 10. Claim boundary

Current conclusion:

The tested public pretest/history representations have not produced a transferable predictive grammar.

The scientifically justified next plane is **measured apparatus state**, not further pattern search on printed outcomes.

EUREKA status: NONE.  
Master EUREKA tally remains 3.
