# ROX-0010 — Natural Bacterial Active-Sensing Loop Bridge

**Version:** 0.1 DESIGN CANDIDATE
**Date:** 2026-10-06
**ROH class:** ROH-PROBE + ROH-BRIDGE
**Status:** SOURCE-QUALIFICATION PHASE ONLY
**Parent control:** ROX-0002B CONTROL_PASS
**Prior natural evidence:** replicated human model-state -> information-policy edge; no natural full-loop PASS yet
**EUREKA status:** NONE

## 0. Why the domain changes

The ROX program has spent enough time inside human confidence tasks.

Those tasks are useful calibration systems, but repeated full-loop attempts have been limited by coarse trial summaries or incomplete public temporal records.

ROX-0010 deliberately moves to an unrelated natural domain:

**single-cell bacterial chemotaxis.**

This is not a metaphorical bridge. A motile bacterium:
- retains information about recent chemical observations through its sensory/adaptation network;
- changes locomotor behavior as a function of that retained state;
- locomotion changes which part of the chemical field is sampled next;
- the new chemical observation updates the retained sensory state.

The candidate natural loop is therefore:

`R_t -> A_t -> Z_{t+1} -> R_{t+1}`.

This is an R2/R3-style **record-coupled active-observation** test. It is not automatically O3 self-model recursion.

## 1. Preferred public source

ChemoTrack:
Panigrahi et al., "ChemoTrack: A comprehensive dataset linking single-cell migration trajectories to precisely defined chemotactic signals."

Public archive:
BioImage Archive study `S-BIAD3674`.

Public analysis repository:
`dpp98/Chemotrack--data-analysis-software`.

The repository provides official downloader scripts for per-condition `tracks_csv` and `tracks_json` files hosted at the EBI BioStudies archive.

## 2. Candidate loop variables

Subject to source-schema qualification:

### R_t — retained observation state
A predictive state inferred only from the cell's recent experienced concentration history and recent motion history.

The state is not called a molecular "belief" and no cognitive interpretation is imported.

Candidate history includes:
- recent local concentration sequence along the trajectory;
- temporal concentration differences;
- recent speed;
- recent heading change / run persistence.

The exact estimator must be frozen before effect scoring.

### A_t — sensing action
A trajectory-derived change in locomotor direction / run-tumble transition.

The action must be defined from kinematics before testing its relation to future concentration.

### Z_{t+1} — next observation
The chemoattractant concentration sampled at the cell's next position.

### R_{t+1} — updated retained state
The same frozen state estimator advanced by the new observation and motion sample.

## 3. Why this is cross-domain relevant

The abstract topology matches ROX-0002B without sharing implementation:

Human adaptive observation:
`confidence/model state -> information action -> observation -> updated model state`.

Bacterial chemotaxis:
`sensory-history state -> locomotor action -> sampled concentration -> updated sensory-history state`.

A cross-domain bridge can count only if the **same frozen topology logic** discriminates intact loops from edge-broken controls.

No human regression coefficient or semantic variable name is transferred.

## 4. Natural controls

The preferred source contains both gradient and uniform-concentration conditions.

At minimum source qualification should obtain:
- one no-gradient control such as `Cmin-0-Cmax-0`;
- one nonzero gradient condition such as `Cmin-0-Cmax-50nM`.

This creates a physically meaningful control:
- motion can change sampled concentration in a gradient;
- the same locomotor action cannot systematically climb a concentration field when the field is uniform.

Additional matched gradient regimes may be added only in a later frozen preregistration.

## 5. Required natural edges

A later numerical experiment must separately test:

### E_R→A — retained-state to action
Does the past-only predictive state improve held-out prediction of the next turn/run action beyond:
- current concentration alone;
- current speed;
- current heading;
- capacity-matched raw-history controls?

### E_A→Z — action to next observation
Does the realized action improve held-out prediction of the next sampled concentration beyond:
- current position/concentration;
- speed;
- local field gradient;
- a matched heading/action permutation?

### E_Z→R' — observation to state update
Does the new concentration observation improve prediction of the next retained state beyond the previous state and action?

### Closure
The intact factorization must beat every one-edge-broken decoy under held-out trajectories.

The weakest indispensable edge controls the loop score.

## 6. Identifiability and representation rules

- Arbitrary track IDs are identifiers only.
- Absolute coordinate origin must not matter.
- Reflection of the gradient axis with consistent coordinate/concentration remapping must leave classification unchanged.
- Temporal order is essential and must be attacked by time-reversal/shift controls.
- A predictive state is reported as an equivalence class if multiple histories remain observationally indistinguishable.
- No molecular receptor state is claimed unless directly measured.

## 7. Source qualification only

Before any effect scoring:

1. verify direct raw/processed trajectory access from the official archive;
2. download a small fixed sample from one uniform and one gradient condition;
3. preserve exact remote paths, file hashes, and bytes;
4. inspect track CSV/JSON schema;
5. verify a stable track/cell identifier, time/frame, x/y coordinates, and any concentration metadata or enough information to reconstruct concentration from documented field geometry;
6. verify trajectories contain enough sequential observations for held-out edge tests;
7. determine whether concentration can be mapped to position without importing outcome-dependent calibration;
8. freeze a numerical preregistration and scorer.

If concentration cannot be reconstructed with auditable provenance, classify SOURCE_INSUFFICIENT and stop.

## 8. Evidence ceiling

A clean PASS would support a natural nonhuman active-observation loop under the ROH architecture.

Because bacteria and humans are unrelated implementations, a later valid transfer using the same frozen abstract loop logic would be materially stronger than another human-task replication.

It still would not establish O3 self-model recursion or a universal law.

## 9. Powerball boundary

No Powerball data enter ROX-0010.

Powerball remains a later hostile blind checksum only after the cross-domain grammar is independently earned.

EUREKA tally remains 3.
