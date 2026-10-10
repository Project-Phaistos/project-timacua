"""Build the Project Phaistos comparative database (CLDF Wordlist + SQLite + wide tables).

Inputs come from ../analysis (the frozen Timucua pilot). Run from the repo root:

    python3 build/build_db.py
    cldf validate cldf/Wordlist-metadata.json
    cldf createdb cldf/Wordlist-metadata.json db/project-phaistos.sqlite
    sqlite3 db/project-phaistos.sqlite < db/views.sql

Tables written to cldf/:
  languages.csv, parameters.csv, forms.csv, cognates.csv  (standard CLDF components)
  comparisons.csv   Timucua x each Southeastern list, per concept (descriptive similarities)
  tests.csv         every aggregate contact test, calibration and placebo run in the pilot
  candidates.csv    candidate-loan tables from every analysis
  place_names.csv   the Timucua-period place-name gazetteer
"""
import importlib.util
import json
import os
import re
import sys

import numpy as np
import pandas as pd
from pycldf import Wordlist

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(REPO, "analysis")
sys.path.insert(0, os.path.join(A, "src"))
from common import sim_sca  # noqa: E402
from twoway import get  # noqa: E402

spec = importlib.util.spec_from_file_location("grid", os.path.join(A, "src", "05_similarity_grid.py"))
grid = importlib.util.module_from_spec(spec); spec.loader.exec_module(grid)

OUT = os.path.join(REPO, "cldf")
TABLES = os.path.join(REPO, "tables")
os.makedirs(OUT, exist_ok=True); os.makedirs(TABLES, exist_ok=True)

SOUTHEAST = ["MIKASUKI", "HITCHITI_1884", "HITCHITI_1937", "CREEK", "ALABAMA", "KOASATI", "APALACHEE",
             "CHOCTAW", "CHICKASAW", "PROTO_MUSKOGEAN"]
MUSK6 = ["MIKASUKI", "CREEK", "ALABAMA", "KOASATI", "CHOCTAW", "CHICKASAW"]


def rd(*p, **kw):
    return pd.read_csv(os.path.join(A, *p), **kw)


def seg2form(s):
    return s.replace(" ", "")


# ----------------------------------------------------------------------------- sources
BIB_EXTRA = r"""
@book{Gatschet1884,
  author = {Gatschet, Albert S.},
  title = {A Migration Legend of the Creek Indians, vol. 1},
  publisher = {D. G. Brinton},
  address = {Philadelphia},
  year = {1884},
  url = {https://archive.org/details/migrationcreek00gatsrich}
}
@misc{Haas1937,
  author = {Haas, Mary R.},
  title = {Hitchiti field notebook I (consultant Willie Haney, Eufaula, Oklahoma)},
  year = {1937},
  howpublished = {Mary R. Haas Papers, Mss.Ms.Coll.94, box 19, American Philosophical Society}
}
@article{Kimball1988,
  author = {Kimball, Geoffrey},
  title = {An Apalachee vocabulary},
  journal = {International Journal of American Linguistics},
  volume = {54},
  number = {4},
  pages = {387--398},
  year = {1988}
}
@article{Kimball1987,
  author = {Kimball, Geoffrey},
  title = {A grammatical sketch of Apalachee},
  journal = {International Journal of American Linguistics},
  volume = {53},
  number = {2},
  pages = {136--174},
  year = {1987}
}
@phdthesis{Boynton1982,
  author = {Boynton, Sylvia S.},
  title = {Mikasuki Grammar in Outline},
  school = {University of Florida},
  year = {1982},
  url = {https://archive.org/details/mikasukigrammari00boyn}
}
@incollection{Booker2005,
  author = {Booker, Karen M.},
  title = {Muskogean historical phonology},
  booktitle = {Native Languages of the Southeastern United States},
  editor = {Hardy, Heather K. and Scancarelli, Janine},
  publisher = {University of Nebraska Press},
  address = {Lincoln},
  pages = {246--298},
  year = {2005}
}
@misc{Pilot2026,
  author = {Crowley, Dennis},
  title = {Recovering Timucua: pre-registered pilot of computer-assisted contact detection},
  year = {2026},
  howpublished = {Project Phaistos, analysis/ in this repository}
}
"""


