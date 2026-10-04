# ROX-0002A — Pre-Generation Clarification v1.0.1

**Date:** 2026-10-04
**Status:** FROZEN BEFORE ANY SYNTHETIC GENERATION OR SCORING
**Parent:** ROX_0002A_PREREGISTRATION_v1.0.md

The v1.0 generator described U_t and M_t as standardized within-case states but did not define an outcome-blind standardization rule. To prevent any full-trajectory lookahead, generator-side scaling is fixed as follows:

- `U_t = (u_t - 0.0030) / 0.0015`;
- `M_t = (m_t - 0.35) / 0.10`.

Both are clipped to [-4,4] before entering the action-policy logit.

These constants are design constants fixed before generation and are not estimated from generated trajectories.

Inference-side `u_hat` and `m_hat` remain standardized using DEV mean/SD only, exactly as preregistered.

No other generator rule, split, coefficient range, model family, penalty, classification threshold, destruction control, decoy, or PASS gate changes.
