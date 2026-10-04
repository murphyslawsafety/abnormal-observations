# ROX-0001A — Pre-Generation Clarification v1.0.1

**Date:** 2026-10-04  
**Status:** FROZEN BEFORE ANY SYNTHETIC GENERATION OR SCORING  
**Parent preregistration:** ROX_0001A_PREREGISTRATION_v1.0.md

The v1.0 role-assignment sentence said the continuous r/m assignment would be selected by H0 validation codelength, but H0 does not contain either continuous channel and therefore cannot distinguish their roles.

This is corrected before generation as follows:

- the two binary-valued predictor columns are assigned to z/a in either order; because both enter symmetrically as main effects plus their own last-8 histories, choose lexicographically by exposed column index;
- among the two continuous-valued columns, fit both possible r/m assignments on the internal final 20% of DEV;
- choose the assignment with minimum H4 validation codelength;
- freeze that assignment before VAL/TEST scoring;
- all H0/H3/H4 TEST comparisons remain exactly as preregistered.

No generator, coefficient range, split, penalty, threshold, pseudo-recursive control, or PASS gate changes.
