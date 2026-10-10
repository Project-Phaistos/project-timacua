# Project Phaistos: Timucua–Muskogean comparative database

A CLDF database comparing Timucua with the Muskogean languages of the Southeast (Mikasuki, Hitchiti, Creek, Alabama, Koasati, Apalachee, Choctaw, Chickasaw and Proto-Muskogean), plus 50 control languages. It is the data layer of the proposal *Recovering Timucua: A Computer-Assisted Framework for Text Analysis and Contact Detection in Mikasuki and Muscogee* (Crowley, Phaistos Labs, 2026), and holds every form, cognate judgment, similarity score and test result from the pre-registered pilot.

## What's in it

| Path | Contents |
|---|---|
| `cldf/` | CLDF Wordlist: 67 languages, 100 concepts, 6,799 forms, 2,424 cognate judgments, plus four extra tables (below). Validates with `cldf validate`. |
| `db/project-phaistos.sqlite` | The same data as SQLite, with ready-made views (`db/views.sql`). |
| `tables/southeast_wordlist.csv` | One row per concept, one column per Southeastern language plus Timucua. |
| `tables/timucua_comparisons_wide.csv` | The same grid with each form's similarity to Timucua and its candidate p-value. |
| `analysis/` | The full pilot: pipeline code, pre-registration and addenda (with hashes), validation, all results. See `analysis/README.md`. |
| `build/` | `build.sh` rebuilds `cldf/`, `db/` and `tables/` from `analysis/`. |

### Languages

| Group | Lists | Source |
|---|---|---|
| Possible donor | Timucua | ASJP (Granberry 1993) |
| Muskogean | Mikasuki, Creek, Alabama, Koasati, Choctaw, Chickasaw | ASJP |
| Muskogean, added by hand | Hitchiti (Gatschet 1884), Hitchiti (Haas 1937), Apalachee (Kimball 1988) | transcribed from the sources, page numbers in `Source` |
| Reconstruction | Proto-Muskogean (33 concepts) | ASJP list of Booker (2005) |
| Calibration and special | Mobilian Jargon, Yuchi, Natchez, Warao, Spanish, English | ASJP |
| Control panel | 50 languages, one per family, outside North America | ASJP |

### Tables

- **forms.csv.** `Value` keeps the source spelling (ASJP code, Gatschet, Haas or Kimball). `Form` and `Segments` give the normalized IPA. `Normalization` logs each rule applied. The flags record the Stage 2 and 3 results: `Muskogean_Residue` (no cognate in another Muskogean language), `Strict_Residue`, `European_Flag`, `Loose_Mapping`, and Kimball's expert judgment for Apalachee (`Expert_Muskogean_Cognate`).
- **cognates.csv.** Automated cognate sets (LexStat and SCA) from the frozen Stage 2 run (`main-…`) and from the rerun with Hitchiti (`h1-…`).
- **comparisons.csv.** For every concept shared with Timucua, each Southeastern list's best form pair, SCA, NED and TPG similarity, its rank among all 87 Timucua concepts, and the candidate p-value. `Analysis_Status` says whether the pair was a pre-registered test or is descriptive only.
- **tests.csv.** All 32 aggregate tests: the H2 confirmatory and secondary tests, H3, H4, the Hitchiti check, the exploratory Warao run and the calibrations.
- **candidates.csv.** Candidate-loan tables from every analysis, in both directions.
- **place_names.csv.** 22 Timucua-period place names and 2 modern names often mistaken for Timucua, with how each passed into modern use and an evidence grade.

## Quick start

```python
import sqlite3
db = sqlite3.connect("db/project-phaistos.sqlite")

# one concept across the Southeast
db.execute("select language, original, form, source from southeast_forms where concept = 'dog'").fetchall()

# Mikasuki words with no Muskogean cognate, closest Timucua match first
db.execute("""select concept, form, timucua_form, sca, p_candidate from timucua_vs_southeast
              where language = 'Mikasuki' and form_is_muskogean_residue = 1 order by p_candidate""").fetchall()

# every test and its verdict
db.execute("select test, z, p_perm, p_max, verdict from test_results").fetchall()
```

Or with pycldf: `Wordlist.from_metadata("cldf/Wordlist-metadata.json")`.

## Results so far

- **H2 (pre-registered): no Timucua layer detected.** Mikasuki residue x Timucua gives z = 0.64, p = 0.26; Timucua ranks 29th of 51 candidate donors. All Creek, measure and robustness variants agree.
- **The null is bounded.** The same design detects inheritance and pidginization but misses documented Yuchi–Creek and Natchez–Creek contact at 33 to 38 concepts. It rules out only a large layer.
- **H1:** the 3 Mikasuki residue words covered by 1880s Hitchiti (who, tree, fire) are all attested there, so they predate the move to Florida.
- **H4:** Apalachee x Timucua is null too (z = −0.70).
- **Post hoc lead, Muskogean into Timucua:** *efa* 'dog', *neha* 'grease', *ilake* 'night'.
- **Methods:** a plain permutation test flags 8 to 30% of unrelated pairs. The two-way rank rule used here brings that to about 2%.

**Reading `comparisons.csv`.** A candidate p-value ranks one pair against the other 86 Timucua concepts, so its floor is 0.0115. Short forms reach that floor by chance (*ma* 'that' matches in five languages). Only the analyses marked as tests in `Analysis_Status` and `tests.csv` were pre-registered; the rest is descriptive.

## Rebuild

```
pip install pycldf lingpy lingrex python-igraph rapidfuzz scipy pandas
./build/build.sh
```

Missing similarity matrices are computed on the fly into `analysis/results/grid/` (not tracked). To rerun the pilot itself, follow `analysis/README.md`.

## Sources and licences

- Code (`build/`, `analysis/src/`, `analysis/workstream_a/`) is under the MIT licence in `LICENSE`. The data keep their source licences, below.
- ASJP, WOLD, IDS, WALS and Concepticon data are CC-BY 4.0. Cite them as listed in `cldf/sources.bib` and `analysis/docs/bibliography_and_outreach.md`.
- Gatschet (1884) is in the public domain.
- Kimball (1988) Apalachee forms are short citations of a published vocabulary, credited per form.
- The Haas (1937) Hitchiti forms are transcribed from a digitized notebook in the Mary R. Haas Papers at the American Philosophical Society. Check the APS reuse terms before making this repository public.

## Community note

All material here is published or archival. Following section 9 of the proposal, the Seminole Tribe of Florida and the Miccosukee Tribe of Indians of Florida are being asked for guidance, including whether they want to see results before anything is shared publicly. Keep this repository private until they have answered.

## Citation

Crowley, Dennis. 2026. *Project Phaistos: Timucua–Muskogean comparative database* (pilot release). Phaistos Labs.
