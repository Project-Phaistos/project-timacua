#!/usr/bin/env python3
"""Validate a CSV export of Timucua archival token annotations.

Usage: python tools/timucua_text/validate.py annotations.csv
No NLP or external dependencies are required. This validates structure and
provenance fields; it does not certify a transcription or gloss as correct.
"""
import csv
import sys
from pathlib import Path

REQUIRED = ("text_id", "line_id", "token_id", "source_ref", "diplomatic_form", "certainty")
OPTIONAL = (
    "normalized_form", "segmentation", "gloss", "translation",
    "notes", "annotator", "review_status",
)
CERTAINTY = {"high", "medium", "low", "unreadable"}
REVIEW = {"unreviewed", "reviewed", "disputed"}


def validate(path):
    errors = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        missing = [field for field in REQUIRED if field not in fields]
        if missing:
            return [f"Missing required columns: {', '.join(missing)}"]
        unknown = [field for field in fields if field not in REQUIRED + OPTIONAL]
        if unknown:
            errors.append(f"Unknown columns: {', '.join(unknown)}")
        seen = set()
        count = 0
        for line_no, row in enumerate(reader, start=2):
            count += 1
            for field in REQUIRED:
                if not (row.get(field) or "").strip():
                    errors.append(f"Row {line_no}: {field} is required.")
            certainty = (row.get("certainty") or "").strip().lower()
            if certainty and certainty not in CERTAINTY:
                errors.append(f"Row {line_no}: invalid certainty '{certainty}'.")
            review = (row.get("review_status") or "unreviewed").strip().lower()
            if review not in REVIEW:
                errors.append(f"Row {line_no}: invalid review_status '{review}'.")
            key = tuple((row.get(k) or "").strip() for k in ("text_id", "line_id", "token_id"))
            if all(key) and key in seen:
                errors.append(f"Row {line_no}: duplicate token key {key}.")
            seen.add(key)
            if certainty == "unreadable" and (row.get("normalized_form") or "").strip():
                errors.append(f"Row {line_no}: unreadable token must not have normalized_form.")
        if count == 0:
            errors.append("No annotation records found; the header-only template is not a dataset.")
    return errors


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python tools/timucua_text/validate.py annotations.csv")
    path = Path(sys.argv[1])
    if not path.is_file():
        raise SystemExit(f"File not found: {path}")
    errors = validate(path)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        raise SystemExit(1)
    print(f"Valid annotation structure: {path}")


if __name__ == "__main__":
    main()
