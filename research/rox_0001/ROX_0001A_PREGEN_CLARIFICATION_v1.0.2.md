# ROX-0001A — Pre-Generation Clarification v1.0.2

**Date:** 2026-10-04  
**Status:** FROZEN BEFORE ANY SYNTHETIC GENERATION OR SCORING  
**Supersedes:** v1.0.1 continuous-channel tie rule only

The two continuous channels both appear in H4, so H4 codelength alone cannot identify which should enter first as the record channel.

Before VAL/TEST, using only the internal final 20% of DEV:

1. fit H0;
2. separately fit H0+c0 and H0+c1;
3. assign as `r` the continuous channel giving the larger penalized held-out gain over H0;
4. assign the other channel as `m`;
5. break an exact tie by exposed column index;
6. freeze this assignment for all VAL/TEST scoring and pseudo-recursive controls.

This makes the nested comparison operationally identifiable without semantic labels.

All generator rules, splits, penalties, class thresholds, pseudo-recursive controls, and PASS gates remain unchanged.
