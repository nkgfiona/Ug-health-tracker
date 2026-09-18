# generate_synthetic_patients.py
# ─────────────────────────────────────────────────────────────────────────
# Generates a synthetic hospital_patients.csv for the Uganda Health Tracker
# project. Patient identity fields (name, doctor, exact dates, billing) are
# SYNTHETIC — real patient-level health records can never legally be public,
# in Uganda or anywhere else. What is NOT synthetic:
#
#   - Facility names, districts, and regions: data/reference/uganda_hospitals.csv,
#     a curated set of real, verifiable Uganda hospitals spanning all four
#     regions, sourced from Wikipedia's "List of hospitals in Uganda" /
#     Uganda's 13 Regional Referral Hospitals.
#     https://en.wikipedia.org/wiki/List_of_hospitals_in_Uganda
#
#   - District population, urban/rural status, and city name:
#     data/reference/uganda_district_population.csv, real UBOS 2023
#     projection figures as tabulated on Wikipedia's "Districts of Uganda".
#     https://en.wikipedia.org/wiki/Districts_of_Uganda
#
#   - National population context: data/reference/uganda_national_population.csv,
#     from UBOS's National Population and Housing Census 2024.
#
#   - Disease mix: weighted toward the leading causes of hospital admission
#     actually reported in Uganda, per a 4-year retrospective study at
#     Mulago National Referral Hospital (HIV/AIDS 30%, hypertension 14%,
#     TB 12%, pneumonia 11%, heart failure 9.3%) plus malaria, which the
#     Ministry of Health reports as Uganda's leading overall cause of
#     morbidity (30-50% of outpatient visits, ~35% of admissions).
#     Sources:
#     https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0216060
#     https://pmc.ncbi.nlm.nih.gov/articles/PMC3156969/
#
#   - Insurance providers: real, IRA-Uganda-licensed insurers (Jubilee
#     Health, AAR, UAP Old Mutual, APA), weighted so most patients are
#     "Out-of-Pocket" — Uganda's insurance penetration is under 1% of GDP.
#     https://en.wikipedia.org/wiki/List_of_insurance_companies_in_Uganda
#
# All reference data lives in data/reference/ as plain CSV files, not
# hardcoded in this script or fetched at runtime — everything needed to
# reproduce this dataset ships inside the repo itself.
#
# This is disclosed plainly in the project README: facility/geography and
# epidemiological weighting are real and cited; individual patient rows
# are simulated for demonstration purposes.
# ─────────────────────────────────────────────────────────────────────────

import csv
import random
from datetime import date, timedelta

random.seed(42)  # reproducible output

HOSPITALS_FILE = "../../data/reference/uganda_hospitals.csv"
DISTRICT_POPULATION_FILE = "../../data/reference/uganda_district_population.csv"


def load_hospitals():
    """Returns a list of (hospital_name, district, region) tuples."""
    with open(HOSPITALS_FILE, newline="", encoding="utf-8") as f:
        return [(row["hospital_name"], row["district"], row["region"])
                for row in csv.DictReader(f)]


