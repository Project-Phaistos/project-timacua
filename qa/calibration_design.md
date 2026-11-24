# Calibration benchmark design: small and localized contact layers

## Current evidence

The frozen calibration table contains five positive controls. Three are detected and two are missed. In particular, the method does not detect the documented Yuchi–Creek and Natchez–Creek cases at 33 and 38 shared concepts. This is a warning against interpreting a null Mikasuki–Timucua result as evidence that no individual words were borrowed.

The current controls are too few and too heterogeneous to estimate general sensitivity. The table also lacks a sufficiently defined gold-standard negative panel, so it cannot estimate specificity.

## Next benchmark release

Do not tune on the existing five controls and then report them as independent validation. Build a larger, literature-adjudicated panel and separate it by language pair before tuning.

### 1. Gold-standard control panel

For each pair, record:
- recipient and proposed donor;
- expected status: documented contact, no known contact, or unresolved;
- independent source citation and a short evidence note;
- number of comparable concepts and semantic domain;
- direction of transfer, where known;
- confidence and adjudicator;
- split assignment (development or held-out test).

Use qa/calibration_controls_template.csv as the blank data-entry template. Do not label a pair negative merely because a study did not discuss contact; negative controls need positive evidence for unrelatedness or a carefully justified null status.

### 2. Small-layer stress test

For every documented positive pair with enough data, repeatedly subsample shared concepts at fixed sizes (target sizes: 5, 10, 15, 20, 30, 40, and 60 where available). Preserve semantic-domain restrictions in separate strata. Keep the sampling seed and number of repetitions in the report. Do not mix the same language pair across development and held-out sets.

### 3. Report

For each sample-size and domain stratum, report:
- detection rate with binomial confidence intervals;
- false-positive rate on adjudicated negative controls;
- precision and recall where prevalence is defined by the test panel;
- permutation and maximum-rule p-values;
- number of concepts and language pairs contributing;
- failures and exclusions, not only successful detections.

### 4. Decision rule

A future null result should be interpreted only within the sample-size and semantic-domain ranges where held-out positive controls show adequate detection and negative controls show acceptable false-positive rates. Until then, the defensible claim is narrower: the current test did not detect a large Timucua-derived layer in the available lists.

## Scope

This document specifies the next experiment; it does not report a new calibration run or manufacture control examples. The template is intentionally empty pending source-backed adjudication.
