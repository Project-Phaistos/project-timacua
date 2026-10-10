#!/usr/bin/env bash
# Rebuild the whole database from analysis/ (run from the repo root).
set -euo pipefail
python3 build/build_db.py
cldf validate cldf/Wordlist-metadata.json
rm -f db/project-phaistos.sqlite
cldf createdb cldf/Wordlist-metadata.json db/project-phaistos.sqlite
python3 - <<'EOF'
import sqlite3
con = sqlite3.connect("db/project-phaistos.sqlite")
con.executescript(open("db/views.sql").read())
con.commit()
print("views:", [r[0] for r in con.execute("select name from sqlite_master where type='view'")])
EOF
python3 build/build_site.py
