# Release QA

Run `python qa/check_release.py` from the repository root (or any directory).

The dependency-free check verifies the published CLDF release's declared record
counts, unique identifiers, form-to-language and form-to-concept references,
cognate-to-form references, and metadata table extents. It also checks the
published test-suite and place-name record counts.

GitHub Actions runs this check on pushes, pull requests, and manual dispatch.
It is a release-integrity check, not a re-analysis of the contact hypothesis:
a passing result does not establish that the statistical design detects every
historical contact event.
