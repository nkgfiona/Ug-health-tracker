# db_connection.py
# ─────────────────────────────────────────────────────────────────────────
# Shared PostgreSQL connection helper for the Uganda Health Tracker
# star-schema database (see sql/schema.sql).
# ─────────────────────────────────────────────────────────────────────────

import config
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


def get_engine():
    """Creates and returns a SQLAlchemy engine for the health database."""
    connection_string = (
        f"postgresql+psycopg2://"
        f"{config.DB_USER}:{config.DB_PASSWORD}"
        f"@{config.DB_HOST}:{config.DB_PORT}"
        f"/{config.DB_NAME}"
    )
    return create_engine(connection_string)


def test_connection():
    """Tries to connect to PostgreSQL and prints a success or error message."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database(), current_user;"))
            row = result.fetchone()
            print("Connection successful!")
            print(f"   Database : {row[0]}")
            print(f"   User     : {row[1]}")
            print(f"   Host     : {config.DB_HOST}:{config.DB_PORT}")
        engine.dispose()
    except SQLAlchemyError as error:
        print(f"Connection failed: {error}")


def run_query(sql_query, params=None):
    """
    Runs a SQL query against PostgreSQL and returns the result as a
    pandas DataFrame (empty DataFrame if something went wrong).
    """
    engine = get_engine()
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text(sql_query), conn, params=params or {})
    finally:
        engine.dispose()
    return df

if __name__ == "__main__":
    print("Testing PostgreSQL connection...")
    test_connection()

    print("\nTesting a simple query...")
    result = run_query("SELECT current_database() AS database_name, current_user AS username;")
    print(result)
