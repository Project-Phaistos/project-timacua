#!/usr/bin/env python3
"""Validate the Broadwell semantic review queue and preserve human annotations."""
import csv
from pathlib import Path
root = Path(__file__).resolve().parents[1]
path = root / "sources/broadwell_semantic_review.csv"
with path.open(encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))
assert len(rows) == 3770, f"Expected 3,770 entry records, got {len(rows)}"
assert len({r["entry_id"] for r in rows}) == len(rows), "Entry IDs are not unique"
assert all(r["gloss_fragment_type"].startswith("unparsed") for r in rows)
assert all(r["pdf_page"].isdigit() for r in rows)
for row in rows:
    if row["review_decision"] == "needs_human_review":
        assert not row["normalized_english_gloss"], "Unreviewed gloss promoted to normalized meaning"
    else:
        assert row["normalized_english_gloss"], "Reviewed row lacks normalized gloss"
by_key = {(r["headword"].casefold(), r["pdf_page"]): r for r in rows}
expected = {
    ("efa", "86"): ("dog", "thing", "2009", "21", "reviewed_manual"),
    ("ilaqe", "138"): ("night; become night; afternoon", "thing", "1233", "92", "reviewed_manual_exploratory"),
    ("neha", "198"): ("sauce; grease; medicinal liquid", "body", "323", "32", "reviewed_manual_exploratory"),
}
for key, values in expected.items():
    row = by_key[key]
    actual = (row["normalized_english_gloss"], row["semantic_domain"],
              row["concepticon_id"], row["cldf_parameter_id"], row["review_decision"])
    assert actual == values, f"Unexpected reviewed annotation for {key}: {actual}"
print(f"PASS: {len(rows)} entries; 3 traceable manual annotations; remaining rows stay unreviewed.")
