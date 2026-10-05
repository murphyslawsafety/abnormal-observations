# ROX-0007 — Active-vs-Fixed Natural Observation-Loop Test

**Version:** 0.1 DESIGN CANDIDATE
**Date:** 2026-10-05
**ROH class:** ROH-PROBE + ROH-BRIDGE
**Status:** SOURCE-QUALIFICATION PHASE ONLY / NO EFFECT SCORING
**Parent synthetic control:** ROX-0002B CONTROL_PASS
**Prior natural evidence:** ROX-0004A strong replicated M->A edge, closed-loop FAIL
**EUREKA status:** NONE

## 0. Why this source

ROX-0004A established a strong held-out natural edge from explicit confidence to subsequent information-seeking policy, but the archive did not expose the stochastic sensory content needed to close the observation-update edge cleanly.

ROX-0007 uses the public data/code from:

**Kaanders, Sepulveda, Folke, Ortoleva & De Martino — "Humans actively sample evidence to support prior beliefs"**  
Public repository: `BDMLab/Kaanders_et_al_2021`.

The source is unusually well matched because Experiment 2 contains both:
- a **Free** condition in which participants actively allocate evidence sampling; and
- a **Fixed** condition in which evidence-presentation allocation is externally imposed.

Both expose:
- initial confidence `Conf1`;
- second confidence `Conf2`;
- initial/final choice and correctness;
- sampling/exposure duration variables;
- response switch/change-of-mind variables.

This allows the observer-policy edge to be tested against an explicit policy-exogenous control rather than only shuffled decoys.

## 1. Candidate natural loop

The candidate O2 loop is:

`M_t -> A_t -> Z_{t+1} -> M_{t+1}`

with:
- `M_t` = initial confidence `Conf1`;
- `A_t` = participant-controlled sampling allocation in Free trials;
- `Z_{t+1}` = evidence exposure induced by that sampling allocation;
- `M_{t+1}` = second confidence `Conf2`.

The Fixed condition is the edge-broken control for `M->A`: presentation allocation is experimenter-controlled rather than selected by the participant.

## 2. Core test principle

A true observer-policy loop should satisfy both:

1. in Free sampling, the pre-sampling model state predicts how evidence is actively sampled beyond current choice/difficulty;
2. the resulting sampling/exposure predicts the subsequent confidence update beyond the initial state;

while the corresponding model-state -> allocation edge must weaken or disappear when allocation is externally fixed.

The target is the **loop topology**, not replication of the paper's reported coefficient.

## 3. Source lock

Source repository is pinned before scoring to commit:

`2f9c697454a5e6047c4d389da135c74992f0d9f3`.

Primary files:
- `data/exp2_data_free.csv`
- `data/exp2_data_fixed.csv`
- `data/exp2_variable_definitions.docx`

Secondary architecture/discovery file, not confirmatory scoring:
- `data/exp1_main_data.csv`
- `data/exp1_variable_definitions.docx`

No model-result or prediction file from the authors is used as outcome truth.

## 4. Planned edge family

Exact numerical models are frozen only after source-schema qualification.

### E2 — confidence/model-state -> sampling policy

Free condition:
test whether `Conf1` predicts a signed sampling-bias/allocation variable after controlling for:
- initial choice;
- initial correctness;
- objective dot difference / difficulty;
- initial RT;
- block/trial/session;
- presentation-side nuisance terms where needed.

Fixed condition:
apply the same abstract edge to experimenter-assigned presentation allocation.

The Free-vs-Fixed contrast is the primary agency control.

### E3 — policy -> observation

Free sampling duration/allocation determines which evidence remains visible longer and therefore changes the observation stream.

Fixed condition provides the same exposure dimension without endogenous selection.

### E4 — observation -> updated model state

Test whether post-initial-choice sampling/exposure predicts `Conf2` / `ConfChange` beyond:
- `Conf1`;
- objective difficulty;
- initial correctness;
- response switch/change-of-mind;
- initial RT;
- session/block terms.

The decisive topology result must require both E2 and E4 under held-out participants.

## 5. Free-vs-Fixed closure control

The preferred closure statistic will be a weakest-edge score:

`L_LOOP=min(Delta_E2_free-vs-fixed, Delta_E4)`.

An active-observer interpretation requires:
- positive E2 in Free under held-out subjects;
- a materially weaker E2 under Fixed;
- positive E4 in held-out Free subjects;
- one-edge destruction controls;
- participant-held-out replication.

The exact codelength definitions and thresholds will be frozen after schema qualification and before any scoring.

## 6. Representation controls

Planned controls include:
- left/right relabeling;
- chosen/unchosen relabeling with consistent sign change;
- confidence monotone recoding where permitted;
- subject-ID removal;
- sampling-allocation time shift/permutation within matched trial strata;
- Free/Fixed label swap as a hostile control where structurally valid.

## 7. Evidence ceiling

A clean result can support **R2/O2 natural model-guided observation** and a stronger active-vs-exogenous policy contrast than ROX-0004A.

It cannot establish O3 self-model recursion, universal ROH, or Powerball predictability.

## 8. Source qualification requirements

Before scoring:
1. hash the pinned raw data files;
2. extract and archive variable-definition text;
3. verify participant counts;
4. verify the Free and Fixed files share the required temporal variables;
5. verify no target variable is reconstructed from author model outputs;
6. freeze subject splits, edge formulas, penalties, gates, and destruction controls.

No Powerball data enter ROX-0007.

EUREKA tally remains 3.
