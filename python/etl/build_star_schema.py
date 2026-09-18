# build_star_schema.py
# ─────────────────────────────────────────────────────────────────────────
# The missing link in the pipeline: takes the flat staging table
# (loaded by load_to_staging.py from the raw CSV) and populates the star
# schema — every dimension table, then the fact table that references them.
# Safe to re-run on its own any number of times: it truncates and resets
# every star schema table first, so it never collides with data from a
# previous run.
#
# Run order:
#   1. psql -d uganda_health_db -f sql/schema.sql      (creates empty tables)
#   2. python load_to_staging.py                       (raw CSV -> staging)
#   3. python build_star_schema.py                     (staging -> star schema)
#   4. python main.py                                  (runs the analysis)
#
# How it works: for each dimension, pull the distinct values out of the
# staging table, insert them, then read the auto-generated surrogate keys
# back out to build a lookup dict (e.g. {"Mulago National Referral
# Hospital": 7}). Those lookups are then used to build the fact table rows,
# swapping every text value for the matching surrogate key.
# ─────────────────────────────────────────────────────────────────────────

import pandas as pd
from db_connection import get_engine

STAGING_TABLE = "hospital_patients_staging"

# Matches the condition list in python/data_generation/generate_synthetic_patients.py.
# If that list changes, update this too.
CONDITION_INFO = {
    "Malaria":       ("Infectious",         "Moderate", "B54"),
    "HIV/AIDS":      ("Infectious",         "Severe",   "B20"),
    "Hypertension":  ("Non-communicable",   "Moderate", "I10"),
    "Tuberculosis":  ("Infectious",         "Severe",   "A15"),
    "Pneumonia":     ("Infectious",         "Moderate", "J18"),
    "Heart Failure": ("Non-communicable",   "Severe",   "I50"),
    "Diabetes":      ("Non-communicable",   "Moderate", "E11"),
    "Typhoid Fever": ("Infectious",         "Moderate", "A01.0"),
}

MEDICATION_INFO = {
    "Artemether-Lumefantrine":            ("Antimalarial",   "Antimalarial combination", "Prescription"),
    "Tenofovir-Lamivudine-Dolutegravir":  ("Antiretroviral", "ARV combination",          "Prescription"),
    "Amlodipine":                         ("Antihypertensive", "Calcium channel blocker", "Prescription"),
    "Rifampicin-Isoniazid":               ("Antitubercular", "TB combination therapy",   "Prescription"),
    "Amoxicillin":                        ("Antibiotic",     "Penicillin",               "Prescription"),
    "Furosemide":                         ("Diuretic",       "Loop diuretic",             "Prescription"),
    "Metformin":                          ("Antidiabetic",   "Biguanide",                 "Prescription"),
    "Ciprofloxacin":                      ("Antibiotic",     "Fluoroquinolone",           "Prescription"),
}

ADMISSION_PRIORITY = {"Emergency": 1, "Urgent": 2, "Elective": 3}

TEST_RESULT_INFO = {
    "Abnormal":     ("Requires follow-up", 2),
    "Inconclusive": ("Requires follow-up", 1),
    "Normal":       ("No action needed",   0),
}


def load_staging(engine):
    print(f"Reading staging table '{STAGING_TABLE}'...")
    df = pd.read_sql(f'SELECT * FROM public."{STAGING_TABLE}"', engine)
    print(f"   {len(df)} rows loaded.")
    return df


def build_date_dim(df, engine):
    """Every unique admission/discharge date becomes one date-dimension row."""
    all_dates = pd.to_datetime(
        pd.concat([df["date_of_admission"], df["discharge_date"]]),
        dayfirst=True
    ).drop_duplicates().sort_values()

    date_rows = pd.DataFrame({
        "date_key": all_dates.dt.strftime("%Y%m%d").astype(int),
        "full_date": all_dates.dt.date,
        "year": all_dates.dt.year,
        "quarter": all_dates.dt.quarter,
        "month": all_dates.dt.month,
        "month_name": all_dates.dt.month_name(),
        "day": all_dates.dt.day,
        "day_of_week": all_dates.dt.dayofweek,
        "day_name": all_dates.dt.day_name(),
        "week_of_year": all_dates.dt.isocalendar().week,
        "is_weekend": all_dates.dt.dayofweek >= 5,
        "is_holiday": False,  # no Uganda public holiday calendar wired in yet
    })

    date_rows.to_sql("date", engine, schema="public", if_exists="append", index=False)
    print(f"   date: {len(date_rows)} rows inserted.")
    return dict(zip(all_dates.dt.strftime("%d/%m/%Y"), date_rows["date_key"]))


