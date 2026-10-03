# RCX-PB-GRAMMAR-0001 — Historical Partition-Grammar Stage H Design v0.1

**Date:** 2026-10-03  
**ROH class:** ROH-PROBE  
**Status:** DESIGN CANDIDATE / OUTCOME-BLIND REPRESENTATION CHOICE / NOT YET FROZEN FOR HISTORICAL SCORING

## 1. Representation correction

The synthetic control validated a persistent-object noncommutative grammar decompiler.

The outcome-blind Powerball pretest diagnostic shows that literal same-object composition across all three pretest transitions is almost always empty:
- 1410/1412 blocks have zero objects surviving P1->P2->P3->P4;
- only 2/1412 retain one such object.

Therefore the real-data grammar must not force the synthetic persistent-object ontology onto Powerball.

The natural anonymous object is instead a **set partition of observation positions**.

## 2. Observer quotient

For the 20 white-ball pretest cells, replace every physical object identifier by its first-occurrence equivalence-class symbol.

Example:

`[17,4,61,9,33] ; [4,52,17,8,12]`

becomes:

`[a,b,c,d,e] ; [b,f,a,g,h]`.

The full four-pretest prefix becomes a restricted-growth-string (RGS) partition of 20 positions.

This retains:
- equality / recurrence;
- row and extraction position;
- disappearance / reappearance;
- multiplicity;
- temporal order.

It removes:
- printed-number magnitude;
- arbitrary ball names;
- machine and set semantics from discovery.

## 3. Draw as partition extension

The official draw is represented only as an extension of the 20-cell partition.

For each draw position the production is one of:

- `NEW`: a physical object not present in any of the four pretests;
- `REF(class_role)`: an existing pretest equivalence class selected again.

An existing class role is described anonymously by:
- its four-row occurrence bit pattern;
- its extraction-position tuple with -1 for absence;
- its prior multiplicity;
- row age since last occurrence;
- whether it appeared in P4;
- its anonymous co-occurrence degree inside the four-row prefix.

Multiple unseen physical objects share the same `NEW` nonterminal but remain distinct terminals when the grammar is later compiled back to exact objects.

## 4. Grammar hierarchy

Exactly four historical grammar levels are contemplated:

### H1 — production marginal
Probability of NEW versus each anonymous existing-role family.

### H2 — ordered draw production
Condition the next draw-position production on earlier draw-position productions in the same extension.

### H3 — prefix-state grammar
Condition productions on the anonymous four-pretest partition state compressed to frozen invariants:
- multiplicity histogram;
- six pairwise row-overlap counts;
- three consecutive position-preserving overlap counts;
- unique-object count;
- role-family histogram.

### H4 — predictive-state quotient
Merge H3 prefix states only when their training-era future extension distributions are statistically indistinguishable under a frozen divergence threshold.

H4 is the Observer-Code-style behavioral quotient.

No fifth level may be added under this experiment ID.

## 5. Fair compiler baseline

The baseline is not an arbitrary frequency model.

Given a pretest prefix containing `n_seen` distinct physical objects from the current 69-object white-ball universe:

- each existing physical object has fair sequential hazard `1/(69-j)` at draw position j after removal of already selected draw objects;
- the aggregate NEW hazard is the number of currently unseen physical objects divided by the remaining universe size;
- if a role family contains multiple equivalent existing objects, its aggregate fair probability is the count of available objects in that role family divided by the remaining universe.

Thus the null compiler already accounts exactly for the combinatorics of equivalence-class multiplicity.

The learned grammar must beat this fair partition-extension compiler, not merely a flat marginal baseline.

## 6. Grammar score

Primary historical statistic will be predictive codelength improvement:

`DeltaL = log P_grammar(extension | prefix, past) - log P_fair(extension | prefix)`.

Scoring is sequential over the five draw positions.

Exact object labels are not scored in Stage H.

## 7. Grammar-first advancement

A candidate historical grammar can advance to dual reconstruction only if, under strict rolling origin:
- cumulative DeltaL > 0;
- at least 60% of full nonoverlapping 30-target blocks have positive DeltaL;
- all three chronological terciles have positive DeltaL;
- no one target contributes >20% of all positive DeltaL;
- arbitrary consistent relabeling changes no score;
- reversed / order-destroyed prefix representation performs worse by a frozen margin.

If no grammar level advances, STOP before invariant reconstruction and null campaigns.

## 8. Dual reconstruction after operation signal only

Only an advancing operation grammar receives an independent invariant channel.

Candidate invariant family will be frozen before that stage and may include:
- partition block-size spectrum;
- recurrence multiplicity histogram after completion;
- row-overlap matrix spectrum;
- rank / singular values of anonymous incidence operators;
- orbit counts under relabeling;
- order-sensitive composition statistics on role-transition operators.

The invariant channel must independently constrain the same admissible draw-extension grammar.

No predictive-only result is accepted as a recovered deeper grammar.

## 9. Rendered checksum boundary

Only after:
- operation grammar PASS;
- invariant reconstruction PASS;
- matched grammar nulls;
- nontrivial transfer / target-only sufficiency controls

may a later experiment compile the anonymous grammar back into exact-number probabilities.

No ticket is generated in Stage H.

## 10. Next freeze items

Before historical draw scoring:
1. freeze exact role-family serialization;
2. freeze H1-H4 estimators;
3. freeze H4 divergence threshold and minimum support;
4. freeze rolling-origin warm-up;
5. freeze order-destruction margin;
6. freeze MDL/search penalty across H1-H4;
7. freeze target-only and word-recombination nulls;
8. freeze code and hashes.

This design uses no draw outcome to choose the representation layer.
