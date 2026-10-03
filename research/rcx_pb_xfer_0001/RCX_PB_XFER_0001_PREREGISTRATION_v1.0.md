# RCX-PB-XFER-0001 — Independent Mechanical-Lottery Recurrence Transfer Control

**Version:** 1.0  
**Freeze date:** 2026-10-03  
**Track:** Reality-Code / Powerball physical-checksum branch — independent apparatus transfer control  
**Status:** PREREGISTERED BEFORE ACCESSING THE 2013–2014 DAILY 4 MORNING OFFICIAL DRAW OUTCOMES FOR SCORING  
**EUREKA status:** NONE

## 0. Why this experiment exists

RCX-PB-GC-0004 closed as FAIL under its frozen Gate-A rule. Its strongest component was the Powerball same-set physical-object recurrence witness W2:

- mean AUC = 0.5260511129;
- block z = 2.9906480753;
- 26/40 positive 30-target blocks;
- all three chronological terciles > 0.5.

The preregistered threshold was z >= 3.0, so this result remains a FAIL and cannot be promoted or threshold-shifted.

The scientifically valid next question is therefore not to refit Powerball. It is:

> Does the exact same recurrence architecture transfer, without tuning, to an independent mechanical lottery that publicly records the ball sets used before each drawing?

Texas Daily 4 Morning is selected as the independent physical control because the Texas Lottery publicly states that:
- at least four pre-tests are conducted before every Daily 4 drawing;
- the machine uses four separate ball sets, one for each winning-number chamber;
- each chamber's ball set is tested independently;
- the machine and ball sets actually used for the drawing are explicitly marked in the pre-test record.

This is a cross-apparatus replication/control. It is not a claim that Daily 4 and Powerball use identical machinery or hidden physics.

## 1. Frozen hypothesis

The exact transferred hypothesis is:

> If the Powerball W2 near-threshold effect reflects a real ball-set-conditioned physical persistence / recurrence phenomenon rather than chance, then past official selections of physical objects from the same ball set should provide above-chance rank information for later selected objects in an independent mechanical lottery.

Only the W2 recurrence architecture is transferred.

No current-pretest digit pattern, printed-digit arithmetic, machine-specific fitted coefficient, or post-hoc feature is allowed.

## 2. Official sources

### Pre-test / apparatus source

Texas Lottery Daily 4 pre-test archive and official CSV download.

Authoritative source page:
`https://www.texaslottery.com/export/sites/lottery/Games/Daily_4/pre_test_download.html`

Daily 4 Morning pre-test CSV:
`https://www.texaslottery.com/export/sites/lottery/Games/Daily_4/daily4morningpretest.csv`

The CSV schema published by the Texas Lottery includes:
- Game Name;
- Month / Day / Year;
- Test Number;
- Machine;
- Machine Used;
- Ball Set 1..4;
- Ball Set 1..4 Used;
- alternate machine / alternate ball sets and Used indicators;
- pre-test numbers;
- re-test indicator.

### Outcome source

Texas Lottery Daily 4 Past Winning Numbers:
`https://www.texaslottery.com/export/sites/lottery/Games/Daily_4/Winning_Numbers/`

Use only the official **Morning Winning Numbers** column.

The exact downloadable winning-number endpoint may be resolved after this freeze through the official "Download All Years" link on that page. No third-party outcome source is authorized.

## 3. Time split

### Historical state initialization
Calendar year **2013**, Daily 4 Morning only.

2013 is used only to initialize past same-ball-set draw histories.

### Independent transfer evaluation
Calendar year **2014**, Daily 4 Morning only.

The 2014 official Morning outcomes are the evaluation era.

No 2014 outcome may affect:
- the recurrence formula;
- window selection;
- smoothing strength;
- scoring rule;
- pass threshold;
- null definitions.

The recurrence formula and all thresholds come from the already-frozen Powerball W2 architecture and this preregistration.

## 4. Physical identity

Daily 4 has four drawing chambers.

Each chamber is treated as its own physical-object universe:
- chamber 1: digits 0..9 in the ball set designated for Ball Set 1;
- chamber 2: digits 0..9 in Ball Set 2;
- chamber 3: digits 0..9 in Ball Set 3;
- chamber 4: digits 0..9 in Ball Set 4.

Physical object identity is:

`(chamber_id, ball_set_id, printed_digit)`.

Printed digit is categorical identity only. Its numeric magnitude is never used.

## 5. Used ball-set resolution

For each date and chamber, determine the ball set actually used for the official drawing from the Texas pre-test CSV "Used" fields.

Rules:
1. inspect all pre-test / retest rows for the date;
2. for each chamber, identify the unique ball-set ID marked as used for the drawing;
3. if exactly one used ball set is resolved for every chamber, the date is eligible;
4. if a chamber has no used set or more than one incompatible used set, classify the date as `SOURCE_AMBIGUOUS` and exclude it before looking at the official winning digits for scoring;
5. preserve every such exclusion in the source ledger.

