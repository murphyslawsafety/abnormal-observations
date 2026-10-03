# RCX-PB-GC-0003 — Stage-1 Execution Specification v1.0

**Date:** 2026-10-03  
**Status:** FROZEN BEFORE STAGE-1 WALK-FORWARD SCORING  
**Parent preregistration Git blob:** `427001ac832a56579f286a8dc84e7b1c967bd92e`  
**Historical corpus SHA-256:** `ffc95ec931d6c0d6ba7a92a39c4385b9a8c93e243ae8a25826c9b02e5e21048b`  
**Historical completed blocks:** 1413  
**First Stage-1 target:** historical block index 200 (2017-09-06)  
**Stage-1 target count:** 1213  
**EUREKA status:** NONE

This file freezes the implementation details that were intentionally left abstract in the parent preregistration. It does not alter the scientific gates.

## 1. General scoring form

All candidate probabilities are normalized within the current without-replacement risk set.

For a channel that supplies candidate log scores `s(b)`:

`P(b)=exp(s(b)-m)/sum_r exp(s(r)-m)`, where `m=max_r s(r)`.

The fair white probability at ordered extraction position `j in {0,1,2,3,4}` is `1/(69-j)`. The fair Powerball probability is `1/26`.

All categorical empirical hazard estimates use a Beta prior centered on the fair per-risk-set selection probability with frozen prior strength:

`alpha = 20`.

For feature value `v` at white position `j`:

`p_hat(v) = (S(v) + alpha*p0)/(E(v)+alpha)`

where `S` is past selected count, `E` is past candidate-exposure count, and `p0=1/(69-j)`.

The feature contribution is:

`log h(v)=log(p_hat(v)/p0)`.

Multiple frozen primitive features are combined by their arithmetic mean in log-hazard space. No feature weight is fitted or tuned.

## 2. P1 OBJECT plane

### P1-O operation channel — current physical-object transition

White candidate features:
1. `OCC`: number of the four current pretests containing candidate, 0..4.
2. `SAMEPOS`: number of current pretests containing candidate at the current official draw extraction position, 0..4.
3. `LASTPOS`: candidate position in pretest 4, encoded -1 if absent or 0..4 if present.

Each feature has its own past-only exposure/selected hazard table by draw position. P1-O log score is the mean of the three log-hazard contributions.

Powerball P1-O features:
1. `PB_OCC`: number of four pretests whose Powerball equals candidate, 0..4.
2. `PB_LAST`: 1 if pretest 4 Powerball equals candidate, else 0.

P1-O Powerball log score is their mean log hazard.

### P1-I invariant channel — persistent physical-object state

For the current ball set, examine only earlier completed blocks using that same ball-set ID.

Frozen dyadic windows:
`W={1,4,16,64}`.

For each candidate and each W:
- `n_W` = min(W, number of earlier completed blocks using this set);
- `c_W` = number of those n_W official draws containing the candidate.

White smoothed rate:

`r_W=(c_W + 4*(5/69))/(n_W+4)`.

Powerball smoothed rate:

`r_W=(c_W + 4*(1/26))/(n_W+4)`.

If `n_W=0`, the rate equals the fair rate.

P1-I candidate log score is the mean over the four windows of `log(r_W/p_fair_object)`, then normalized over the current risk set.

The smoothing strength 4 is frozen and distinct from the alpha=20 empirical-hazard prior.

## 3. P2 QUOTIENT plane

All P2 quantities are invariant to a consistent bijective relabeling of physical object identifiers.

### P2-O operation channel — anonymous relational transition

White candidate features:
1. `OCC` — as above.
2. `SAMEPOS` — as above.
3. `PREFIX_COOCCUR` — total number of same-pretest co-occurrences between candidate and all already selected official white prefix objects, summed over four pretests. At position 0 this is 0.
4. `ADJ_FWD` — number of current pretests where the immediately preceding official prefix object occurs directly before candidate. At position 0 this is 0.
5. `ADJ_REV` — number of current pretests where candidate occurs directly before the immediately preceding prefix object. At position 0 this is 0.
6. `GRAPH_DEG` — number of distinct current-pretest white objects that co-occur with candidate in at least one of the four pretest rows; 0 for an unseen candidate.
7. `ORBIT_SIZE` — number of the 69 candidate objects sharing candidate's exact current four-row incidence/position/directed-adjacency role.

Each feature uses the same past-only empirical hazard estimator. P2-O score is the mean of seven log hazards.

