#!/usr/bin/env python3
"""Dependency-free release checks for the published Timucua CLDF dataset.

Run from any working directory: python qa/check_release.py
These checks validate the committed release artifacts; they do not rerun
or reinterpret the linguistic analyses.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def unique(records: list[dict[str, str]], field: str, label: str) -> None:
    values = [r.get(field, "") for r in records]
    if any(not value for value in values):
        raise AssertionError(f"{label}: blank {field}")
    if len(values) != len(set(values)):
        raise AssertionError(f"{label}: duplicate {field}")


def main() -> int:
    languages = rows("cldf/languages.csv")
    concepts = rows("cldf/parameters.csv")
    forms = rows("cldf/forms.csv")
    cognates = rows("cldf/cognates.csv")
    comparisons = rows("cldf/comparisons.csv")
    candidates = rows("cldf/candidates.csv")
    tests = rows("cldf/tests.csv")
    places = rows("cldf/place_names.csv")

    for records, label in [
        (languages, "languages"), (concepts, "concepts"),
        (forms, "forms"), (cognates, "cognates"), (comparisons, "comparisons"),
        (candidates, "candidates"), (tests, "tests"), (places, "place names"),
    ]:
        unique(records, "ID", label)

    assert len(languages) == 67, f"expected 67 languages, got {len(languages)}"
    assert len(concepts) == 100, f"expected 100 concepts, got {len(concepts)}"
    assert len(forms) == 6799, f"expected 6,799 forms, got {len(forms)}"
    assert len(cognates) == 2424, f"expected 2,424 cognate judgments, got {len(cognates)}"
    assert len(comparisons) == 607, f"expected 607 comparisons, got {len(comparisons)}"
    assert len(candidates) == 156, f"expected 156 candidate records, got {len(candidates)}"
    assert len(tests) == 32, f"expected 32 test rows, got {len(tests)}"
    assert len(places) == 24, f"expected 24 place-name records, got {len(places)}"

    language_ids = {r["ID"] for r in languages}
    concept_ids = {r["ID"] for r in concepts}
    form_ids = {r["ID"] for r in forms}
    for form in forms:
        assert form["Language_ID"] in language_ids, (
            f"form {form['ID']} has unknown language {form['Language_ID']}"
        )
        assert form["Parameter_ID"] in concept_ids, (
            f"form {form['ID']} has unknown concept {form['Parameter_ID']}"
        )
        assert form["Form"], f"form {form['ID']} has empty normalized form"

    for comparison in comparisons:
        assert comparison["Form_ID"] in form_ids, f"comparison {comparison['ID']} points to missing form"
        assert comparison["Timucua_Form_ID"] in form_ids, f"comparison {comparison['ID']} points to missing Timucua form"
        assert comparison["Language_ID"] in language_ids, f"comparison {comparison['ID']} has unknown language"
        assert comparison["Parameter_ID"] in concept_ids, f"comparison {comparison['ID']} has unknown concept"

    for candidate in candidates:
        assert candidate["Parameter_ID"] in concept_ids, f"candidate {candidate['ID']} has unknown concept"

    for cognate in cognates:
        assert cognate["Form_ID"] in form_ids, (
            f"cognate {cognate['ID']} points to missing form {cognate['Form_ID']}"
        )
        assert cognate["Cognateset_ID"], f"cognate {cognate['ID']} has no cognate set"

    metadata = json.loads((ROOT / "cldf/Wordlist-metadata.json").read_text(encoding="utf-8"))
    extents: dict[str, int] = {}
    for table in metadata["tables"]:
        url = table.get("url")
        if url:
            extents[url] = int(table.get("dc:extent", -1))
    assert extents.get("forms.csv") == len(forms), "CLDF form extent disagrees with forms.csv"
    assert extents.get("languages.csv") == len(languages), "CLDF language extent disagrees with languages.csv"
    assert extents.get("parameters.csv") == len(concepts), "CLDF parameter extent disagrees with parameters.csv"
    assert extents.get("cognates.csv") == len(cognates), "CLDF cognate extent disagrees with cognates.csv"

    print("Timucua release QA: PASS")
    print(f"  {len(languages)} languages; {len(concepts)} concepts; {len(forms)} forms")
    print(f"  {len(cognates)} cognate judgments; {len(comparisons)} comparisons; {len(candidates)} candidate records")
    print(f"  {len(tests)} tests; {len(places)} place-name records")
    print("  unique IDs, CLDF foreign keys, and declared table extents verified")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Timucua release QA: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