Alternate-machine/retest rows are not collapsed into the designated-machine row. The Used indicator controls which physical ball set defines the official draw object identity.

## 6. Exact transferred recurrence score

For each evaluation date d, chamber c, used ball set s, and candidate digit b in 0..9:

Use only earlier official Morning draws from that **same chamber and same ball set**.

Frozen windows:
`W = {1,4,16,64}`.

For each W:
- `n_W` = number of available earlier same-chamber/same-set draws, capped at W;
- `c_W` = number of those draws in which candidate b was selected.

Fair object probability:
`p0 = 1/10`.

Frozen smoothing strength:
`4`.

Smoothed rate:
`r_W = (c_W + 4*p0)/(n_W + 4)`.

Candidate score:
`S(b) = mean_W log(r_W/p0)`.

No parameter is fitted.

If there is no earlier same-set history, every candidate receives the same score and the chamber AUC is 0.5.

## 7. Chamber and date AUC

For each chamber/date:
- compare the selected digit's score against the nine nonselected digits;
- pair score = 1 if selected > nonselected;
- 0.5 if tied;
- 0 if selected < nonselected;
- chamber AUC = mean over nine comparisons.

Date AUC:
`AUC_date = mean(AUC_chamber1..4)`.

Fair expectation = 0.5.

## 8. Primary actual-history transfer gate

Use all eligible 2014 Morning dates in chronological order.

Report:
- pooled mean date AUC;
- mean AUC by each of the four chambers;
- three chronological tercile means;
- nonoverlapping full **20-date** block means;
- fraction of full 20-date blocks with mean AUC > 0.5;
- block-level z:

`z = (mean(block_AUC)-0.5)/(sd(block_AUC)/sqrt(B))`.

The transfer becomes a **candidate replication** only if all are true:

1. pooled mean date AUC > 0.5;
2. block z >= 3.0;
3. >=60% of full 20-date blocks have AUC > 0.5;
4. all three chronological terciles have AUC > 0.5;
5. at least 3 of 4 chamber-specific mean AUCs are > 0.5;
6. source/provenance checks pass.

If any criterion fails, the experiment stops as FAIL and no null campaign is run.

## 9. Matched null campaign

Run only if the actual 2014 transfer becomes a candidate replication.

All nulls use the exact same 2013 initialization and 2014 scoring pipeline.

Use 999 deterministic replicates per null family.

Seed:
`int(SHA256("RCX-PB-XFER-0001|" + family + "|" + replicate)[0:16],16)`.

### N1 — fair outcome null
Replace each 2014 chamber's winning digit with an independent uniform digit 0..9, preserving dates and used ball-set schedule.

### N2 — chronology shuffle
Within each chamber, permute the observed 2014 official winning digits across eligible dates, preserving empirical digit marginals.

### N3 — ball-set schedule destruction
Within each chamber, permute the 2014 used ball-set IDs across dates while keeping official winning digits fixed.

### N4 — wrong-chamber transfer
Rotate physical histories:
- chamber 1 uses chamber 2 history;
- chamber 2 uses chamber 3 history;
- chamber 3 uses chamber 4 history;
- chamber 4 uses chamber 1 history.

Used ball-set IDs remain chamber-local; only the recurrence-history channel is rotated.

Primary null statistic:
the same pooled block-z statistic, with the sign/block/tercile/chamber gates also required.

Empirical p:
`p=(1 + #null_stat >= observed_stat)/1000`.

PASS requires:
- all four null families p <= 0.01;
- all actual-history gates remain satisfied.

## 10. Interpretation classes

### TRANSFER_SUPPORT
Actual-history gate passes and all four null families pass p <= 0.01.

Maximum claim:
the same frozen same-ball-set recurrence architecture discriminated later selected physical objects in an independent mechanical-lottery apparatus.

This would elevate the Powerball W2 near-threshold finding from isolated post-hoc curiosity to a cross-apparatus methodological signal. It would still not prove Powerball predictability.

### FAIL
Any actual-history criterion fails, or any required null p > 0.01.

Interpretation:
the Powerball W2 near-threshold result did not replicate cleanly under this independent mechanical transfer test.

### UNIDENTIFIABLE
Official source metadata cannot resolve used ball sets or 2013/2014 Morning outcomes with sufficient provenance under the frozen rules.

## 11. Powerball boundary

No Powerball model is changed by this experiment.

If TRANSFER_SUPPORT occurs:
- close this control;
- design a new Powerball experiment under a new ID;
- freeze an apparatus/ball-set recurrence model before any further Powerball scoring.

If FAIL:
- do not use W2 recurrence as justification for another Powerball predictor.

## 12. EUREKA boundary

This control cannot create an EUREKA by itself.

Even TRANSFER_SUPPORT would be a cross-apparatus methodological signal requiring independent replication and a separately frozen predictive test.

Cross-project EUREKA tally remains 3 unless a separately qualifying result occurs.
