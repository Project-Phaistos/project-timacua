# Release QA and calibration audit

Run from the repository root:

- `python qa/check_release.py` validates row counts, unique IDs, foreign keys and CLDF extents for the public data.
- `python qa/calibration_report.py` regenerates the frozen five-positive-control contact-detection summary.
- `python qa/audit_analysis_source.py` checks the archived analysis code for portability and decision-rule hazards.
- `python qa/compare_sqlite.py` compares rebuilt SQLite table contents and schema definitions with the committed database.
- `python -m unittest discover -s tests -v` tests the archival-text annotation validator.

## Contact-detection calibration

The calibration audit isolates five frozen positive-control tests. Three are detected and two are missed. The missed Yuchi–Creek and Natchez–Creek controls show why a null result cannot rule out small or localized contact layers. Five selected controls do not estimate general sensitivity, and the current table has no sufficiently defined negative-control panel for estimating specificity.

The next experiment is specified in [`calibration_design.md`](calibration_design.md), with an intentionally empty, source-backed control-entry template in [`calibration_controls_template.csv`](calibration_controls_template.csv). The template is not a dataset and contains no invented control examples.

## Archived analysis source audit

The committed machine-readable findings are in [`analysis_source_audit.json`](analysis_source_audit.json); CI regenerates the file and checks that it is unchanged.

The source audit identifies a candidate-tier inconsistency: the archived code counts five assessable criteria but requires six for the strong tier, making that branch unreachable. It also detects an environment-specific absolute fallback path for external datasets. The H1 source-check script separately corrects an archived negative count of -6 caused by bitwise inversion of an object column.

These findings are reported rather than silently rewriting scientific decisions. The strong-tier threshold requires an explicit decision about the five assessable criteria and the two criteria currently marked unassessed. The reproduction workflow sets `TIMUCUA_EXT` and restores external datasets at the exact commits recorded in `cldf/provenance.json`.

## SQLite rebuild comparison

The rebuild workflow regenerates CLDF, SQLite, wide tables and the website from the archived source package. The SQLite comparator distinguishes binary-file changes from changes to actual table contents or schema. Machine-readable source, calibration and SQLite comparison reports are published as GitHub Actions artifacts.

## Scope

These checks establish release integrity and reproducibility properties; they do not validate historical-linguistic interpretations or replace independent expert review. The complete downstream analysis rerun is a separate workflow: [`reproduce-analysis.yml`](../.github/workflows/reproduce-analysis.yml). It starts from the archived Stage 1 inputs and uses provenance-pinned external datasets.