def load_district_population():
    """Returns {district_name: (estimated_population, is_urban, city_name)}."""
    lookup = {}
    with open(DISTRICT_POPULATION_FILE, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            lookup[row["district"]] = (
                int(row["estimated_population"]),
                row["is_urban"].strip().lower() == "true",
                row["city_name"].strip() or None,
            )
    return lookup


HOSPITALS = load_hospitals()
DISTRICT_POPULATION = load_district_population()

# Fail fast if a hospital references a district with no population entry —
# better than silently writing blank population data into the CSV.
_missing = {d for _, d, _ in HOSPITALS} - DISTRICT_POPULATION.keys()
if _missing:
    raise ValueError(
        f"uganda_district_population.csv is missing entries for: {sorted(_missing)}. "
        f"Add these districts before generating data."
    )

# ── Disease mix, weighted toward real Uganda hospital-admission data ──────
CONDITIONS = [
    ("Malaria", 22), ("HIV/AIDS", 18), ("Hypertension", 14),
    ("Tuberculosis", 12), ("Pneumonia", 11), ("Heart Failure", 9),
    ("Diabetes", 8), ("Typhoid Fever", 6),
]

MEDICATION_BY_CONDITION = {
    "Malaria": "Artemether-Lumefantrine",
    "HIV/AIDS": "Tenofovir-Lamivudine-Dolutegravir",
    "Hypertension": "Amlodipine",
    "Tuberculosis": "Rifampicin-Isoniazid",
    "Pneumonia": "Amoxicillin",
    "Heart Failure": "Furosemide",
    "Diabetes": "Metformin",
    "Typhoid Fever": "Ciprofloxacin",
}

# ── Insurance: real IRA-Uganda-licensed insurers, most patients uninsured ──
INSURANCE = [
    ("Out-of-Pocket", 68),
    ("Jubilee Health Insurance", 10),
    ("AAR Insurance Uganda", 9),
    ("UAP Old Mutual", 7),
    ("APA Insurance Uganda", 6),
]

ADMISSION_TYPES = [("Emergency", 45), ("Urgent", 30), ("Elective", 25)]
TEST_RESULTS = ["Normal", "Abnormal", "Inconclusive"]
BLOOD_TYPES = ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"]

MALE_FIRST_NAMES = ["Mukasa", "Okello", "Byaruhanga", "Ssenyonga", "Wamala",
                    "Otim", "Kato", "Tumusiime", "Kwizera", "Ochieng"]
FEMALE_FIRST_NAMES = ["Nakato", "Achieng", "Nabirye", "Namutebi", "Auma",
                      "Kyomuhendo", "Nansubuga", "Adong", "Namuli", "Akello"]
LAST_NAMES = ["Kirabo", "Ssebunya", "Namono", "Opio", "Nantongo", "Mugisha",
              "Akena", "Nakalema", "Tugume", "Aketch"]

DOCTOR_LAST_NAMES = LAST_NAMES + ["Kaggwa", "Nabatanzi", "Ariong", "Businge"]


def weighted_choice(pairs):
    items, weights = zip(*pairs)
    return random.choices(items, weights=weights, k=1)[0]


def random_date(start_year=2022, end_year=2024):
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    delta_days = (end - start).days
    return start + timedelta(days=random.randint(0, delta_days))


def generate_patient(patient_num):
    gender = random.choice(["Male", "Female"])
    first = random.choice(MALE_FIRST_NAMES if gender == "Male" else FEMALE_FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    name = f"{first} {last}"

    # Uganda has a young population — weight age accordingly
    age_group = random.choices(
        ["Under 18", "18-35", "36-60", "Over 60"],
        weights=[30, 35, 25, 10], k=1
    )[0]
    age = {
        "Under 18": random.randint(1, 17),
        "18-35": random.randint(18, 35),
        "36-60": random.randint(36, 60),
        "Over 60": random.randint(61, 90),
    }[age_group]

    hospital, district, region = random.choice(HOSPITALS)
    estimated_population, is_urban, city_name = DISTRICT_POPULATION[district]

    doctor = f"Dr. {random.choice(['A.', 'B.', 'C.', 'D.', 'E.'])} {random.choice(DOCTOR_LAST_NAMES)}"

    condition = weighted_choice(CONDITIONS)
    medication = MEDICATION_BY_CONDITION[condition]

    admission_date = random_date()
    length_of_stay = max(1, int(random.gauss(7, 4)))
    discharge_date = admission_date + timedelta(days=length_of_stay)

    admission_type = weighted_choice(ADMISSION_TYPES)
    insurance_provider = weighted_choice(INSURANCE)

    # Rough UGX billing scale — higher for emergency/longer stays
    base = 150_000 if admission_type == "Elective" else 300_000
    billing_amount = round(base + (length_of_stay * random.uniform(80_000, 250_000)), -3)

    return {
        "patient_id": f"UGP{patient_num:05d}",
        "name": name,
        "age": age,
        "age_group": age_group,
        "gender": gender,
        "blood_type": random.choice(BLOOD_TYPES),
        "medical_condition": condition,
        "date_of_admission": admission_date.strftime("%d/%m/%Y"),
        "doctor": doctor,
        "hospital": hospital,
        "district": district,
        "region": region,
        "district_estimated_population": estimated_population,
        "district_is_urban": is_urban,
        "district_city_name": city_name or "",
        "insurance_provider": insurance_provider,
        "billing_amount_ugx": billing_amount,
        "room_number": random.randint(100, 450),
        "admission_type": admission_type,
        "discharge_date": discharge_date.strftime("%d/%m/%Y"),
        "medication": medication,
        "test_results": random.choice(TEST_RESULTS),
        "length_of_stay": length_of_stay,
    }


def generate_dataset(n=1000, output_path="../../data/raw/hospital_patients.csv"):
    fieldnames = list(generate_patient(1).keys())
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(1, n + 1):
            writer.writerow(generate_patient(i))
    print(f"Generated {n} synthetic patient records -> {output_path}")


if __name__ == "__main__":
    generate_dataset()
