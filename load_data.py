# load_data.py
# Loads our cleaned health CSV into a PostgreSQL table

import pandas as pd
from database_connection import get_engine

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

    # Get the SQLAlchemy engine
    engine = get_engine()

    print(f"\nUploading to PostgreSQL table '{schema}.{table_name}'...")

    # to_sql() uploads the entire DataFrame to PostgreSQL
    # if_exists='replace' : drops and recreates the table each time
    # if_exists='append'  : adds rows to an existing table
    # if_exists='fail'    : raises an error if the table already exists
    # index=False         : do not write the DataFrame's row numbers as a column
    df.to_sql(
        name      = table_name,
        con       = engine,
        schema    = schema,
        if_exists = "replace",
        index     = False
    )

    print(f"✅ Upload complete! {df.shape[0]} rows written to '{schema}.{table_name}' in PostgreSQL.")
    print(f"   Table '{schema}.{table_name}' now exists in health_db.")

    # Verify by reading back a few rows
    print(f"\nVerifying_upload by reading back 3 rows from '{schema}.{table_name}'...")
    verification = pd.read_sql(
        f'SELECT * FROM {schema}."{table_name}" LIMIT 3',
        engine
    )
    print(verification)

    engine.dispose()  # close all connections in the pool


if __name__ == "__main__":
    # Change the filename below to match your actual CSV file
    load_csv_to_postgres(
        csv_filepath = "hospital_patients.csv",   # ← change to your filename
        table_name   = "hospital_patients",
        schema       = "public"
    )