Uganda Health Tracker
End-to-End Healthcare Data Analytics
Fiona Nakabugo Kabuka — Healthcare Data Analyst | M&E | Power BI | SQL | Data Management
An end-to-end analytics pipeline that turns raw healthcare data into a decision-ready Power BI dashboard — built to demonstrate the full data lifecycle a health M&E system runs on, from data generation through a normalized PostgreSQL data warehouse to interactive analytics.
---
Overview
Problem: Healthcare data requires cleaning, validation, and transformation before it can support decision-making raw records rarely arrive analysis-ready.
Process: Python → PostgreSQL (star schema) → SQL → Power BI. Data is generated, staged, transformed into a proper dimensional model, analyzed with 17 SQL queries, and visualized across a 3-page interactive dashboard.
Outcome: A reproducible, end-to-end analytics workflow capable of transforming raw healthcare data into decision-ready information runnable end-to-end with a single command.
---
Dashboard Preview
	Clinical & Workforce Insights	Geography & Population Insights
Executive Overview - <img width="1686" height="938" alt="Screenshot 2026-09-18 140139" src="https://github.com/user-attachments/assets/d0ba888a-b27f-43fc-803d-db7df696cd93" />
Clinical & Workforce Insights - <img width="1573" height="891" alt="Screenshot 2026-09-18 140433" src="https://github.com/user-attachments/assets/87476b9e-d1bc-4055-a2a7-f80900ce56cd" />
Clinical & Workforce Insights	Geography & Population Insights - <img width="1593" height="884" alt="Screenshot 2026-09-18 140656" src="https://github.com/user-attachments/assets/1c56536e-b6a8-43b8-84c5-7d4061bdb59c" />
---
`powerbi/Uganda_Health.pbix` — open in Power BI Desktop (free, Windows only) for the full interactive experience.
---
Tech Stack
Layer	Tools
Data generation & ETL	Python (pandas, SQLAlchemy, psycopg2)
Database	PostgreSQL (star schema)
Analysis	SQL (17 queries), Python (matplotlib)
Visualization	Power BI (DAX, Power Query, Shape Map)
---
Architecture
```
data/reference/*.csv (real Uganda facility, population, district data)
        │
        ▼
generate_synthetic_patients.py  →  data/raw/hospital_patients.csv
        │
        ▼
load_to_staging.py  →  hospital_patients_staging (flat table)
        │
        ▼
build_star_schema.py  →  10 dimension tables + fact_patient_visits
        │
        ▼
run_analysis.py  →  17 SQL queries, 4 chart pages, summary report
        │
        ▼
Power BI  →  3-page interactive dashboard
```
See `documentation/erd.png` for the full entity-relationship diagram.
`main.py` runs the entire pipeline from CSV generation through analysis in one command.
---
Data Sources & Disclosure
This project is built on a deliberate mix of real, cited data and clearly-disclosed synthetic data — because real, identifiable patient records can never legally be public, in Uganda or anywhere else.
Real and cited:
Facility names, districts, and regions a curated set of 34 real Uganda hospitals spanning all four regions, sourced from Wikipedia's List of Hospitals in Uganda
District population and urban/rural status: UBOS 2023 projections, from Wikipedia's Districts of Uganda
National population(45,935,046) (Uganda's 2024 National Population and Housing Census, UBOS)
Disease-burden weighting leading causes of hospital admission per a 4-year retrospective study at Mulago National Referral Hospital (HIV/AIDS, hypertension, TB, pneumonia, heart failure) plus malaria, per Uganda's Ministry of Health
Insurance providers(real), IRA-Uganda-licensed insurers (Jubilee Health, AAR, UAP Old Mutual, APA), weighted toward Out-of-Pocket to reflect Uganda's low insurance penetration
Synthetic and disclosed: individual patient identity fields: names, exact admission dates, doctor assignments, billing amounts are generated for demonstration purposes. This is standard, expected practice for a portfolio project; the alternative (real patient records) would itself be a privacy violation.
---
Project Structure
```
Ug-health-tracker/
├── data/
│   ├── raw/                    # generated patient-level CSV
│   └── reference/               # real hospital, district, population data
├── python/
│   ├── data_generation/         # synthetic patient data generator
│   └── etl/                     # staging load, star schema build, analysis, pipeline entry point
├── sql/
│   └── schema.sql                # star schema DDL
├── powerbi/
│   └── Uganda_Health.pbix        # the dashboard
├── documentation/
│   └── erd.png                   # entity-relationship diagram
├── outputs/
│   └── reports/                  # generated charts + summary
├── requirements.txt
└── .gitignore
```
---
How to Run It Yourself
```bash
# 1. Create the database
createdb -U postgres uganda_health_db

# 2. Set up credentials
cd python/etl
cp config.example.py config.py    # then fill in your real DB credentials

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the full pipeline
python main.py
```
`main.py` regenerates the source data, rebuilds the schema, loads it, and runs the full analysis in that order, safe to re-run any time.
---
Key Findings
Malaria leads admissions, accounting for 216 of 1,000 cases (nearly 1 in 5) — consistent with published Uganda Ministry of Health morbidity data.
Patient load is concentrated among a subset of doctors: the top 5 doctors each handled 21-25 patients, while the median doctor handled far fewer — a workload-distribution signal relevant to staffing decisions.
Kampala recorded the highest district-level patient volume (62 visits, roughly double the 32-district average): driven by having two sampled hospitals rather than any real epidemiological difference (see Limitations).
Rural districts account for 59.6% of patient visits despite holding only 39.3% of the sampled population: this looks like a striking access-to-care finding, but traces directly back to which facilities were sampled, not real healthcare-seeking behavior (see Limitations). This distinction and catching it is itself a demonstration of the kind of data-quality thinking this project is meant to show.
---
Limitations
Sampling artifact, not real epidemiology: patient volume in this dataset is driven by how many hospitals were sampled per district/region, not by population or real healthcare utilization. Findings that appear to show geographic disparity should be read with this in mind: a per-capita (per-100k) view is more defensible than raw counts.
Local database, manual refresh: the pipeline runs against a local PostgreSQL instance; the dashboard is refreshed manually in Power BI Desktop rather than continuously auto-refreshing from a hosted database.
No public web link: Power BI's "Publish to web" requires tenant-admin rights not available on this account. Instead, the `.pbix` file linked above is available for direct download and just requires Windows and free Power BI Desktop, but gives full access to the actual interactive dashboard.
---
Skills Demonstrated
Data architecture: star schema design (10 dimensions + fact table), with a documented data dictionary
ETL engineering: staging-to-warehouse transformation, idempotent pipeline design, debugging a real missing-dimension bug (doctor workload) traced from symptom to root cause
SQL: 17 analytical queries including per-capita normalization and window-function ranking
Power BI / DAX: RANKX with correct filter-context scoping, SVG-based custom visualizations, Shape Map choropleth mapping
Data quality & integrity: identifying and disclosing a sampling artifact rather than presenting it as a genuine finding
Domain expertise: 10+ years of real Uganda health surveillance experience (CDC/USAID-funded programmes at Makerere School of Public Health) informing realistic data modeling decisions
---
About
Fiona Nakabugo Kabuka
Healthcare Data Analyst | M&E | Power BI | SQL | Data Management
[LinkedIn — www.linkedin.com/in/nakabugo-fiona-8334b638] · [Email — jclovefiona@gmail.com]
---
Data Source Citations
Uganda Bureau of Statistics (UBOS) — Districts of Uganda population data, National Population and Housing Census 2024
List of Hospitals in Uganda — Wikipedia
Trends of admissions at a tertiary hospital in Uganda — PLOS One
List of insurance companies in Uganda — Wikipedia
