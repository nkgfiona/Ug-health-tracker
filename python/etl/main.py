# main.py
# ─────────────────────────────────────────────────────────────────────────
# Single entry point for the Uganda Health Tracker pipeline.
# Runs every stage in order:
#   1. Rebuild the star schema        (sql/schema.sql)
#   2. Load the raw CSV into staging  (load_to_staging.py)
#   3. Populate the star schema       (build_star_schema.py)
#   4. Run the analysis               (run_analysis.py)
#
# Each script can still be run on its own for debugging a single stage —
# this just chains them so the whole pipeline reproduces with one command:
#
#   python main.py
# ─────────────────────────────────────────────────────────────────────────

import os

from build_star_schema import build_star_schema
from db_connection import get_engine
from load_to_staging import load_csv_to_postgres
from run_analysis import run_full_analysis

SCHEMA_FILE = os.path.join("..", "..", "sql", "schema.sql")
RAW_CSV = os.path.join("..", "..", "data", "raw", "hospital_patients.csv")


def rebuild_schema():
    """
    Runs sql/schema.sql against the database. The script starts with
    DROP TABLE IF EXISTS ... CASCADE, so this always starts from a clean,
    empty star schema — safe to re-run any time.
    """
    print("Step 1/4: Rebuilding star schema...")
    with open(SCHEMA_FILE, "r") as f:
        schema_sql = f.read()

    engine = get_engine()

    raw_conn = engine.raw_connection()
    try:
        cursor = raw_conn.cursor()
        cursor.execute(schema_sql)
        raw_conn.commit()
        cursor.close()
    finally:
        raw_conn.close()
        engine.dispose()
    print("   Schema rebuilt.\n")


def main():
    print("=" * 50)
    print("  UGANDA HEALTH TRACKER — FULL PIPELINE")
    print("  Database: uganda_health_db")
    print("=" * 50 + "\n")

    rebuild_schema()

    print("Step 2/4: Loading raw CSV into staging table...")
    load_csv_to_postgres(
        csv_filepath=RAW_CSV,
        table_name="hospital_patients_staging",
        schema="public"
    )
    print()

    print("Step 3/4: Building star schema from staging table...")
    build_star_schema()
    print()

    print("Step 4/4: Running analysis...")
    run_full_analysis()

    print("\nPipeline complete.")


if __name__ == "__main__":
    main()
