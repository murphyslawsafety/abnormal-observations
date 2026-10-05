# ROX-0006 — Trial-Level Confidence→Information-Seeking Loop Replication

**Version:** 0.1 DESIGN CANDIDATE
**Date:** 2026-10-05
**ROH class:** ROH-PROBE + ROH-BRIDGE
**Status:** SOURCE-QUALIFICATION PHASE ONLY
**Parent synthetic control:** ROX-0002B CONTROL_PASS
**Prior natural evidence:** ROX-0004A strong replicated M->A edge; closed-loop FAIL
**EUREKA status:** NONE

## 0. Preferred source

Desender, Boldt & Yeung (2018), "Subjective Confidence Predicts Information Seeking in Decision Making", Psychological Science 29(5):761-778.

Public OSF project:
`sh3wy`.

This source is preferred because the published paradigm includes:
- a perceptual decision;
- confidence;
- free choice to sample additional information;
- forced/no-choice comparison conditions;
- final performance/confidence measures;
- an independent preregistered replication.

ROX-0006 does not treat the published statistical model as truth.

## 1. Source qualification target

Before any numerical scoring:
1. enumerate OSF sh3wy recursively;
2. identify raw trial-level files for both experiments;
3. preserve exact hashes;
4. verify subject IDs;
5. identify trial-wise initial confidence;
6. identify free/forced information-sampling condition;
7. identify actual sample/see-again choice;
8. identify final response/accuracy and final confidence;
9. identify objective stimulus-strength / variance variables;
10. freeze numerical edge models and held-out splits.

If final confidence is unavailable on both observation branches, the source may still calibrate M->A but cannot serve as the direct-loop E4 target.

## 2. Desired natural topology

`M_t -> A_t -> Z_{t+1} -> M_{t+1}`

with:
- M_t = initial confidence or an independently justified confidence proxy;
- A_t = information-seeking / see-again policy;
- Z_{t+1} = additional evidence exposure;
- M_{t+1} = final confidence / updated model state.

## 3. Strong natural contrast

If the source contains both free-choice and forced/no-choice trials, a later preregistration should use the forced condition as a matched control for the value/effect of additional observation rather than relying solely on observational seek/no-seek comparisons.

## 4. Evidence ceiling

A PASS can support R2/O2 natural closed-loop recovery and, if the second experiment transfers under the same frozen abstract edge definitions, narrow within-paradigm replication.

It is not O3, universal ROH, or Powerball evidence.

EUREKA tally remains 3.
