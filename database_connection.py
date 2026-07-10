# database_connection.py

import sys
import pandas as pd
from sqlalchemy import create_engine, text
import config


# ─────────────────────────────────────────────
# FUNCTION 1: Get a SQLAlchemy engine
# ─────────────────────────────────────────────
def get_engine():
    """
    Creates and returns a SQLAlchemy engine.
    All other functions use this as their connection.
    """
    # Look at which script was executed in the terminal
    main_script_running =sys.argv[0]
    
    # If main2.py or analysis2_from_db.py is running, use 'imdb'
    if "2" in main_script_running:
        target_db = "imdb"
    else:
        # Otherwise, fallback to your flat table database (e.g., health_db)
        target_db = "health_db"
        
    connection_string = (
        f"postgresql+psycopg2://"
        f"{config.DB_USER}:{config.DB_PASSWORD}"
        f"@{config.DB_HOST}:{config.DB_PORT}"
        f"/{target_db}"
    )
    engine = create_engine(connection_string)
    return engine


# ─────────────────────────────────────────────
# FUNCTION 2: Test the connection
# ─────────────────────────────────────────────
def test_connection():
    """
    Tries to connect to PostgreSQL and prints a success or error message.
    """
    try:
        engine = get_engine()

        # text() wraps raw SQL strings — required by SQLAlchemy 2.0+
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database(), current_user;"))
            row = result.fetchone()
            print("✅ Connection successful!")
            print(f"   Database : {row[0]}")
            print(f"   User     : {row[1]}")
            print(f"   Host     : {config.DB_HOST}:{config.DB_PORT}")

        engine.dispose()

    except Exception as error:
        print(f"❌ Connection failed: {error}")


# ─────────────────────────────────────────────
# FUNCTION 3: Run a query, return a DataFrame
# ─────────────────────────────────────────────
def run_query(sql_query, params=None):
    """
    Takes a SQL query string, runs it against PostgreSQL,
    and returns the result as a pandas DataFrame.

    Arguments:
        sql_query (str)   : the SQL you want to run
        params    (tuple) : optional values for parameterised queries

    Returns:
        pandas DataFrame with the query results,
        or an empty DataFrame if something went wrong.
    """
    try:
        engine = get_engine()

        # pandas requires a SQLAlchemy engine — not a raw psycopg2 connection
        df = pd.read_sql(sql_query, engine, params=params)

        engine.dispose()

        print(f"✅ Query returned {len(df)} rows and {len(df.columns)} columns.")
        return df

    except Exception as error:
        print(f"❌ Query failed: {error}")
        return pd.DataFrame()


# ─────────────────────────────────────────────
# TEST: Run this file directly to verify
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing PostgreSQL connection...")
    test_connection()

    print("\nTesting a simple query...")
    result = run_query("SELECT current_database() AS database_name, current_user AS username;")
    print(result)