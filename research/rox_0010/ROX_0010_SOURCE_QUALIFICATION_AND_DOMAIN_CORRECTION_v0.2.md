# ROX-0010 — Domain Correction and Source Qualification v0.2

**Date:** 2026-10-06
**Status:** SOURCE_QUALIFIED / PRE-SCORING CORRECTION
**ROH class:** ROH-PROBE + ROH-BRIDGE
**EUREKA status:** NONE

## 1. Domain correction before effect scoring

The v0.1 design referred to ChemoTrack as a bacterial/E. coli source.

That was incorrect.

ChemoTrack is a **eukaryotic single-cell chemotaxis / migration** dataset. The public preprint describes ~2 million measurements from ~500,000 migration tracks in precisely characterized chemoattractant gradients.

This correction is made before any ROX-0010 effect scoring and therefore changes no viewed scientific result.

The intended abstract bridge remains valid at the implementation-independent level:

`retained/sensory state -> migration action -> newly sampled chemical state -> updated retained/sensory state`.

No bacterial molecular mechanism is imported.

## 2. Qualified raw trajectory source

Official archive:
BioImage Archive / BioStudies study `S-BIAD3674`.

Public analysis repository:
`dpp98/Chemotrack--data-analysis-software`.

ROX source-qualification run:
- workflow: 37525051508;
- artifact: 11441323377;
- artifact digest: `sha256:d6969a0204fa22e3438a050f67821d137043e85ad692e66811f8c7a62ac47e55`.

Frozen qualification sample:
- 6 CSV trajectory files from `Cmin-0-Cmax-0`;
- 6 CSV trajectory files from `Cmin-0-Cmax-50nM`.

Per-row schema is identical across sampled files:
- `Nr`;
- `TID`;
- `PID`;
- `x (µm)`;
- `y (µm)`;
- `t (min)`.

Observed sampling interval is exactly 0.5 min within tracks in the qualification sample.

## 3. Qualification scale

Uniform condition sample:
- 246,794 trajectory rows;
- 3,755 tracks;
- every sampled track has at least 12 observations.

0→50 nM gradient sample:
- 238,549 trajectory rows;
- 6,546 tracks;
- every sampled track has at least 12 observations.

Across sampled files:
- maximum track length = 120 observations;
- x spans approximately 0–989 µm.

This is sufficient for subject/track-held-out temporal tests without downloading the complete archive.

## 4. Concentration map provenance

The authors' public analysis code `analysis_cei_theta.py` explicitly defines:

- `xmin = 0 µm`;
- `xmax = 1000 µm`;
- `dC/dx = (Cmax-Cmin)/(xmax-xmin)`;
- `local_conc = x*dC/dx + Cmin`.

Thus for the 0→50 nM condition:

`C(x) = 0.05 * x_µm nM`.

For the 0→0 control:

`C(x)=0`.

The concentration coordinate can therefore be reconstructed from raw x without outcome-dependent fitting.

## 5. Representation warning

The raw tracks do **not** directly observe an intracellular model state.

Therefore ROX-0010 must not label a latent history summary as a molecular belief/self-model.

The next experiment may test:
- causal/predictive equivalence of past trajectory/sensory histories;
- record-coupled migration;
- action-dependent future sampling;

but it cannot claim O3 self-model recursion from this source.

## 6. Next frozen target

ROX-0010A will test a weaker but legitimate natural bridge:

`past sensory/motion record -> migration transformation -> future sampled chemical state`

with:
- a gradient condition;
- a uniform-field control;
- track-held-out evaluation;
- coordinate-reflection invariance;
- temporal-order destruction;
- matched random-walk / history-destruction controls.

A PASS can support a nonhuman natural record-coupled active-sampling architecture.

It cannot by itself establish a recursive observer or universal ROH.

EUREKA tally remains 3.
