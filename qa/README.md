# Release QA and calibration audit

Run from the repository root (or any directory):

- `python qa/check_release.py` checks release integrity.
- `python qa/calibration_report.py` regenerates `qa/calibration_report.json` from the committed `cldf/tests.csv`.

The calibration audit isolates the five frozen positive-control tests. It reports the method's observed detections and misses without pretending that five selected controls estimate general sensitivity. The current table contains no sufficiently defined negative-control panel for estimating specificity. In particular, the missed Yuchi–Creek and Natchez–Creek controls show why a null result cannot rule out small or localized contact layers.

This script summarizes committed test outcomes; it does not rerun the permutation analysis. The full historical-contact pipeline remains distinct from these release and calibration checks.