Powerball P2-O features:
1. exact four-bit pretest occurrence pattern, encoded as integer 0..15;
2. occurrence count 0..4.

P2-O Powerball score is their mean log hazard.

### P2-I invariant / closure channel

The closure channel is fit independently of the empirical operation hazard tables.

For each historical completed block and each white draw prefix length 1..5, construct the anonymous closure vector from four pretest rows plus that official draw prefix:

1. total unique white objects;
2-6. recurrence-multiplicity counts for multiplicities 1..5;
7-10. overlap count between the partial draw row and each of the four pretest rows;
11-14. position-preserving overlap count between the partial draw row and each pretest row, considering only draw positions already present in the prefix;
15. directed-adjacency overlap count between pretest 4 and the partial draw prefix;
16-18. anonymous co-occurrence graph degree mean, standard deviation, and maximum;
19-22. first four nonzero ordered Laplacian eigenvalues of the anonymous co-occurrence graph, zero-padded when necessary.

At each prefix length j, the past-only distribution is summarized by a running mean vector and covariance matrix of actual historical closure vectors.

Candidate invariant log score is the negative one-half Mahalanobis distance:

`s_I=-0.5*(x-mu)^T (Sigma + ridge*I)^-1 (x-mu)`.

Frozen covariance ridge:

`ridge = 1e-3`.

The log-determinant term is common to candidates within a target/position and cancels under normalization.

Powerball P2-I closure vector after appending candidate to the four pretest Powerballs:
1. candidate pretest occurrence count;
2. number of unique Powerball objects in the five-row block;
3-7. recurrence-multiplicity histogram counts for multiplicities 1..5.

The same running-mean/covariance Mahalanobis rule and ridge are used.

## 4. P3 GRAMMAR plane

P3 contains no separately fitted parameter.

P3-O is the equal-weight geometric pool of P1-O and P2-O candidate distributions.

P3-I is the equal-weight geometric pool of P1-I and P2-I candidate distributions.

P3-C is the equal-weight geometric pool of P3-O and P3-I.

For consistency, P1-C pools P1-O/P1-I and P2-C pools P2-O/P2-I with the same equal-weight geometric rule.

All pooling is performed by averaging candidate log probabilities and renormalizing.

## 5. Rolling-origin update order

The first 200 completed blocks initialize all past-only accumulators.

For target index i>=200:

1. all hazard tables, temporal object histories, and invariant running statistics contain only blocks with index < i;
2. score P1/P2/P3 for the target's four pretests and official draw;
3. generate the deterministic one-ticket checksum from P1/P2/P3 combined distributions without seeing the target outcome;
4. reveal/record target outcome for scoring;
5. update all accumulators with the completed target;
6. advance to i+1.

This update order is mandatory.

## 6. One-ticket generation

For each plane, choose the maximum combined-channel conditional-probability candidate at each white position, remove it, and continue.

For Powerball choose the maximum combined-channel probability.

Exact ties are resolved by the SHA ordering rule in the parent preregistration. Printed numerical magnitude is never a tie-breaker.

The ticket is a secondary checksum only.

## 7. Numerical rules

- natural logarithms;
- double-precision floating point;
- softmax uses max-subtraction;
- covariance inverse uses symmetric eigen-decomposition;
- covariance eigenvalues below `1e-10` after ridge addition are clipped to `1e-10` only for numerical inversion;
- relabel-invariance tolerance remains `1e-12` for probabilities;
- no target may be removed because of numerical difficulty.

If numerical execution cannot produce a normalized distribution, that plane is FAIL/UNIDENTIFIABLE for the affected execution rather than silently repaired.

## 8. Stage-1 advancement rule

The parent preregistration remains controlling.

A plane advances only if:
- O total LLR > 0;
- I total LLR > 0;
- C total LLR > 0;
- >=60% of full nonoverlapping 30-target C-LLR blocks are positive;
- no target contributes >20% of total positive C LLR;
- representation robustness passes;
- hardware/set transfer is positive or formally UNIDENTIFIABLE.

If no plane advances, RCX-PB-GC-0003 stops before null simulation.

## 9. No-repair rule

After Stage-1 scoring begins, do not change:
- feature list;
- feature encoding;
- alpha;
- temporal windows;
- smoothing strength;
- covariance vector;
- covariance ridge;
- pooling weights;
- warm-up size;
- ticket rule;
- advancement thresholds.

A later architecture requires a new experiment ID.
