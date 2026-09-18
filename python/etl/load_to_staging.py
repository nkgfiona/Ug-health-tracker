# load_to_staging.py
# Loads a cleaned health CSV into a PostgreSQL staging table.
#
# NOTE: this writes a single flat table (e.g. "hospital_patients") using
# pandas to_sql() it is a STAGING step. It does not populate the star
# schema tables defined in sql/schema.sql (patient, hospital, doctor,
# fact_patient_visits, etc.) on its own. See the project README for how
# the staging table feeds into the star schema.

import pandas as pd
from db_connection import get_engine


def load_csv_to_postgres(csv_filepath, table_name, schema="public"):
    """
    Reads a CSV file into a pandas DataFrame and uploads it
    to a PostgreSQL table using the to_sql() method.

    Arguments:
        csv_filepath (str) : path to your CSV file
        table_name   (str) : what to name the table in PostgreSQL
        schema       (str) : which schema to put it in (default: public)
    """

    print(f"Reading CSV file: {csv_filepath}")
    df = pd.read_csv(csv_filepath)

    print(f"CSV loaded. Shape: {df.shape[0]} rows x {df.shape[1]} columns")
    print(f"Columns: {list(df.columns)}")
    print("\nFirst 3 rows:")
    print(df.head(3))

    engine = get_engine()

    print(f"\nUploading to PostgreSQL table '{schema}.{table_name}'...")
    df.to_sql(
        name=table_name,
        con=engine,
        schema=schema,
        if_exists="replace",
        index=False
    )

    print(f"Upload complete! {df.shape[0]} rows written to '{schema}.{table_name}' in PostgreSQL.")
    print(f"   Table '{schema}.{table_name}' now exists in uganda_health_db.")

    print(f"\nVerifying upload by reading back 3 rows from '{schema}.{table_name}'...")
    verification = pd.read_sql(
        f'SELECT * FROM {schema}."{table_name}" LIMIT 3',
        engine
    )
    print(verification)

    engine.dispose()


if __name__ == "__main__":
    load_csv_to_postgres(
        csv_filepath="../../data/raw/hospital_patients.csv",
        table_name="hospital_patients_staging",
        schema="public"
    )
