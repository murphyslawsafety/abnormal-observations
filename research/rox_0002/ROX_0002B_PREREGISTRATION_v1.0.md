# ROX-0002B — Reflexive Loop-Topology Synthetic Qualification

**Version:** 1.0
**Freeze date:** 2026-10-04
**ROH class:** ROH-CONTROL
**Status:** PREREGISTERED BEFORE GENERATION
**Parent:** ROX-0002 Reflexive Observation Closure Bridge
**EUREKA status:** NONE

## 1. Purpose

ROX-0002B tests the closed topology directly rather than forcing a scalar nesting O0 -> O1 -> O2 -> O3.

The target reflexive loop is:

`M_t -> A_t -> Z_t -> M_{t+1}`

with a contextual state `S_t` included as a matched conditioning variable.

Interpretation:
- M = observer/model state;
- A = observation/measurement policy;
- Z = resulting observation;
- M' = updated observer/model state.

A LOOP classification requires every indispensable edge to survive held-out conditional-codelength tests.

## 2. Synthetic case family

Generate 16 independent opaque binary time-series cases:

- 4 LOOP cases;
- 4 BREAK_MA cases;
- 4 BREAK_AZ cases;
- 4 BREAK_ZM cases.

Each case:
- burn-in 1,000;
- recorded length 20,000;
- DEV first 10,000;
- VAL next 5,000;
- TEST final 5,000.

All exposed binary node marginals are approximately balanced by construction.

## 3. Generator

Context state:
`S_{t+1}=S_t XOR Bernoulli(0.08)`.

For a LOOP case:

`A_t = M_t XOR S_t XOR e_A`

`Z_t = A_t XOR S_t XOR e_Z`

`M_{t+1} = M_t XOR Z_t XOR e_M`

with independent noise:
- `e_A ~ Bernoulli(p_A)`;
- `e_Z ~ Bernoulli(p_Z)`;
- `e_M ~ Bernoulli(p_M)`.

Per-case noise probabilities are drawn deterministically from [0.06,0.14].

Broken generators preserve the same remaining equations and noise ranges:

### BREAK_MA
A_t is an independent fair bit. M->A is absent.

### BREAK_AZ
Z_t is an independent fair bit. A->Z is absent.

### BREAK_ZM
M_{t+1}=M_t XOR e_M. Z->M' is absent.

Initial S and M are deterministic SHA-derived fair bits.

## 4. Exposed data

The decompiler receives only the sequence of tuples:

`(S_t,M_t,A_t,Z_t,M_{t+1})`.

Generator class labels and noise probabilities are hidden from scoring.

This control calibrates topology recovery given a candidate sufficient-state representation. It does not test state discovery.

## 5. Frozen edge models

All probabilities are estimated on DEV only with add-1 Beta/Dirichlet smoothing and frozen for VAL/TEST.

### E2 — model-to-policy
Baseline:
`P(A|S)`.

Full:
`P(A|S,M)`.

### E3 — policy-to-observation
Baseline:
`P(Z|S)`.

Full:
`P(Z|S,A)`.

### E4 — observation-to-model-update
Baseline:
`P(M'|M)`.

Full:
`P(M'|M,Z)`.

For edge e:

`Delta_e = LL_full(TEST)-LL_base(TEST)-0.5*k_e*ln(N)`

where k_e is the additional free-parameter count of the full conditional table over the baseline.

For all three edges, k_e = 2.

## 6. Loop score

`L_loop = min(Delta_E2, Delta_E3, Delta_E4)`.

This weakest-edge statistic prevents one strong relation from hiding a broken loop.

A case is classified LOOP only when:

- each Delta_e > ln(100);
- L_loop > ln(100).

Broken cases are classified by the unique missing edge if:
- the corresponding Delta_e <= 0;
- both other edges > ln(100).

Otherwise classify UNIDENTIFIABLE.

## 7. One-edge destruction controls on true LOOP TEST data

Using the frozen DEV estimators and without refit:

### D_MA
Permute TEST A values within S strata, preserving A|S marginals while breaking M->A alignment.

Required:
`Delta_E2 <= 0`.

### D_AZ
Permute TEST Z values within S strata, preserving Z|S marginals while breaking A->Z alignment.

Required:
`Delta_E3 <= 0`.

### D_ZM
Permute TEST M' values within M strata, preserving M'|M marginals while breaking Z->M' alignment.

Required:
`Delta_E4 <= 0`.

Permutation seeds are SHA-derived from case ID and edge name.

## 8. Time/order control

For each true LOOP case, also score E2/E3/E4 after reversing the TEST temporal order while keeping each row internally intact.

Because each edge is within-row, reversal alone is not expected to break them and is therefore **diagnostic only**.

The actual closure-specific order control is:

shift `M_{t+1}` by one TEST row while keeping M_t,A_t,Z_t fixed.

Required:
the shifted closure edge E4 <= 0.

## 9. Representation controls

For each case:
- flip 0<->1 independently for S, M, A, and Z;
- apply the corresponding consistent flip to M';
- rerun the frozen edge scoring from scratch.

Final class must be unchanged.

Mismatch count required = 0.

## 10. PASS gates

CONTROL_PASS requires all:

1. >=15/16 case classes correct;
2. all 4 LOOP cases classified LOOP;
3. all 12 broken-edge cases identify the correct missing edge or, at worst, one is UNIDENTIFIABLE while none is misidentified as LOOP;
4. every LOOP one-edge destruction control drives its targeted Delta_e <=0;
5. every LOOP one-step closure shift drives E4 <=0;
6. representation-flip mismatch count = 0;
7. no broken-edge case is classified LOOP.

Any failed gate => CONTROL_FAIL.

## 11. Claim boundary

A CONTROL_PASS validates only topology discrimination in this synthetic sufficient-state family.

It does not establish recursive observation in nature, does not prove ROH, does not increment EUREKA, and does not authorize Powerball prediction.

A later natural-domain experiment must independently justify/recover its sufficient-state representation before applying the topology test.

EUREKA tally remains 3.
