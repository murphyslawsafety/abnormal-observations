# RCX-PB-GC-0001 — Final Outcome

**Status:** FAIL — NO SURVIVING GRAMMAR  
**Classification:** Legitimate negative / falsification of the tested implementations  
**EUREKA:** None; master tally remains 3  
**Sealed-test truth used for search/selection/scoring:** No

## Result

The authoritative current-matrix physical corpus qualified for scoring with one declared source-unavailable block (2025-03-01): 1,412 observable physical dates out of 1,413 scheduled dates, with zero blocking corpus anomalies after the pre-scoring source-ingest amendments.

Three preregistered/closed search lines were then tested without printed-label arithmetic:

1. **Finite-memory causal-state tables:** 24 candidates; every candidate underperformed the fair baseline on chronological DEV cross-validation. Best raw result was CS_COUNT_A16 at -0.02451785785 nats/date. The family was pruned on DEV.

2. **Sparse GF(2) event-incidence parity:** all 6,195 white masks of Hamming weight 1–4 and all 15 nonzero PB masks were screened on DEV. Two globally compiled temporal candidates barely cleared the DEV MDL gate and were frozen before validation. Both failed the 261-date validation split and underperformed the fair baseline in both global and forward modes. The branch stopped before matched nulls or sealed testing.

3. **Fixed moment / low-rank temporal operators:** 36 frozen candidates spanning B1/B3/B6 moment bases, temporal ranks 1–3, and L2 penalties 0.1/1/10/100. No candidate satisfied the DEV advancement rule. The best raw global result, MOM_B1_R1_L10, was +0.0006464511 nats/date but -0.0070729641 nats/date after the frozen MDL penalty, and its first global and forward chronological folds were negative.

## Scientific conclusion

RCX-PB-GC-0001 does **not** produce a surviving Powerball grammar.

The negative result applies to the specific low-complexity representations and grammars actually searched: the finite-state family, the low-weight GF(2) event-incidence parity family with temporal compilation, and the frozen moment/low-rank temporal-operator family.

It does not prove that every possible hidden physical dependency, representation, globally constrained history, or transformation grammar is impossible. It also provides no evidence that Powerball is predictable.

Because no candidate survived the pre-sealed gates, the protocol correctly stops **before** full-pipeline matched-null testing and before opening the 273 observable sealed-test draw outcomes. The sealed historical checksum remains unspent.

## Methodological significance

The important positive result here is experimental discipline, not a physical discovery: a strong-looking DEV signal was allowed to fail cleanly on frozen validation rather than being repaired after reveal. The search was then closed by a final pre-sealed amendment instead of continuing indefinitely until something appeared to work.

Any further Powerball architecture search should receive a **new experiment ID** and a newly frozen protocol. It must not be represented as a continuation that reuses RCX-PB-GC-0001's untouched sealed outcomes after changing the search family post hoc.
