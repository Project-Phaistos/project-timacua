#!/usr/bin/env python3
"""Compare rebuilt SQLite logical contents with the committed database."""
import hashlib
import json
import sqlite3
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "db/project-phaistos.sqlite"
OUTPUT = ROOT / "qa/sqlite_rebuild_comparison.json"


def json_value(value):
    if isinstance(value, bytes):
        return {"bytes_sha256": hashlib.sha256(value).hexdigest(), "length": len(value)}
    return value


def snapshot(path):
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        objects = con.execute(
            "SELECT type, name, sql FROM sqlite_master "
            "WHERE name NOT LIKE 'sqlite_%' AND type IN ('table', 'view') "
            "ORDER BY type, name"
        ).fetchall()
        result = {"objects": {}, "tables": {}}
        for kind, name, sql in objects:
            result["objects"][f"{kind}:{name}"] = sql
            if kind != "table":
                continue
            columns = [r[1] for r in con.execute(f'PRAGMA table_info("{name}")')]
            rows = con.execute(f'SELECT * FROM "{name}"').fetchall()
            normalized = [tuple(json_value(v) for v in row) for row in rows]
            normalized.sort(key=lambda row: json.dumps(row, ensure_ascii=False, sort_keys=True, default=str))
            payload = json.dumps(normalized, ensure_ascii=False, sort_keys=True, default=str).encode()
            result["tables"][name] = {
                "rows": len(rows), "columns": columns, "content_sha256": hashlib.sha256(payload).hexdigest()
            }
        return result
    finally:
        con.close()


def main():
    original = subprocess.run(
        ["git", "show", "HEAD:db/project-phaistos.sqlite"],
        cwd=ROOT, check=True, capture_output=True
    ).stdout
    with tempfile.NamedTemporaryFile(suffix=".sqlite") as tmp:
        tmp.write(original)
        tmp.flush()
        before = snapshot(tmp.name)
    after = snapshot(CURRENT)

    table_names = sorted(set(before["tables"]) | set(after["tables"]))
    changed = []
    for name in table_names:
        if before["tables"].get(name) != after["tables"].get(name):
            changed.append(name)
    object_names = sorted(set(before["objects"]) | set(after["objects"]))
    changed_objects = [name for name in object_names if before["objects"].get(name) != after["objects"].get(name)]
    report = {
        "committed_database": "HEAD:db/project-phaistos.sqlite",
        "rebuilt_database": "db/project-phaistos.sqlite",
        "logical_tables_identical": not changed,
        "changed_tables": changed,
        "changed_schema_objects": changed_objects,
        "committed_tables": before["tables"],
        "rebuilt_tables": after["tables"],
        "scope": "Logical table contents and SQLite object definitions; binary file identity is not required.",
    }
    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"SQLite logical tables identical: {not changed}")
    print(f"Changed tables: {changed or 'none'}")
    print(f"Changed schema objects: {changed_objects or 'none'}")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
