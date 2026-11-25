# Broadwell Timucua dictionary source index

Source: George Aaron Broadwell, *A Timucua–English–Spanish Dictionary*,
draft version September 2024. The source PDF is stored at the repository root.

The metadata index records headword spellings, any bracketed phonetic form,
an easily detectable initial part-of-speech label, the dictionary's own status
label, and PDF page number. It does not redistribute definitions or examples.

- Parsed entry records: 3,770
- Distinct headword spellings (case-insensitive): 3,560
- PDF pages containing entries: 2–305
- Timucua forms in the existing CLDF wordlist: 134
- Exact phonetic-string matches for manual review: 166
- Records with no dictionary status label: 1,493

## Status labels in the source

- Borrowed: 277
- Confident: 960
- Confident Hapax Leg.: 9
- Dubious: 4
- Hapax Legomenon: 57
- Pending: 7
- Probable: 457
- Tentative: 506
- Unspecified: 1,493

## Exact-form cross-check

The companion CSV lists exact matches between the dictionary's bracketed
phonetic forms and existing CLDF Timucua forms after whitespace normalization.
These are retrieval candidates only. Identical phonetic strings do not establish
shared meaning, cognacy, borrowing, direction of transfer, or chronology.
Non-matches do not establish that a dictionary item is new: the two sources may
use different transcription conventions or represent different concepts.

## Interpretation and limitations

The parser uses entry-like line patterns and is intended as a reviewable index.
It is not a fully validated lexical database: multi-sense entries remain together,
some headword boundaries or grammatical labels may require manual correction,
and blank status does not mean low confidence. Duplicate headwords are retained.
The dictionary's label 'Borrowed' is reproduced as source metadata; it does not
by itself identify a Muskogean source or demonstrate Timucua–Muskogean contact.
All candidate comparisons must be checked against the dictionary entry and its
cited historical text before being used as evidence.

The PDF and online dictionary should be cited as the authoritative source.
The online Webonary version may have changed since this September 2024 draft.


## Manual comparison audit

A separate, source-traceable review of three previously discussed comparisons is in
`broadwell_candidate_audit.csv`.

- **efa 'dog' — strongest documented transfer.** Broadwell records Timucua `efa`
  as “dog” with a Confident label (PDF p. 86). Gatschet (1884:58) explicitly says
  Maskoki `ífa` went over to Timucua. The existing CLDF also records Timucua
  `efa` and Creek, Alabama, and Koasati `ifa` for “dog”. This is historical
  evidence for a transfer, not a new finding produced by the statistical test.
  The current CLDF has no Mikasuki “dog” form, so it should not be presented as
  evidence for a specifically Mikasuki borrowing layer.
- **ilaqe [ilake] 'night' — exploratory.** Broadwell gives “become night,
  afternoon; night” and labels the entry Confident (PDF p. 138). Creek and
  Mikasuki have `niɬaki` for “night” in the CLDF. The forms are not an obvious
  regular sound match; borrowing is not established.
- **neha 'sauce/grease' — low-confidence exploratory.** Broadwell gives “sauce;
  grease; medicinal liquid” (PDF p. 198), but the entry has no status label.
  Creek and Chickasaw `niha` are comparison forms in the CLDF. Broadwell also
  has a separate Timucua `niha` entry meaning “older sibling” (Probable, PDF
  p. 201); it must not be confused with `neha` “grease”.

These three examples illustrate why a dictionary-wide comparison needs semantic
review and source-level auditing. Similar spellings alone are not evidence of
borrowing. The dictionary's 277 entries marked “Borrowed” are not automatically
Muskogean loans: the label does not name a donor language, and many entries are
transparent Spanish or Christian vocabulary. Donor attribution must be assessed
entry by entry.

## Files

- `broadwell_dictionary_index.csv`: parsed headword metadata and source page.
- `broadwell_cldf_exact_form_matches.csv`: exact phonetic-string matches against
  the 134 Timucua forms already in the CLDF.
- `broadwell_candidate_audit.csv`: manual assessment of the three comparisons
  above, with evidence and explicit decision labels.
