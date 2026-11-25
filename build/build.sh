#!/usr/bin/env bash
# Rebuild the whole database from analysis/ (run from the repo root).
set -euo pipefail

# The source package is stored as a zip to keep the repository compact.
# Extract it on first build; reject paths outside the repository.
if [[ ! -d analysis ]]; then
  if [[ ! -f analysis_all.zip ]]; then
    echo "Missing analysis/ and analysis_all.zip; cannot rebuild." >&2
    exit 1
  fi
  python3 - <<'PY'
from pathlib import Path
from zipfile import ZipFile

archive = Path("analysis_all.zip")
root = Path.cwd().resolve()
with ZipFile(archive) as zf:
    members = zf.namelist()
    if not members or any(not name.startswith("analysis/") for name in members):
        raise SystemExit("Unexpected archive layout: expected every entry under analysis/")
    for name in members:
        target = (root / name).resolve()
        if target != root and root not in target.parents:
            raise SystemExit(f"Unsafe archive member: {name}")
    zf.extractall(root)
if not (root / "analysis" / "src" / "common.py").is_file():
    raise SystemExit("Archive extraction did not produce analysis/src/common.py")
PY
fi

python3 build/build_db.py
cldf validate cldf/Wordlist-metadata.json
rm -f db/project-phaistos.sqlite
cldf createdb cldf/Wordlist-metadata.json db/project-phaistos.sqlite
python3 - <<'PY'
import sqlite3
con = sqlite3.connect("db/project-phaistos.sqlite")
con.executescript(open("db/views.sql").read())
con.commit()
print("views:", [r[0] for r in con.execute("select name from sqlite_master where type='view'")])
PY
python3 build/build_site.py
