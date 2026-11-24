#!/usr/bin/env python3
"""Audit known portability and decision-rule hazards in analysis_all.zip."""
import hashlib
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "analysis_all.zip"
OUTPUT = ROOT / "qa/analysis_source_audit.json"


def main():
    digest = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
    with zipfile.ZipFile(ARCHIVE) as archive:
        names = set(archive.namelist())
        required = ("analysis/src/07_run_workstream_b.py", "analysis/src/common.py",
                    "analysis/src/12_haas1937_boynton_checks.py")
        missing = [name for name in required if name not in names]
        if missing:
            raise SystemExit(f"Missing expected source files in archive: {missing}")
        workstream = archive.read(required[0]).decode("utf-8")
        common = archive.read(required[1]).decode("utf-8")
        source_check = archive.read(required[2]).decode("utf-8")

    denominator = re.search(r'criteria_met_of_(\d+)_assessable', workstream)
    threshold = re.search(r'met\s*>=\s*(\d+)', workstream)
    if not denominator or not threshold:
        raise SystemExit("Could not locate candidate criteria denominator and strong-tier threshold.")
    n_assessable, required_met = int(denominator.group(1)), int(threshold.group(1))
    findings = [{
        "id": "timucua-strong-tier-threshold",
        "severity": "high" if required_met > n_assessable else "info",
        "source": required[0],
        "assessable_criteria": n_assessable,
        "strong_tier_threshold": required_met,
        "unreachable": required_met > n_assessable,
        "finding": (
            f"The code counts {n_assessable} assessable criteria but requires {required_met} "
            "for the strong tier. That branch is unreachable; no candidate can receive this tier."
            if required_met > n_assessable else
            "The strong-tier threshold does not exceed the assessable-criteria count."
        ),
        "recommended_resolution": (
            "Decide and document whether strong requires all assessable criteria or whether "
            "additional criteria must be adjudicated. Do not silently lower the threshold: "
            "C5/C6 are explicitly unassessed and this is a scientific decision."
        ),
    }]
    hardcoded = re.search(r'"/tmp/claude-[^"]+"', common)
    findings.append({
        "id": "timucua-external-data-path",
        "severity": "medium" if hardcoded else "info",
        "source": required[1],
        "hardcoded_fallback_path_present": bool(hardcoded),
        "finding": (
            "The source embeds an environment-specific absolute fallback for external datasets. "
            "The pipeline is portable only when TIMUCUA_EXT is explicitly set."
            if hardcoded else "No environment-specific absolute fallback was found."
        ),
        "recommended_resolution": "Use a repository-relative default while retaining TIMUCUA_EXT override.",
    })
    h1_bug = "absent_from_hitchiti" in source_check and "frozen script applied ~" in source_check
    findings.append({
        "id": "timucua-h1-count-correction",
        "severity": "info",
        "source": required[2],
        "separate_corrected_count_present": h1_bug,
        "finding": (
            "The addendum source-check script explicitly recomputes the H1 absent count because "
            "the frozen H1 output contains -6 from bitwise inversion of an object column."
            if h1_bug else "No explicit H1 count correction was detected."
        ),
        "recommended_resolution": "Keep the corrected count as the cited value and retain the frozen output only for audit history.",
    })
    report = {
        "title": "Timucua archived analysis source audit",
        "archive": "analysis_all.zip",
        "archive_sha256": digest,
        "findings": findings,
        "scope": "Static source inspection only; no linguistic result or preregistered hypothesis is changed.",
    }
    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for item in findings:
        print(f'{item["severity"].upper()}: {item["id"]}: {item["finding"]}')
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
