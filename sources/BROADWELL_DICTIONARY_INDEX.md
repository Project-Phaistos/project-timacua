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

See broadwell_candidate_audit.csv for source-traceable review of three comparisons.
Timucua efa 'dog' is marked Confident (PDF p. 86); Gatschet (1884:58)
explicitly states that Maskoki ífa went over to Timucua. The CLDF also has
Creek, Alabama, and Koasati ifa for 'dog'. This is historical evidence for
transfer, not a new result from the statistical test, and the current CLDF
contains no Mikasuki dog form.

Timucua ilaqe [ilake] is 'become night; afternoon; night' and Confident
(PDF p. 138). Creek and Mikasuki niɬaki are comparison forms for 'night',
but the forms are not an obvious regular sound match; borrowing is unproven.

Timucua neha is 'sauce; grease; medicinal liquid' (PDF p. 198), with no
status label. Creek and Chickasaw niha are comparison forms. A separate
Timucua niha 'older sibling' entry is marked Probable (PDF p. 201) and
must not be conflated with neha 'grease'.

The dictionary's 277 entries marked 'Borrowed' are not automatically
Muskogean loans: the label does not name a donor language.

## Files

- broadwell_dictionary_index.csv: parsed headword metadata and source page.
- broadwell_cldf_exact_form_matches.csv: exact-form screening against the
  Timucua forms already in the CLDF.
- broadwell_candidate_audit.csv: manual assessment of the comparisons above.
