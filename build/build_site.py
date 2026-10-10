"""Build the project website (docs/index.html) from the CLDF database and the pilot results.

The page is one self-contained file: build/site/template.html with site.css, site.js and the data
payload inlined, so it works from GitHub Pages (Settings -> Pages -> main, /docs) and when opened
straight from disk. Run from the repo root after build_db.py:

    python3 build/build_site.py
"""
import base64
import datetime
import json
import os
import re

import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLDF = os.path.join(REPO, "cldf")
A = os.path.join(REPO, "analysis")
SITE = os.path.join(REPO, "build", "site")
OUT = os.path.join(REPO, "docs")

SOUTHEAST = ["TIMUCUA", "MIKASUKI", "HITCHITI_1884", "HITCHITI_1937", "CREEK", "ALABAMA", "KOASATI", "APALACHEE",
             "CHOCTAW", "CHICKASAW", "PROTO_MUSKOGEAN"]
NICE = {"PROTO_MUSKOGEAN": "Proto-Muskogean", "MOBILIAN_JARGON": "Mobilian Jargon", "MUSK_INHERITED": "Muskogean (inherited)"}


def nice(lid, name=None):
    if lid in NICE:
        return NICE[lid]
    if name and not name.isupper() and "_" not in name:
        return name
    return re.sub(r"\s\d+$", "", lid.replace("_", " ").title())


def rd(*p, **kw):
    return pd.read_csv(os.path.join(*p), **kw)


def clean(v):
    if isinstance(v, float) and pd.isna(v):
        return None
    if hasattr(v, "item"):
        return v.item()
    return v


def records(df):
    return [{k: clean(v) for k, v in r.items()} for r in df.to_dict("records")]


def main():
    langs = rd(CLDF, "languages.csv")
    params = rd(CLDF, "parameters.csv"); params["ID"] = params.ID.astype(str)
    forms = rd(CLDF, "forms.csv"); forms["Parameter_ID"] = forms.Parameter_ID.astype(str)
    cog = rd(CLDF, "cognates.csv")
    comp = rd(CLDF, "comparisons.csv"); comp["Parameter_ID"] = comp.Parameter_ID.astype(str)
    tests = rd(CLDF, "tests.csv")
    cand = rd(CLDF, "candidates.csv"); cand["Parameter_ID"] = cand.Parameter_ID.astype(str)
    places = rd(CLDF, "place_names.csv", dtype=str).fillna("")

    counts = forms.groupby("Language_ID").size()
    lang_out = [dict(id=r.ID, name=nice(r.ID, r.Name), family=clean(r.Family), role=r.Role,
                     macroarea=clean(r.Macroarea), glottocode=clean(r.Glottocode), source=clean(r.Data_Source),
                     n=int(counts.get(r.ID, 0)))
                for r in langs.itertuples()]

    concepts = [dict(id=r.ID, name=r.Name, gloss=clean(r.Concepticon_Gloss), stratum=clean(r.Stratum),
                     wold=clean(r.WOLD_Borrowed_Score), mres=bool(r.Mikasuki_Residue), cres=bool(r.Creek_Residue))
                for r in params.itertuples()]

    # cognate set per form: the Hitchiti rerun covers the six ASJP Muskogean lists plus Gatschet's Hitchiti
    h1 = cog[(cog.Run.str.startswith("stage2_h1")) & (cog.Method == "LexStat")]
    cset = dict(zip(h1.Form_ID, h1.Cognateset_ID.str.replace("h1-lexstat-", "", regex=False)))
    se = forms[forms.Language_ID.isin(SOUTHEAST)]
    form_out = []
    for r in se.itertuples():
        form_out.append(dict(
            id=r.ID, l=r.Language_ID, c=r.Parameter_ID, v=clean(r.Value), f=r.Form,
            src=clean(r.Source), res=clean(r.Muskogean_Residue), strict=clean(r.Strict_Residue),
            loose=bool(r.Loose_Mapping) if pd.notna(r.Loose_Mapping) else False,
            expert=clean(r.Expert_Muskogean_Cognate), note=clean(r.Comment), cog=cset.get(r.ID)))

    comp_out = [dict(l=r.Language_ID, c=r.Parameter_ID, f=r.Form, t=r.Timucua_Form, sca=r.SCA, ned=r.NED,
                     tpg=int(r.TPG), rank=int(r.Rank_SCA), n=int(r.N_Timucua_Concepts), p=r.P_Candidate,
                     status=r.Analysis_Status) for r in comp.itertuples()]

    cand_out = records(cand.rename(columns={"Parameter_ID": "c"}))
    test_out = records(tests)

    place_out = records(places)

    # ranking strips for the confirmatory test (H2, Mikasuki residue, SCA)
    tw = rd(A, "results", "twoway_H2_MIKASUKI_SCA.csv")
    fam = dict(zip(langs.ID, langs.Family)); macro = dict(zip(langs.ID, langs.Macroarea))
    donors = [dict(id=r.col, name=nice(r.col), family=clean(fam.get(r.col)), macro=clean(macro.get(r.col)),
                   score=round(r.interaction, 3), z=round(r.z, 2), dS=round(r.dS, 3), focal=r.col == "TIMUCUA")
              for r in tw[tw.row == "MIKASUKI"].itertuples()]
    recips = [dict(id=r.row, name=nice(r.row), family=clean(fam.get(r.row)), macro=clean(macro.get(r.row)),
                   score=round(r.interaction, 3), z=round(r.z, 2), dS=round(r.dS, 3), focal=r.row == "MIKASUKI")
              for r in tw[tw.col == "TIMUCUA"].itertuples()]

    rates = rd(A, "results", "stage2_residue_rates_by_language.csv")
    rates_out = [dict(id=r.Language_ID, name=nice(r.Language_ID), rate=r.residue_concept_rate,
                      n=int(r.residue_concepts), of=int(r.concepts)) for r in rates.itertuples()]

    power = rd(A, "validation", "power_grid.csv")
    gaz_counts = places.Survives.value_counts().to_dict()

    data = dict(
        built=datetime.date.today().isoformat(),
        counts=dict(languages=len(langs), concepts=len(params), forms=len(forms), cognates=len(cog),
                    comparisons=len(comp), tests=len(tests), candidates=len(cand), places=len(places)),
        languages=lang_out, concepts=concepts, forms=form_out, comparisons=comp_out, tests=test_out,
        candidates=cand_out, places=place_out, donors=donors, recipients=recips, rates=rates_out,
        power=records(power), survives=gaz_counts, southeast=SOUTHEAST)

    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = open(os.path.join(SITE, "template.html"), encoding="utf-8").read()
    html = (html.replace("/*{{CSS}}*/", open(os.path.join(SITE, "site.css"), encoding="utf-8").read())
                .replace("/*{{JS}}*/", open(os.path.join(SITE, "site.js"), encoding="utf-8").read())
                .replace("{{DATA}}", payload)
                .replace("{{BUILT}}", data["built"])
                .replace("{{LOGO}}", "data:image/png;base64," + base64.b64encode(
                    open(os.path.join(SITE, "logo.png"), "rb").read()).decode()))
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(html)
    open(os.path.join(OUT, ".nojekyll"), "w").write("")
    print(f"docs/index.html: {len(html) / 1024:.0f} KB, {len(form_out)} forms, {len(comp_out)} comparisons")


if __name__ == "__main__":
    main()
