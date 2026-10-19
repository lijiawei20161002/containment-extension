"""Write the incident library to incidents/: records, JSON schema, taxonomy, and a DuckDB file.

Usage: python3 scripts/build_incident_library.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "src"))
from containment_extension.incident_library import RECORDS_DIR, json_schema, taxonomy, to_duckdb, write_record  # noqa: E402
from incident_codings import records  # noqa: E402

ROOT = HERE.parent / "incidents"

if __name__ == "__main__":
    recs = records()
    for old in RECORDS_DIR.glob("*.json"):
        old.unlink()
    for r in recs:
        write_record(r)
    (ROOT / "schema").mkdir(parents=True, exist_ok=True)
    (ROOT / "schema" / "incident.schema.json").write_text(json.dumps(json_schema(), indent=1), encoding="utf-8")
    (ROOT / "taxonomy.json").write_text(json.dumps(taxonomy(), indent=1, ensure_ascii=False), encoding="utf-8")
    db = ROOT / "incidents.duckdb"
    if db.exists():
        db.unlink()
    con = to_duckdb(recs, db)
    n = con.execute("SELECT count(*) FROM incidents").fetchone()[0]
    con.close()
    print(f"wrote {len(recs)} records, schema, taxonomy, duckdb ({n} rows) under {ROOT}")
