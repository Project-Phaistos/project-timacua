#!/usr/bin/env python3
"""Create a source-traceable metadata index from Broadwell's Sept. 2024 PDF."""
from __future__ import annotations
import csv
import re
from collections import Counter
from pathlib import Path

source = Path("broadwell-dictionary.txt")
out_dir = Path("sources")
out_dir.mkdir(parents=True, exist_ok=True)
text = source.read_text(encoding="utf-8", errors="replace")
lines = text.split("\n")
start_re = re.compile(
    r"^\S+(?:\s+\[[^\]]+\])?\s+"
    r"(?:nprop\b|pron\b|adj\b|adv\b|quant\b|post\b|prep\b|"
    r"conj\b|interj\b|num\b|vt\b|vi\b|v\b|n\b|{{|[0-9]\)|\*)"
)
starts = []
page = 1
for i, raw in enumerate(lines):
    page += raw.count("\f")
    clean = raw.replace("\f", "")
    if start_re.match(clean):
        starts.append((i, clean, page))

fields = ["headword", "phonetic_form", "part_of_speech", "status", "pdf_page"]
rows = []
for n, (idx, first, page_no) in enumerate(starts):
    end = starts[n + 1][0] if n + 1 < len(starts) else len(lines)
    block = "\n".join(x.replace("\f", "") for x in lines[idx:end]).strip()
    headword = re.match(r"^(\S+)", first).group(1)
    phon = re.match(r"^\S+\s+\[([^\]]+)\]", first)
    rest = first[len(headword):].strip()
    pos = re.match(
        r"(nprop|pron|adj|adv|quant|post|prep|conj|interj|num|vt|vi|v|n)\b",
        rest,
    )
    status = re.search(r"\[Status\s+([^\]]+)\]", block, re.I | re.S)
    status_value = re.sub(r"\s+", " ", status.group(1)).strip() if status else ""
    rows.append({
        "headword": headword,
        "phonetic_form": phon.group(1).strip() if phon else "",
        "part_of_speech": pos.group(1) if pos else "",
        "status": status_value,
        "pdf_page": page_no,
    })

csv_path = out_dir / "broadwell_dictionary_index.csv"
with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

status_counts = Counter(r["status"] or "Unspecified" for r in rows)
unique = len({r["headword"].casefold() for r in rows})
report = [
    "# Broadwell Timucua dictionary source index",
    "",
    "Source: George Aaron Broadwell, *A Timucua–English–Spanish Dictionary*,",
    "draft version September 2024. The source PDF is stored at the repository root.",
    "",
    "This file is a metadata index, not a replacement for the dictionary. It records",
    "headword spellings, any bracketed phonetic form, an easily detectable initial",
    "part-of-speech label, the dictionary's own status label, and PDF page number.",
    "No definitions, examples, or extended dictionary text are redistributed here.",
    "",
    f"- Parsed entry records: {len(rows):,}",
    f"- Distinct headword spellings (case-insensitive): {unique:,}",
    f"- PDF pages containing entries: {min(r['pdf_page'] for r in rows)}–{max(r['pdf_page'] for r in rows)}",
    f"- Records with no status label: {status_counts['Unspecified']:,}",
    "",
    "## Status labels in the source",
    "",
]
for label, count in sorted(status_counts.items()):
    report.append(f"- {label}: {count:,}")
report += [
    "",
    "## Interpretation and limitations",
    "",
    "The parser uses entry-like line patterns and is intended as a reviewable index.",
    "It is not a fully validated lexical database: multi-sense entries remain together,",
    "some headword boundaries or grammatical labels may require manual correction,",
    "and blank status does not mean low confidence. Duplicate headwords are retained.",
    "The dictionary's label 'Borrowed' is reproduced as source metadata; it does not",
    "by itself identify a Muskogean source or demonstrate Timucua–Muskogean contact.",
    "All candidate comparisons must be checked against the dictionary entry and its",
    "cited historical text before being used as evidence.",
    "",
    "The PDF and online dictionary should be cited as the authoritative source.",
    "The online Webonary version may have changed since this September 2024 draft.",
]
(out_dir / "BROADWELL_DICTIONARY_INDEX.md").write_text("\n".join(report) + "\n", encoding="utf-8")
print(f"Wrote {len(rows)} entry records; {unique} distinct headwords.")
