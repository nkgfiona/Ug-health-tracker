# load2_data.py
# ─────────────────────────────────────────────────────────────────────────────
# Fetches all star schema dimension and fact tables from PostgreSQL
# into pandas DataFrames for direct use or inspection.
#
# Database : imdb
# Schema   : public
# Tables   : patient, "date", hospital, doctor, medical_condition,
#            medication, insurance, admission_type, test_results,
#            fact_patient_visits
# ─────────────────────────────────────────────────────────────────────────────
import sys
import os
import pandas as pd
from database_connection import get_engine
 
 
# ── Dynamic Path Helper ─────────────────────────────────────────────────────
# This tells Python to look in the parent directory (02_phase1_health_database)
# so it can easily find 'database_connection.py'.
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

def fetch_tables_from_postgres(schema="public"):
    """
    Connects to PostgreSQL and loads all star schema tables
    directly into pandas DataFrames.

    Arguments:
        schema (str) : which schema to read from (default: public)

    Returns:
        dict: keys are table names, values are DataFrames.
              Empty DataFrame stored for any table that fails to load.
    """

    # ── Table list ────────────────────────────────────────────────────────────
    # IMPORTANT: 'date' is a reserved word in PostgreSQL.
    # It must be wrapped in double-quotes in every SQL query.
    tables_to_fetch = [
        "patient",
        "date",              # reserved word — quoted automatically below
        "hospital",
        "doctor",
        "medical_condition",
        "medication",
        "insurance",
        "admission_type",
        "test_results",
        "district",          # NEW: district table
        "fact_patient_visits",
    ]

    dataframes = {}

    engine = get_engine()

    print(f"Connecting to database to fetch tables from schema '{schema}'...\n")

    for table_name in tables_to_fetch:
        print(f"  Reading: {schema}.\"{table_name}\"...")
        try:
            # Always wrap table name in double-quotes.
            # This safely handles reserved words like 'date' and
            # any table name that contains uppercase or special characters.
            query = f'SELECT * FROM {schema}."{table_name}"'

            df = pd.read_sql(query, con=engine)

            dataframes[table_name] = df
            print(f"     Loaded: {df.shape[0]:,} rows x {df.shape[1]} columns")

        except Exception as e:
            print(f"     ERROR loading '{table_name}': {e}")
            dataframes[table_name] = pd.DataFrame()

    engine.dispose()

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "-" * 50)
    print("FETCH COMPLETE — Table Summary")
    print("-" * 50)
    for name, df in dataframes.items():
        status = (f"{df.shape[0]:>6,} rows x {df.shape[1]:>2} cols"
                  if not df.empty else "  FAILED — empty DataFrame")
        print(f"  {name:<25} {status}")
    print("-" * 50)

    return dataframes


def preview_fact_table(dataframes):
    """
    Prints the first 5 rows of the fact table and its column names.
    Useful for verifying the schema after loading.
    """
    fact = dataframes.get("fact_patient_visits", pd.DataFrame())

    if fact.empty:
        print("\nfact_patient_visits did not load. Check the table exists in imdb.")
        return

    print("\n=== fact_patient_visits — first 5 rows ===")
    print(fact.head(5).to_string())
    print(f"\nColumns: {list(fact.columns)}")


def preview_all_dimensions(dataframes):
    """
    Prints the first 3 rows of each dimension table.
    Useful for confirming key column names before writing JOIN queries.
    """
    dims = [t for t in dataframes if t != "fact_patient_visits"]

    print("\n=== DIMENSION TABLE PREVIEWS ===")
    for name in dims:
        df = dataframes[name]
        if df.empty:
            print(f"\n  [{name}] — empty / failed to load")
            continue
        print(f"\n  [{name}] — {df.shape[0]:,} rows")
        print(f"  Columns : {list(df.columns)}")
        print(df.head(3).to_string(index=False))


# ─────────────────────────────────────────────────────────────────────────────
# Run directly to verify all tables load correctly
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    db_tables = fetch_tables_from_postgres(schema="public")
    preview_fact_table(db_tables)
    preview_all_dimensions(db_tables)