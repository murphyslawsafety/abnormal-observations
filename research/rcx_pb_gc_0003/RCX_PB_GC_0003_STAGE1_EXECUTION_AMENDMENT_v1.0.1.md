# RCX-PB-GC-0003 — Stage-1 Execution Amendment v1.0.1

**Date:** 2026-10-03  
**Status:** FROZEN BEFORE ANY STAGE-1 OUTCOME WAS PRODUCED  
**Reason:** computational optimization only after the first local execution attempt timed out before writing a Stage-1 result.

No scientific feature, parameter, threshold, model family, probability formula, warm-up rule, or advancement gate changes.

## A. Exact quotient-equivalence caching

The P2-I invariant scorer may cache a candidate closure score within a target/prefix for candidates that have the exact same four-pretest structural role:
- identical position-or-absence tuple across the four pretests.

For Powerball P2-I, candidates with the identical four-bit pretest-equality pattern may share the same computed closure score.

This is a mathematical memoization only. Equivalent candidates already receive identical invariant vectors and therefore identical scores. Caching must reproduce uncached probabilities to floating-point tolerance.

## B. Secondary ticket checksum deferred

The one-ticket historical checksum is secondary and cannot affect Stage-1 advancement.

To conserve compute, Stage-1 is split:

1. **Stage 1A:** run the complete O/I/C historical likelihood test, block gates, concentration gate, and robustness checks.
2. **Stage 1B:** generate the deterministic one-ticket checksum only for any plane that survives all Stage-1A gates before transfer/null promotion.

The deterministic ticket rule itself is unchanged.

If no plane survives Stage 1A, ticket generation is not run because it cannot rescue the experiment.

## C. New runner hash

Optimized local Stage-1A runner:
- filename: `rcx0003_stage1_walkforward.py`
- SHA-256: `0085e4d3672b1ca668de0a2778131e53764ac8103c48e6b0a7489a44af23669f`

This supersedes the earlier runner hash only for execution mechanics. The parent scientific specification remains controlling.