def build_simple_dim(df, engine, source_col, table, name_col, key_col, extra_cols=None, info_map=None):
    """
    Generic dimension loader: takes the distinct values in `source_col`,
    inserts them into `table`, and returns a {value: surrogate_key} lookup.
    `key_col` must match the table's actual primary key column name — most
    tables use `<table>_key`, but medical_condition (condition_key),
    admission_type (admission_key), and test_results (test_key) don't.
    `info_map`, if given, supplies the extra descriptive columns per value.
    """
    values = df[source_col].dropna().unique()
    rows = []
    for v in values:
        row = {name_col: v}
        if info_map and v in info_map:
            for col, val in zip(extra_cols, info_map[v]):
                row[col] = val
        rows.append(row)

    dim_df = pd.DataFrame(rows)
    dim_df.to_sql(table, engine, schema="public", if_exists="append", index=False)

    lookup_df = pd.read_sql(
        f'SELECT {key_col}, {name_col} FROM public."{table}"', engine
    )
    print(f"   {table}: {len(dim_df)} rows inserted.")
    return dict(zip(lookup_df[name_col], lookup_df[key_col]))


def build_patient_dim(df, engine):
    age_bounds = {
        "Under 18": (0, 17), "18-35": (18, 35),
        "36-60": (36, 60), "Over 60": (61, 120),
    }
    patients = df[["patient_id", "name", "gender", "blood_type", "age_group"]].drop_duplicates(subset="patient_id")
    patients = patients.rename(columns={"name": "full_name"})
    patients["age_range_start"] = patients["age_group"].map(lambda g: age_bounds.get(g, (None, None))[0])
    patients["age_range_end"] = patients["age_group"].map(lambda g: age_bounds.get(g, (None, None))[1])

    patients.to_sql("patient", engine, schema="public", if_exists="append", index=False)
    print(f"   patient: {len(patients)} rows inserted.")

    lookup_df = pd.read_sql('SELECT patient_key, patient_id FROM public.patient', engine)
    return dict(zip(lookup_df["patient_id"], lookup_df["patient_key"]))


def build_doctor_dim(df, engine):
    """
    This dimension was missing entirely in the first version of this script —
    fact_patient_visits.doctor_key was never populated, which is why doctor
    queries (e.g. run_analysis.py's q6_doctors) returned zero rows.
    specialty/department aren't in the source data, so they're left NULL.
    """
    doctors = df[["doctor"]].drop_duplicates()
    doctors = doctors.rename(columns={"doctor": "doctor_name"})

    doctors.to_sql("doctor", engine, schema="public", if_exists="append", index=False)
    print(f"   doctor: {len(doctors)} rows inserted.")

    lookup_df = pd.read_sql('SELECT doctor_key, doctor_name FROM public.doctor', engine)
    return dict(zip(lookup_df["doctor_name"], lookup_df["doctor_key"]))


def build_hospital_dim(df, engine):
    """
    hospital.city/state/country are repurposed for Uganda's admin structure:
    city = district, state = region, country = 'Uganda' (see schema.sql note).
    """
    hospitals = df[["hospital", "district", "region"]].drop_duplicates(subset="hospital")
    hospitals = hospitals.rename(columns={
        "hospital": "hospital_name", "district": "city", "region": "state"
    })
    hospitals["country"] = "Uganda"

    hospitals.to_sql("hospital", engine, schema="public", if_exists="append", index=False)
    print(f"   hospital: {len(hospitals)} rows inserted.")

    lookup_df = pd.read_sql('SELECT hospital_key, hospital_name FROM public.hospital', engine)
    return dict(zip(lookup_df["hospital_name"], lookup_df["hospital_key"]))


def build_district_dim(df, engine):
    """
    estimated_population and is_urban come straight from the staging
    table's district_estimated_population / district_is_urban columns —
    generate_synthetic_patients.py embeds these per row from
    data/reference/uganda_district_population.csv, so there's a single
    source of truth instead of a duplicate lookup here.
    """
    districts = df[[
        "district", "region", "district_estimated_population", "district_is_urban"
    ]].drop_duplicates(subset="district")
    districts = districts.rename(columns={
        "district": "district_name",
        "district_estimated_population": "estimated_population",
        "district_is_urban": "is_urban",
    })

    districts.to_sql("district", engine, schema="public", if_exists="append", index=False)
    print(f"   district: {len(districts)} rows inserted.")

    lookup_df = pd.read_sql('SELECT district_key, district_name FROM public.district', engine)
    return dict(zip(lookup_df["district_name"], lookup_df["district_key"]))


