# ROX-0005 — Source Qualification Outcome v1.0

**Date:** 2026-10-05
**Status:** SOURCE_INSUFFICIENT
**EUREKA:** NONE

The public OSF project `wamgt` was enumerated prospectively before any ROX-0005 numerical effect scoring.

Qualified source:
- one public file: `Mohretal_2024_Data.csv`;
- SHA-256: `b035a95df8ee3d1c6096ba44e1b07863c9e03f65fe68e9d44530ad303348aaf1`;
- 908 rows;
- 27 columns.

The file is participant-level summary data, not trial-level data. It contains aggregate fields such as:
- accuracy_1 / accuracy_2;
- % trials info seeking;
- conf_increases_perc;
- meanConf1 / meanConf2;
- fitted model coefficients.

It does **not** expose the trial sequence:
`initial confidence -> seek decision -> second observation/no-observation -> final confidence`
required by the frozen ROX-0005 design.

Therefore the source cannot support the intended held-out edge/topology test without importing already-aggregated/fitted results.

ROX-0005 stops as SOURCE_INSUFFICIENT. No effect test was run and no failure of the ROH architecture is inferred.

The next source must contain raw trial-level temporal records.

EUREKA tally remains 3.