def main():
    # ------------------------------------------------------------------- languages
    langs = rd("cldf", "languages.csv")
    langs = langs[langs.ID != "MUSK_INHERITED"].copy()
    langs["Data_Source"] = "ASJP v20 (lexibank/asjp cf4bf0d)"
    langs.loc[langs.ID == "PROTO_MUSKOGEAN", "Data_Source"] = "ASJP list of Booker (2005) reconstructions"
    add = pd.DataFrame([
        dict(ID="APALACHEE", Name="Apalachee", Macroarea="North America", Glottocode="apal1237", Family="Muskogean",
             Role="addendum_h4", Data_Source="Kimball (1988) retranscription of the 1688 letter and the Paina document"),
        dict(ID="HITCHITI_1884", Name="Hitchiti (Gatschet 1884)", Macroarea="North America", Glottocode="hitc1239",
             Family="Muskogean", Role="addendum_h1",
             Data_Source="Gatschet (1884), from G. W. Stidham of Eufaula, Indian Territory; pre-Florida baseline"),
        dict(ID="HITCHITI_1937", Name="Hitchiti (Haas 1937)", Macroarea="North America", Glottocode="hitc1239",
             Family="Muskogean", Role="source_check",
             Data_Source="Haas (1937) notebook, consultant Willie Haney, Eufaula, Oklahoma; grandfather from Florida"),
    ])
    langs = pd.concat([langs, add], ignore_index=True)
    langs["Name"] = langs.Name.where(langs.Role.str.startswith(("addendum", "source")),
                                     langs.Name.str.replace("_", " ").str.title())

    # ------------------------------------------------------------------- parameters
    params = rd("cldf", "parameters.csv")
    params["ID"] = params.ID.astype(str)
    strata = rd("cldf", "concept_strata.csv"); strata["ID"] = strata.ID.astype(str)
    params = params.merge(strata[["ID", "stratum"]].rename(columns={"stratum": "Stratum"}), on="ID", how="left")
    cl = rd("concept_lists", "concept_list_planned.csv")
    wold = cl.dropna(subset=["concepticon_id"]).drop_duplicates("concepticon_id")
    wold = dict(zip(wold.concepticon_id.astype(int).astype(str), wold.wold_borrowed_score))
    params["WOLD_Borrowed_Score"] = params.Concepticon_ID.astype("Int64").astype(str).map(wold)
    resid = json.load(open(os.path.join(A, "results", "residue_concepts.json")))
    params["Mikasuki_Residue"] = params.ID.isin(resid["MIKASUKI"])
    params["Creek_Residue"] = params.ID.isin(resid["CREEK"])
    params = params[["ID", "Name", "Concepticon_ID", "Concepticon_Gloss", "Stratum", "WOLD_Borrowed_Score",
                     "Mikasuki_Residue", "Creek_Residue"]]
    gloss = dict(zip(params.ID, params.Name))

    # ------------------------------------------------------------------- forms
    f = rd("cldf", "forms.csv"); f["Parameter_ID"] = f.Parameter_ID.astype(str)
    f = f[f.Language_ID != "MUSK_INHERITED"].copy()
    nlog = rd("cldf", "normalization_log.csv")
    rules = nlog.groupby("Form_ID").Rule.apply(lambda s: "; ".join(sorted(set(s))))
    forms = pd.DataFrame(dict(
        ID=f.ID, Language_ID=f.Language_ID, Parameter_ID=f.Parameter_ID, Value=f.Asjp_Value,
        Form=f.Segments.map(seg2form), Segments=f.Segments, Original_Segments=f.Original_Segments,
        Normalization=f.ID.map(rules).fillna(""), Comment=f.Comment.fillna(""), Source=f.Source.fillna(""),
        Loose_Mapping=False))

    def addendum(df, lang, value_col, src, page_col=None, note_col=None, loose_rx="loose"):
        rows = []
        for k, r in enumerate(df.itertuples(index=False)):
            pid = str(r.Parameter_ID)
            n = sum(1 for x in rows if x["Parameter_ID"] == pid) + 1
            note = str(getattr(r, note_col) if note_col and pd.notna(getattr(r, note_col)) else "")
            page = str(getattr(r, page_col)) if page_col else ""
            rows.append(dict(ID=f"{lang}-{pid}-{n}", Language_ID=lang, Parameter_ID=pid,
                             Value=getattr(r, value_col), Form=seg2form(r.Segments), Segments=r.Segments,
                             Original_Segments="", Normalization="hand transcription to IPA segments",
                             Comment=note, Source=f"{src}[{page}]" if page else src,
                             Loose_Mapping=bool(re.search(loose_rx, note, re.I))))
        return pd.DataFrame(rows)

    ap = rd("cldf_addendum", "apalachee_forms.csv")
    ap["Note"] = ap.Mapping_note.fillna("")
    ap_f = addendum(ap, "APALACHEE", "Form", "Kimball1988", note_col="Note", loose_rx=".+")
    ap_f["Comment"] = ["; ".join(x for x in (f"manuscript spelling: {m}", n) if x)
                       for m, n in zip(ap.Manuscript_spelling, ap.Note)]
    ap_f["Expert_Muskogean_Cognate"] = list(ap.Kimball_cognates.fillna(""))
    gat = rd("cldf_addendum", "hitchiti_forms.csv")
    gat_f = addendum(gat, "HITCHITI_1884", "Gatschet_spelling", "Gatschet1884", page_col="Page", note_col="Note",
                     loose_rx="mapped|possessed|place-name")
    haas = rd("cldf_addendum", "hitchiti_haas1937_forms.csv")
    haas_f = addendum(haas, "HITCHITI_1937", "Haas_spelling", "Haas1937", page_col="Notebook_page", note_col="Note")
    forms = pd.concat([forms, ap_f, gat_f, haas_f], ignore_index=True)
    forms["Expert_Muskogean_Cognate"] = forms.get("Expert_Muskogean_Cognate", pd.Series(dtype=str)).fillna("")

    # residue flags from the frozen Stage 2 run (main) and the addendum runs
    cog = rd("results", "stage2_muskogean_cognates.csv")
    def partners(df, idcol, langcol):
        out = {}
        for ref in ("lexstatid", "scaid"):
            g = df.groupby(ref)[langcol].apply(set)
            for r in df.itertuples():
                out.setdefault(getattr(r, idcol), set()).update(g[getattr(r, ref)] - {getattr(r, langcol)})
        return out
    p_main = partners(cog, "Form_ID", "Language_ID")
    forms["Muskogean_Residue"] = forms.ID.map(lambda i: (len(p_main[i]) == 0) if i in p_main else pd.NA)
    pool = rd("results", "stage3_residue_pool.csv")
    forms["European_Flag"] = forms.ID.map(dict(zip(pool.Form_ID, pool.european_flag)))
    forms["Strict_Residue"] = forms.ID.map(dict(zip(pool.Form_ID, pool.strict_residue)))
    kim = rd("results", "h4_apalachee", "stage2_vs_kimball.csv")
    ap_auto = {(str(r.concept), r.Form): (not r.auto_inherited) for r in kim.itertuples()}
    hres = rd("results", "h1_hitchiti", "hitchiti_residue.csv")
    hi_auto = {(str(r.parameter_id), r.form): (not r.inherited) for r in hres.itertuples()}
    forms.loc[forms.Language_ID == "APALACHEE", "Muskogean_Residue"] = [
        ap_auto.get((str(p), k), pd.NA) for p, k in zip(ap.Parameter_ID, ap.Form)]
    for lang, m in (("HITCHITI_1884", hi_auto),):
        sel = forms.Language_ID == lang
        forms.loc[sel, "Muskogean_Residue"] = [m.get((p, fo), pd.NA) for p, fo in
                                               zip(forms.loc[sel, "Parameter_ID"], forms.loc[sel, "Form"])]

    # ------------------------------------------------------------------- cognates
    seg_index = {}
    for r in forms.itertuples():
        seg_index.setdefault((r.Language_ID, r.Parameter_ID, r.Segments), r.ID)
    cogrows = []
    for r in cog.itertuples():
        for meth, cid in (("LexStat", r.lexstatid), ("SCA", r.scaid)):
            cogrows.append(dict(Form_ID=r.Form_ID, Cognateset_ID=f"main-{meth.lower()}-{cid}", Method=meth,
                                Run="stage2_main (frozen pre-registration)", Source="Pilot2026"))
    h1 = rd("results", "h1_hitchiti", "stage2_with_hitchiti.csv")
    for r in h1.itertuples():
        lang = "HITCHITI_1884" if r.doculect == "HITCHITI" else r.doculect
        fid = seg_index.get((lang, str(r.concept), r.seg))
        if fid is None:
            continue
        for meth, cid in (("LexStat", r.lexstatid), ("SCA", r.scaid)):
            cogrows.append(dict(Form_ID=fid, Cognateset_ID=f"h1-{meth.lower()}-{cid}", Method=meth,
                                Run="stage2_h1_hitchiti (Addendum 2)", Source="Pilot2026"))
    cognates = pd.DataFrame(cogrows)
    cognates.insert(0, "ID", [f"cog-{i + 1}" for i in range(len(cognates))])

    # ------------------------------------------------------------------- comparisons (Timucua x Southeast)
    allf = {}
    for L, g in forms.groupby("Language_ID"):
        allf[L] = {c: list(gg.Segments) for c, gg in g.groupby("Parameter_ID")}
    for L in SOUTHEAST:
        A_ = "HITCHITI" if L == "HITCHITI_1884" else L
        grid.pair_job((A_, "TIMUCUA", allf[L], allf["TIMUCUA"]))
    status = {"MIKASUKI": "tested: H2 (pre-registered, residue concepts)", "CREEK": "tested: H2 secondary",
              "APALACHEE": "tested: H4 (Addendum 1)", "HITCHITI_1884": "tested: Georgia-era check (Addendum 2)"}
    tim_index = {(p, s): i for (l, p, s), i in seg_index.items() if l == "TIMUCUA"}
    comp = []
    for L in SOUTHEAST:
        A_ = "HITCHITI" if L == "HITCHITI_1884" else L
        mats = {m: get(A_, "TIMUCUA", m) for m in ("SCA", "NED", "TPG")}
        rows_, cols_, M = mats["SCA"]
        for c in [c for c in rows_ if c in cols_]:
            i, j = rows_.index(c), cols_.index(c)
            obs = M[i, j]; oth = np.delete(M[i], j)
            s, a, b = max((sim_sca(x, y), x, y) for x in allf[L][c] for y in allf["TIMUCUA"][c])
            comp.append(dict(
                Language_ID=L, Parameter_ID=c, Form_ID=seg_index[(L, c, a)], Timucua_Form_ID=tim_index[(c, b)],
                Form=seg2form(a), Timucua_Form=seg2form(b), SCA=round(float(obs), 3),
                NED=round(float(mats["NED"][2][i, j]), 3), TPG=int(mats["TPG"][2][i, j]),
                Rank_SCA=int((oth > obs).sum()) + 1, N_Timucua_Concepts=int(len(oth) + 1),
                P_Candidate=round(float((1 + (oth >= obs).sum()) / (1 + len(oth))), 4),
                Analysis_Status=status.get(L, "descriptive only (not a pre-registered test)")))
    comp = pd.DataFrame(comp)
    comp.insert(0, "ID", [f"cmp-{r.Language_ID}-{r.Parameter_ID}" for r in comp.itertuples()])

    # ------------------------------------------------------------------- tests
    t = pd.concat([rd("results", "all_tests.csv")], ignore_index=True)
    tests = []
    def trow(label, hyp, row, col, cset, measure, d, status, src):
        g = lambda k: d.get(k) if isinstance(d, dict) else getattr(d, k, None)
        tests.append(dict(ID=label, Hypothesis=hyp, Recipient=row, Donor=col, Concept_Set=cset, Measure=measure,
                          N_Items=g("focal_n_items"), Delta_S=g("focal_dS"), Z=g("focal_z"), P_Perm=g("focal_p_perm"),
                          P_Row=g("focal_p_row"), P_Col=g("focal_p_col"), P_Max=g("focal_p_max"),
                          Ruleset_A=g("ruleset_A"), Ruleset_B=g("ruleset_B"), Verdict=g("verdict"),
                          Status=status, Result_File=src))
    for r in t.itertuples():
        hyp = r.label.split("_")[0] if r.label.startswith(("H2", "H3")) else r.role
        cset = re.sub(r"^(H2|H3|descriptive|exploratory)_", "", r.label)
        trow(r.label, hyp, r.row, r.col, cset, r.measure, r._asdict(), r.role, "analysis/results/all_tests.csv")
    h4 = json.load(open(os.path.join(A, "results", "h4_apalachee", "h4_summary.json")))
    trow("H4_APALACHEE_SCA", "H4", "APALACHEE", "TIMUCUA", "24 Apalachee concepts", "SCA", h4["apalachee"],
         "addendum 1", "analysis/results/h4_apalachee/h4_summary.json")
    trow("H4_MIKASUKI_same_concepts_SCA", "H4", "MIKASUKI", "TIMUCUA", "same 24 concepts", "SCA",
         h4["mikasuki_same_concepts"], "addendum 1 comparison", "analysis/results/h4_apalachee/h4_summary.json")
    h1s = json.load(open(os.path.join(A, "results", "h1_hitchiti", "h1_summary.json")))
    for k, cset in (("all_shared", "28 shared concepts"), ("residue", "6 Hitchiti residue concepts")):
        d = dict(h1s[k]); d["verdict"] = "H0 retained" if not d["ruleset_A"] else "lead"
        trow(f"GEORGIA_HITCHITI_{k}_SCA", "H1 (Georgia-era check)", "HITCHITI_1884", "TIMUCUA", cset, "SCA", d,
             "addendum 2, descriptive", "analysis/results/h1_hitchiti/h1_summary.json")
    cal = rd("validation", "placebo_and_calibration.csv")
    for r in cal[cal.analysis.str.startswith("calibration")].itertuples():
        a_, b_ = r.analysis.replace("calibration: ", "").split(" x ")
        d = r._asdict(); d["verdict"] = "detected" if r.focal_p_max < 0.05 else "not detected"
        trow(f"CAL_{a_}_x_{b_}", "calibration", a_, b_, f"{r.n_concepts} shared concepts", r.measure, d,
             "validation (before freezing)", "analysis/validation/placebo_and_calibration.csv")
    tests = pd.DataFrame(tests)
    for c in ("Delta_S", "Z", "P_Perm", "P_Row", "P_Col", "P_Max"):
        tests[c] = pd.to_numeric(tests[c]).round(4)
    tests["N_Items"] = pd.to_numeric(tests.N_Items).astype("Int64")

    # ------------------------------------------------------------------- candidates
    cand = []
    for L, fn in (("MIKASUKI", "candidates_mikasuki.csv"), ("CREEK", "candidates_creek.csv")):
        for r in rd("results", fn).itertuples():
            cand.append(dict(Direction="Timucua -> Muskogean", Recipient=L, Donor="TIMUCUA",
                             Parameter_ID=str(r.parameter_id), Recipient_Form=seg2form(r.recipient_form),
                             Donor_Form=seg2form(r.timucua_form), SCA=r.sim, Rank=r.rank_among_timucua_concepts,
                             N=r.n_timucua_concepts, P_Candidate=r.p_candidate, P_BH=r.p_bh,
                             Status=f"pre-registered; tier {getattr(r, 'tier', '')}"))
    inh = grid.all_forms()["MUSK_INHERITED"]
    for r in rd("results", "h3_timucua_items.csv").itertuples():
        pid = next(k for k, v in gloss.items() if v == r.concept)
        tf = r.timucua.split(" | ")
        best = max(((sim_sca(x, y), x, y) for x in tf for y in inh.get(pid, [])), default=(np.nan, tf[0], ""))
        cand.append(dict(Direction="Muskogean -> Timucua", Recipient="TIMUCUA", Donor="MUSK_INHERITED",
                         Parameter_ID=pid, Recipient_Form=seg2form(best[1]), Donor_Form=seg2form(best[2]),
                         SCA=r.sim, Rank=np.nan, N=np.nan, P_Candidate=round(r.p_candidate, 4), P_BH=np.nan,
                         Status="H3 descriptive count (post hoc lead if p <= 0.05)"))
    for r in rd("results", "h4_apalachee", "apalachee_candidates.csv").itertuples():
        pid = next(k for k, v in gloss.items() if v == r.concept)
        cand.append(dict(Direction="Timucua -> Apalachee", Recipient="APALACHEE", Donor="TIMUCUA", Parameter_ID=pid,
                         Recipient_Form=r.apalachee, Donor_Form=r.timucua, SCA=r.sim, Rank=r.rank, N=r.n_timucua,
                         P_Candidate=r.p_candidate, P_BH=np.nan, Status="addendum 1, descriptive"))
    for r in rd("results", "h1_hitchiti", "hitchiti_candidates.csv").itertuples():
        pid = next(k for k, v in gloss.items() if v == r.concept)
        cand.append(dict(Direction="Timucua -> Hitchiti", Recipient="HITCHITI_1884", Donor="TIMUCUA",
                         Parameter_ID=pid, Recipient_Form=r.hitchiti, Donor_Form=r.timucua, SCA=r.sim, Rank=r.rank,
                         N=87, P_Candidate=r.p_candidate, P_BH=np.nan, Status="addendum 2, descriptive"))
    cand = pd.DataFrame(cand)
    cand.insert(0, "ID", [f"cand-{i + 1}" for i in range(len(cand))])
    for c in ("Rank", "N"):
        cand[c] = pd.to_numeric(cand[c]).astype("Int64")

    # ------------------------------------------------------------------- place names
    pn = rd("gazetteer", "place_name_gazetteer.csv", dtype=str).fillna("")
    pn.insert(0, "ID", [f"place-{i + 1}" for i in range(len(pn))])
    pn.columns = ["ID"] + ["_".join(w.capitalize() for w in c.split("_")) for c in pn.columns[1:]]

    # ------------------------------------------------------------------- write CLDF
    for fn in os.listdir(OUT):
        os.remove(os.path.join(OUT, fn))
    ds = Wordlist.in_dir(OUT)
    ds.add_component("LanguageTable", "Family", "Role", "Data_Source")
    ds.add_component("ParameterTable",
                     {"name": "Concepticon_ID", "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#concepticonReference"},
                     "Concepticon_Gloss", "Stratum",
                     {"name": "WOLD_Borrowed_Score", "datatype": "decimal"},
                     {"name": "Mikasuki_Residue", "datatype": "boolean"},
                     {"name": "Creek_Residue", "datatype": "boolean"})
    ds.add_component("CognateTable", "Method", "Run")
    ds.add_columns("FormTable", {"name": "Value", "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#value"},
                   "Original_Segments", "Normalization",
                   {"name": "Loose_Mapping", "datatype": "boolean"},
                   {"name": "Muskogean_Residue", "datatype": "boolean"},
                   {"name": "European_Flag", "datatype": "boolean"},
                   {"name": "Strict_Residue", "datatype": "boolean"},
                   "Expert_Muskogean_Cognate")
    ds.add_table("comparisons.csv",
                 {"name": "ID", "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#id"},
                 {"name": "Language_ID", "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#languageReference"},
                 {"name": "Parameter_ID", "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#parameterReference"},
                 {"name": "Form_ID", "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#formReference"},
                 "Timucua_Form_ID", "Form", "Timucua_Form",
                 {"name": "SCA", "datatype": "decimal"}, {"name": "NED", "datatype": "decimal"},
                 {"name": "TPG", "datatype": "integer"}, {"name": "Rank_SCA", "datatype": "integer"},
                 {"name": "N_Timucua_Concepts", "datatype": "integer"}, {"name": "P_Candidate", "datatype": "decimal"},
                 "Analysis_Status")
    ds.add_foreign_key("comparisons.csv", "Timucua_Form_ID", "FormTable", "ID")
    ds.add_table("tests.csv",
                 {"name": "ID", "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#id"},
                 "Hypothesis", "Recipient", "Donor", "Concept_Set", "Measure",
                 {"name": "N_Items", "datatype": "integer"},
                 *[{"name": c, "datatype": "decimal"} for c in ("Delta_S", "Z", "P_Perm", "P_Row", "P_Col", "P_Max")],
                 {"name": "Ruleset_A", "datatype": "boolean"}, {"name": "Ruleset_B", "datatype": "boolean"},
                 "Verdict", "Status", "Result_File")
    ds.add_table("candidates.csv",
                 {"name": "ID", "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#id"},
                 "Direction", "Recipient", "Donor",
                 {"name": "Parameter_ID", "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#parameterReference"},
                 "Recipient_Form", "Donor_Form", {"name": "SCA", "datatype": "decimal"},
                 {"name": "Rank", "datatype": "integer"}, {"name": "N", "datatype": "integer"},
                 {"name": "P_Candidate", "datatype": "decimal"}, {"name": "P_BH", "datatype": "decimal"}, "Status")
    ds.add_table("place_names.csv", {"name": "ID", "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#id"},
                 *pn.columns[1:])

    bib = open(os.path.join(A, "cldf", "sources.bib")).read() + BIB_EXTRA
    open(os.path.join(OUT, "sources.bib"), "w").write(bib)
    ds.add_sources(*__import__("pycldf").sources.Sources.from_file(os.path.join(OUT, "sources.bib")))

    def recs(df):
        df = df.astype(object).where(pd.notna(df), None)
        out = df.to_dict("records")
        for r in out:
            if "Segments" in r and isinstance(r["Segments"], str):
                r["Segments"] = r["Segments"].split()
            if "Source" in r and isinstance(r["Source"], str):
                r["Source"] = [r["Source"]] if r["Source"] else []
        return out

    ds.write(LanguageTable=recs(langs[["ID", "Name", "Macroarea", "Latitude", "Longitude", "Glottocode",
                                       "Family", "Role", "Data_Source"]]),
             ParameterTable=recs(params), FormTable=recs(forms), CognateTable=recs(cognates),
             **{"comparisons.csv": recs(comp), "tests.csv": recs(tests), "candidates.csv": recs(cand),
                "place_names.csv": recs(pn)})
    ds.validate()

    # ------------------------------------------------------------------- wide tables
    order = ["TIMUCUA"] + SOUTHEAST
    names = dict(zip(langs.ID, langs.Name))
    w = forms[forms.Language_ID.isin(order)].groupby(["Parameter_ID", "Language_ID"]).Form.apply(" / ".join).unstack()
    w = w.reindex(columns=order).rename(columns=names)
    w.insert(0, "Concept", [gloss[c] for c in w.index])
    w = w.loc[sorted(w.index, key=int)]
    w.to_csv(os.path.join(TABLES, "southeast_wordlist.csv"), index_label="Parameter_ID")
    cw = comp.assign(Cell=comp.Form + " (" + comp.SCA.map("{:.2f}".format) + ", p=" +
                     comp.P_Candidate.map("{:.3f}".format) + ")")
    cw = cw.pivot(index="Parameter_ID", columns="Language_ID", values="Cell").reindex(columns=SOUTHEAST)
    cw = cw.rename(columns=names)
    tim = forms[forms.Language_ID == "TIMUCUA"].groupby("Parameter_ID").Form.apply(" / ".join)
    cw.insert(0, "Timucua", tim.reindex(cw.index)); cw.insert(0, "Concept", [gloss[c] for c in cw.index])
    cw = cw.loc[sorted(cw.index, key=int)]
    cw.to_csv(os.path.join(TABLES, "timucua_comparisons_wide.csv"), index_label="Parameter_ID")
    print(f"languages {len(langs)}, concepts {len(params)}, forms {len(forms)}, cognate judgments {len(cognates)}, "
          f"comparisons {len(comp)}, tests {len(tests)}, candidates {len(cand)}, place names {len(pn)}")


if __name__ == "__main__":
    main()
