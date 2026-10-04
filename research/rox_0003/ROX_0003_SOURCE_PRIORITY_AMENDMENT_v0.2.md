# ROX-0003 — Source Priority Amendment v0.2

**Date:** 2026-10-04
**Status:** SOURCE-QUALIFICATION ONLY / FROZEN BEFORE NATURAL-DATA SCORING
**Parent:** ROX_0003_DESIGN_v0.1.md

## Priority-source correction

The 2020 Balsdon/Wyart/Mamassian archive is still scientifically relevant, but its cited OSF fork identifiers did not resolve through the current OSF API during source qualification. This is an access/provenance issue, not a scientific result.

The preferred first natural calibration source is changed, before any natural numerical scoring, to:

**Balsdon & Philiastides (2024), "Confidence control for efficient behaviour in dynamic environments", Nature Communications 15:9089. DOI 10.1038/s41467-024-53312-3. OSF project DOI 10.17605/OSF.IO/5D8NH.**

Reason for priority:
- the task explicitly studies online confidence as a control signal;
- evidence quality changes dynamically within a decision;
- stimulus presentation continues until the participant responds;
- the authors compare a confidence-control model against non-confidence-control sequential-sampling models;
- raw behavior is stated to be available in CSV and MATLAB form, alongside EEG/pupillometry and analysis code.

The ROX claim remains independent of the authors' interpretation. Their fitted model is not treated as truth.

## Frozen source-qualification rule

Before any natural scoring:
1. resolve the OSF project and enumerate the raw behavioral files;
2. hash the exact source payloads;
3. verify subject identifiers and trial/event timing are sufficient for a subject-held-out test;
4. determine whether trial-wise evidence dynamics and response/stopping policy can reconstruct the candidate loop without importing fitted latent labels;
5. freeze a numerical preregistration and scorer.

If the public archive does not expose the variables required for the closed-loop topology, classify this source as SOURCE_INSUFFICIENT and move to the next preregistered natural candidate. Do not infer missing trial structure from the paper alone.

No natural-domain result is created by this amendment.
