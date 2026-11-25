# Technical correction and pipeline status

## Applied to the correction bundle

- Corrected the H1 coverage calculation to count only explicit false attestations; missing values are excluded.
- Corrected the archived H1 summary to 0 absent of 3 checkable Hitchiti concepts.
- Removed obsolete hash-manifest files and the script that generated them, and removed the associated freeze/timestamp claims from project documentation and code comments.
- Added scripts to retrieve pinned external datasets and run the analysis stages, including the H3 placebo table.
- Added direct Python dependencies (an install list, not a version lock).
- Reconciled counts: 6,716 forms / 64 base languages plus 83 forms / 3 addendum language records = 6,799 forms / 67 combined languages.
- Recorded the project owner's confirmation that tribal consultation has been completed and approved. APS reuse terms for Haas notebook-derived material remain a separate issue.

## Checks completed

- Python syntax compilation passed.
- Shell syntax checks passed.
- Dataset counts, H1 rows, and H3 placebo counts were checked.

## Full pipeline not executed

This execution environment lacked pycldf, lingpy, lingrex, morfessor, and igraph. Package installation failed because the environment had no network/DNS access. No new similarity grid or inferential result is claimed.

Run in a network-enabled environment:

```bash
cd analysis
python3 -m pip install -r requirements.txt
export TIMUCUA_EXT="$PWD/../external"
bash get_external_sources.sh
bash run_pipeline.sh
cd ..
./build/build.sh
```

After a successful run, record resolved dependency versions and retain the complete run log.
