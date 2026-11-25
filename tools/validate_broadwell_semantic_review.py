#!/usr/bin/env python3
"""Validate the conservative Broadwell semantic review queue."""
import csv
from pathlib import Path
root = Path(__file__).resolve().parents[1]
path = root / "sources/broadwell_semantic_review.csv"
with path.open(encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))
assert len(rows) >= 3000, f"Too few review records: {len(rows)}"
assert len({r["entry_id"] for r in rows}) == len(rows), "Entry IDs are not unique"
assert all(r["review_decision"] == "needs_human_review" for r in rows)
assert all(not r["normalized_english_gloss"] for r in rows), "Unreviewed glosses must remain blank"
assert all(r["gloss_fragment_type"].startswith("unparsed") for r in rows)
assert all(r["pdf_page"].isdigit() for r in rows)
print(f"PASS: {len(rows)} records; unique IDs; no unreviewed gloss promoted to normalized meaning.")
