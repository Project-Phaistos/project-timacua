#!/usr/bin/env python3
"""Sanity checks for the reproducible Broadwell dictionary index."""
import csv
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sources = root / "sources"

def read_csv(name):
    with (sources / name).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

entries = read_csv("broadwell_dictionary_index.csv")
matches = read_csv("broadwell_cldf_exact_form_matches.csv")
audit = read_csv("broadwell_candidate_audit.csv")

assert len(entries) >= 3000, f"Unexpectedly few dictionary records: {len(entries)}"
assert len({r["headword"].casefold() for r in entries}) >= 3000
assert all(2 <= int(r["pdf_page"]) <= 305 for r in entries)
assert any(r["headword"].casefold() == "efa" and r["phonetic_form"] == "efa"
           and r["status"] == "Confident" for r in entries)
assert any(r["headword"].casefold() == "ilaqe" and r["phonetic_form"] == "ilake"
           and r["status"] == "Confident" for r in entries)
assert any(r["headword"].casefold() == "neha" and r["phonetic_form"] == "neha"
           for r in entries)
assert any(r["headword"].casefold() == "niha" and "older sibling" in r.get("status", "").lower()
           for r in entries) is False  # Status is a confidence label, not a gloss field.
assert len(matches) >= 100
assert all(r["match_type"].startswith("exact phonetic string") for r in matches)
required = {"TIM-EFA-001", "TIM-ILAQE-002", "TIM-NEHA-003"}
assert {r["candidate_id"] for r in audit} == required
assert all(r["assessment"] and r["decision"] for r in audit)
print(f"PASS: {len(entries)} dictionary records; {len(matches)} exact-form matches; {len(audit)} audited candidates.")
