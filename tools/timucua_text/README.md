# Timucua archival-text annotation prototype

This is a small, dependency-free data model and validator for a future text-processing corpus. It is deliberately a schema and workflow prototype, **not a claim that new Timucua text has been transcribed**.

## Why this deliverable

The comparative wordlist can test lexical contact, but it cannot itself recover syntax, morphology, discourse, or contextual meanings from archival texts. A text corpus needs to preserve the source reading separately from analyst normalization and interpretation. The schema therefore records a diplomatic form, optional normalization and segmentation, gloss/translation, a source reference, and an explicit certainty/review state.

## Files

- `schema.json`: JSON Schema for one token annotation.
- `template.csv`: header-only CSV template; it contains no fabricated lexical records.
- `validate.py`: standard-library validator for CSV exports.

## Use

```bash
python tools/timucua_text/validate.py annotations.csv
python -m unittest discover -s tests -v
```

Required columns are `text_id,line_id,token_id,source_ref,diplomatic_form,certainty`. Certainty must be `high`, `medium`, `low`, or `unreadable`. The source reading is never overwritten by normalized spelling or segmentation. Duplicate token keys are rejected.

## Annotation rules

1. Cite every token to an archival source and page/folio or stable image identifier.
2. Preserve the diplomatic reading verbatim; put editorial normalization in a separate field.
3. Mark unreadable material explicitly; do not guess a form.
4. Treat segmentation, glosses, and translations as hypotheses that can be reviewed or disputed.
5. Keep the annotation history and source permissions with the corpus.

The validator checks file structure and basic consistency only. It cannot establish palaeographic accuracy, linguistic correctness, or archival reuse permission.