def build_fact_table(df, engine, patient_key, date_key, hospital_key, doctor_key,
                      condition_key, medication_key, insurance_key,
                      admission_key, test_key, district_key):
    fact = pd.DataFrame({
        "patient_key": df["patient_id"].map(patient_key),
        "date_key": df["date_of_admission"].map(date_key),
        "hospital_key": df["hospital"].map(hospital_key),
        "doctor_key": df["doctor"].map(doctor_key),
        "condition_key": df["medical_condition"].map(condition_key),
        "medication_key": df["medication"].map(medication_key),
        "insurance_key": df["insurance_provider"].map(insurance_key),
        "admission_type_key": df["admission_type"].map(admission_key),
        "test_result_key": df["test_results"].map(test_key),
        "district_key": df["district"].map(district_key),
        "billing_amount": df["billing_amount_ugx"],
        "length_of_stay": df["length_of_stay"],
        "room_number": df["room_number"],
        "age": df["age"],
    })

    missing = fact.isna().sum()
    if missing.any():
        print("Warning — some rows failed to map to a dimension key:")
        print(missing[missing > 0])

    fact.to_sql("fact_patient_visits", engine, schema="public", if_exists="append", index=False)
    print(f"   fact_patient_visits: {len(fact)} rows inserted.")


def truncate_star_schema(engine):
    """
    Clears every star schema table and resets the SERIAL key counters back
    to 1, so this script can be run on its own, more than once, without
    needing schema.sql re-run first. Without this, a second run tries to
    INSERT the same patient_id/etc a second time and Postgres rejects it
    as a duplicate key — which is the "already exists" error this fixes.
    TRUNCATE ... CASCADE clears dependent tables too, so listing just the
    dimension tables plus the fact table (in any order) is enough.
    """
    print("Clearing existing star schema data...")
    raw_conn = engine.raw_connection()
    try:
        cursor = raw_conn.cursor()
        cursor.execute("""
            TRUNCATE TABLE
                fact_patient_visits, patient, "date", hospital, doctor,
                district, medical_condition, medication, insurance,
                admission_type, test_results
            RESTART IDENTITY CASCADE;
        """)
        raw_conn.commit()
        cursor.close()
    finally:
        raw_conn.close()
    print("   Cleared.\n")


def build_star_schema():
    engine = get_engine()
    try:
        truncate_star_schema(engine)
        df = load_staging(engine)

        print("\nBuilding dimension tables...")
        patient_key = build_patient_dim(df, engine)
        date_key = build_date_dim(df, engine)
        hospital_key = build_hospital_dim(df, engine)
        doctor_key = build_doctor_dim(df, engine)
        district_key = build_district_dim(df, engine)
        condition_key = build_simple_dim(
            df, engine, "medical_condition", "medical_condition", "condition_name", "condition_key",
            extra_cols=["condition_category", "severity_level", "icd10_code"],
            info_map=CONDITION_INFO
        )
        medication_key = build_simple_dim(
            df, engine, "medication", "medication", "medication_name", "medication_key",
            extra_cols=["medication_category", "drug_class", "prescription_type"],
            info_map=MEDICATION_INFO
        )
        insurance_key = build_simple_dim(
            df, engine, "insurance_provider", "insurance", "insurance_provider", "insurance_key"
        )
        admission_key = build_simple_dim(
            df, engine, "admission_type", "admission_type", "admission_type", "admission_key",
            extra_cols=["priority_level"],
            info_map={k: (v,) for k, v in ADMISSION_PRIORITY.items()}
        )
        test_key = build_simple_dim(
            df, engine, "test_results", "test_results", "test_result", "test_key",
            extra_cols=["result_category", "severity_indicator"],
            info_map=TEST_RESULT_INFO
        )

        print("\nBuilding fact table...")
        build_fact_table(
            df, engine, patient_key, date_key, hospital_key, doctor_key,
            condition_key, medication_key, insurance_key,
            admission_key, test_key, district_key
        )

        print("\nStar schema populated successfully.")

    finally:
        engine.dispose()


if __name__ == "__main__":
    build_star_schema()