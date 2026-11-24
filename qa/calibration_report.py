#!/usr/bin/env python3
"""Summarize the committed Timucua contact-detection positive controls.

Run from any directory: python qa/calibration_report.py
This is an audit of the frozen test table, not a fresh execution of the
underlying permutation pipeline.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "cldf/tests.csv"


def main():
    with TESTS.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    controls = [
        row for row in rows
        if row.get("Hypothesis", "").strip().lower() == "calibration"
        and row.get("Status", "").strip().lower() == "validation (before freezing)"
    ]
    if len(controls) != 5:
        raise SystemExit(f"Expected 5 frozen positive controls; found {len(controls)}.")

    positives = []
    for row in controls:
        detected = row.get("Verdict", "").strip().lower() == "detected"
        positives.append({
            "test": row["ID"],
            "recipient": row["Recipient"],
            "donor": row["Donor"],
            "shared_concepts": int(row["N_Items"]),
            "detected": detected,
            "permutation_p": float(row["P_Perm"]),
            "max_rule_p": float(row["P_Max"]),
        })

    detected = sum(item["detected"] for item in positives)
    small = [item for item in positives if item["shared_concepts"] <= 38]
    large = [item for item in positives if item["shared_concepts"] >= 90]
    report = {
        "title": "Timucua contact-detection calibration audit",
        "source": "cldf/tests.csv",
        "source_scope": "five frozen positive-control tests; no newly run simulations",
        "positive_controls": positives,
        "summary": {
            "positive_controls": len(positives),
            "detected": detected,
            "missed": len(positives) - detected,
            "sensitivity_on_this_small_control_set": round(detected / len(positives), 3),
            "controls_with_38_or_fewer_shared_concepts": len(small),
            "detected_among_controls_with_38_or_fewer": sum(x["detected"] for x in small),
            "controls_with_90_or_more_shared_concepts": len(large),
            "detected_among_controls_with_90_or_more": sum(x["detected"] for x in large),
        },
        "interpretation": [
            "The method detected all three controls with at least 37 shared concepts only when the contact signal was strong in the larger cases; it missed both documented Yuchi–Creek and Natchez–Creek controls at 33 and 38 concepts.",
            "The 3/5 fraction is descriptive of these selected controls, not a general estimate of sensitivity.",
            "The table does not supply a sufficiently defined set of known-negative controls for a specificity estimate.",
            "The existing null result therefore cannot exclude small, localized, or lexically restricted contact layers.",
        ],
    }
    out = ROOT / "qa/calibration_report.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    print(f"Wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
