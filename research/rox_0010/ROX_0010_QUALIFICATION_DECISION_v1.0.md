# ROX-0010 — Qualification Decision v1.0

**Date:** 2026-10-06
**Status:** SOURCE_QUALIFIED / PARKED_FOR_LOWER_LAYER_BRIDGE
**Classification:** VALID NATURAL TRAJECTORY SOURCE, INSUFFICIENT FOR DIRECT O2/O3 CLAIM
**EUREKA:** NONE
**Cross-project EUREKA tally:** 3

ROX-0010 successfully qualified raw eukaryotic chemotaxis trajectories from ChemoTrack.

The source is excellent for later tests of:
- quotient/representation transfer across chemical regimes;
- sensory-state -> migration transformation;
- trajectory-level record dependence;
- coordinate/relabeling invariance.

However, the source exposes only track identity, x/y position, and time. Chemical concentration is reconstructable from position and condition, but no intracellular model state is directly measured.

Therefore using this source now to claim a closed recursive observer would require inferring both the internal observer state and the loop from the same trajectories. That would weaken identifiability and risk turning kinematic persistence into apparent observation feedback.

Decision:
- preserve ROX-0010 as a future N1/N2/N3 lower-layer natural bridge;
- do not force it into the R5/O3 program;
- move the active program to a natural closed-loop virtual-reality dataset where neural/model state, action, and action-dependent sensory feedback are synchronously observed.

No effect scoring was performed under ROX-0010.

EUREKA tally remains 3.
