#!/usr/bin/env python3
"""Create a conservative, human-reviewable semantic annotation queue.

The extracted fragment is deliberately labelled raw: Broadwell's PDF often
runs English and Spanish together without a separator, and entries may contain
multiple senses. This script does not infer normalized meanings.
"""
from __future__ import annotations
import csv, hashlib, re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = root / "broadwell-dictionary.txt"
index_path = root / "sources/broadwell_dictionary_index.csv"
out_path = root / "sources/broadwell_semantic_review.csv"
if not source.exists():
    raise SystemExit("Missing broadwell-dictionary.txt; run the PDF extraction workflow first.")

with index_path.open(encoding="utf-8-sig", newline="") as f:
    index_rows = list(csv.DictReader(f))

lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
start_re = re.compile(
    r"^\\S+(?:\\s+\\[[^\\]]+\\])?\\s+"
    r"(?:nprop\\b|pron\\b|adj\\b|adv\\b|quant\\b|post\\b|prep\\b|"
    r"conj\\b|interj\\b|num\\b|vt\\b|vi\\b|v\\b|n\\b|{{|[0-9]\\)|\\*)"
)
starts = []
page = 1
for i, raw in enumerate(lines):
    page += raw.count("\\f")
    clean = raw.replace("\\f", "").strip()
    if start_re.match(clean):
        starts.append((i, clean, page))

pos_re = re.compile(r"^(nprop|pron|adj|adv|quant|post|prep|conj|interj|num|vt|vi|v|n)\\b")
rows = []
for ordinal, (line_no, first, page_no) in enumerate(starts, 1):
    # Use the corresponding parser row as the stable metadata source.
    meta = index_rows[ordinal - 1] if ordinal <= len(index_rows) else {}
    head = re.match(r"^(\\S+)", first).group(1)
    rest = first[len(head):].strip()
    phon = re.match(r"^\\[([^\\]]+)\\]\\s*(.*)$", rest)
    after_phon = phon.group(2) if phon else rest
    pos = pos_re.match(after_phon)
    fragment = after_phon[pos.end():].strip() if pos else after_phon
    fragment = re.sub(r"\\s*\\[Status\\s+[^\\]]+\\].*$", "", fragment, flags=re.I)
    fragment = fragment[:180].strip()
    key = f"{ordinal}|{head}|{meta.get('phonetic_form','')}|{page_no}"
    entry_id = "BW-" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:12].upper()
    rows.append({
        "entry_id": entry_id,
        "headword": meta.get("headword", head),
        "phonetic_form": meta.get("phonetic_form", ""),
        "part_of_speech_candidate": meta.get("part_of_speech", ""),
        "dictionary_status": meta.get("status", ""),
        "pdf_page": meta.get("pdf_page", page_no),
        "source_line": line_no + 1,
        "gloss_fragment_raw": fragment,
        "gloss_fragment_type": "unparsed first-line fragment; may mix English and Spanish",
        "normalized_english_gloss": "",
        "sense_number": "",
        "semantic_domain": "",
        "concepticon_id": "",
        "cldf_parameter_id": "",
        "review_decision": "needs_human_review",
        "reviewer_notes": "",
    })

fields = list(rows[0]) if rows else []
out_path.parent.mkdir(parents=True, exist_ok=True)
with out_path.open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)
print(f"Wrote {len(rows)} conservative semantic review records to {out_path}")
