# analysis2_from_db.py
# ─────────────────────────────────────────────────────────────────────────────
# Star schema hospital patient analysis.
# All queries run against PostgreSQL (imdb database, public schema).
# Results printed to terminal and saved as three chart pages.
#
# FIX LOG (all bugs from original file corrected here):
#   1. All SQL table names now prefixed with public. schema
#   2. Reserved word 'date' quoted as "date" in every query
#   4. Chart 6 bar offset removed (single bar set needs no offset)
#   5. Chart 10 set_xticks() added before set_xticklabels()
#   6. Revenue chart uses enumerate() for safe label positioning
#   7. Admission type printed properly in terminal summary
#   8. Function parameters renamed to match what is actually passed
# =============================================================================
# NEW FEATURES ADDED:
#   9. District analysis functions (q11-q17)
#   10. District chart page (Page 4)
#   11. Expanded summary report with district statistics
#   12. Save summary to file with all statistics
#   13. Debugging and error handling for chart pages
#   14. NaN/Inf handling for axis limits
#   15. Conditional chart display - only shows charts with available data
#   16. Improved chart formatting - better labels, spacing, readability
#   17. Removed all unused variable assignments
# =============================================================================

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from database_connection import run_query


# =============================================================================
# SECTION 1 — QUERIES
# Each function runs one SQL query and returns a pandas DataFrame.
# All tables use public. prefix and "date" is quoted.
# =============================================================================

def q1_monthly_revenue():
    """
    Query 1: Monthly revenue and patient volume over time.
    Joins fact_patient_visits with the date dimension.
    """
    sql = """
        SELECT
            d.year,
            d.month,
            d.month_name,
            COUNT(f.visit_id)                                   AS total_patients,
            ROUND(SUM(f.billing_amount)::numeric, 2)            AS total_revenue,
            ROUND(AVG(f.billing_amount)::numeric, 2)            AS avg_billing,
            ROUND(AVG(f.length_of_stay)::numeric, 1)            AS avg_stay_days
        FROM public.fact_patient_visits f
        JOIN public."date" d ON f.date_key = d.date_key
        GROUP BY d.year, d.month, d.month_name
        ORDER BY d.year, d.month;
    """
    print("\n[Query 1] Monthly Revenue and Patient Volume...")
    return run_query(sql)


def q2_conditions():
    """
    Query 2: Medical conditions ranked by total cost and patient volume.
    """
    sql = """
        SELECT
            c.condition_name,
            COUNT(f.visit_id)                                       AS patient_count,
            ROUND(SUM(f.billing_amount)::numeric, 2)                AS total_cost,
            ROUND(AVG(f.billing_amount)::numeric, 2)                AS avg_cost_per_patient,
            ROUND(AVG(f.length_of_stay)::numeric, 1)                AS avg_stay_days,
            ROUND(
                (SUM(f.billing_amount) / NULLIF(COUNT(f.visit_id), 0))::numeric,
                2
            )                                                        AS cost_per_visit
        FROM public.fact_patient_visits f
        JOIN public.medical_condition c ON f.condition_key = c.condition_key
        GROUP BY c.condition_name
        ORDER BY total_cost DESC;
    """
    print("\n[Query 2] Medical Conditions by Cost and Volume...")
    return run_query(sql)


def q3_hospitals():
    """
    Query 3: Hospital performance — revenue, patients, doctors, avg stay.
    """
    sql = """
        SELECT
            h.hospital_name,
            h.city,
            COUNT(DISTINCT f.patient_key)                           AS unique_patients,
            COUNT(f.visit_id)                                       AS total_admissions,
            ROUND(SUM(f.billing_amount)::numeric, 2)                AS total_revenue,
            ROUND(AVG(f.billing_amount)::numeric, 2)                AS avg_billing,
            ROUND(AVG(f.length_of_stay)::numeric, 1)                AS avg_stay_days,
            COUNT(DISTINCT f.doctor_key)                            AS active_doctors,
            COUNT(DISTINCT f.condition_key)                         AS conditions_treated,
            ROUND(
                (SUM(f.billing_amount) / NULLIF(COUNT(DISTINCT f.patient_key), 0))::numeric,
                2
            )                                                        AS revenue_per_patient
        FROM public.fact_patient_visits f
        JOIN public.hospital h ON f.hospital_key = h.hospital_key
        GROUP BY h.hospital_name, h.city
        ORDER BY total_revenue DESC;
    """
    print("\n[Query 3] Hospital Performance...")
    return run_query(sql)


def q4_insurance():
    """
    Query 4: Insurance providers — patient count, avg billing, total billed.
    """
    sql = """
        SELECT
            i.insurance_provider,
            COUNT(*)                                                AS patients,
            ROUND(AVG(f.billing_amount)::numeric, 2)               AS avg_bill,
            ROUND(SUM(f.billing_amount)::numeric, 2)               AS total_bill
        FROM public.fact_patient_visits f
        JOIN public.insurance i ON f.insurance_key = i.insurance_key
        GROUP BY i.insurance_provider
        ORDER BY total_bill DESC;
    """
    print("\n[Query 4] Insurance Provider Analysis...")
    return run_query(sql)


def q5_admission_types():
    """
    Query 5: Admission type efficiency — visits, avg stay, avg cost.
    """
    sql = """
        SELECT
            a.admission_type,
            COUNT(*)                                                AS visits,
            ROUND(AVG(f.length_of_stay)::numeric, 1)               AS avg_stay,
            ROUND(AVG(f.billing_amount)::numeric, 2)               AS avg_cost,
            ROUND(SUM(f.billing_amount)::numeric, 2)               AS total_cost
        FROM public.fact_patient_visits f
        JOIN public.admission_type a ON f.admission_type_key = a.admission_key
        GROUP BY a.admission_type
        ORDER BY avg_cost DESC;
    """
    print("\n[Query 5] Admission Type Efficiency...")
    return run_query(sql)


def q6_doctors():
    """
    Query 6: Top 10 doctors by patients handled and revenue generated.
    """
    sql = """
        SELECT
            d.doctor_name,
            d.specialty,
            COUNT(f.visit_id)                                       AS patients_handled,
            ROUND(SUM(f.billing_amount)::numeric, 2)                AS total_revenue,
            ROUND(AVG(f.billing_amount)::numeric, 2)                AS avg_billing
        FROM public.fact_patient_visits f
        JOIN public.doctor d ON f.doctor_key = d.doctor_key
        GROUP BY d.doctor_name, d.specialty
        ORDER BY patients_handled DESC
        LIMIT 10;
    """
    print("\n[Query 6] Doctor Workload (Top 10)...")
    return run_query(sql)


def q7_demographics():
    """
    Query 7: Patient demographics — age group and gender breakdown.
    """
    sql = """
        SELECT
            p.age_group,
            p.gender,
            COUNT(DISTINCT f.patient_key)                           AS patient_count,
            COUNT(f.visit_id)                                       AS total_visits,
            ROUND(AVG(f.billing_amount)::numeric, 2)                AS avg_billing,
            ROUND(AVG(f.length_of_stay)::numeric, 1)                AS avg_stay
        FROM public.fact_patient_visits f
        JOIN public.patient p ON f.patient_key = p.patient_key
        GROUP BY p.age_group, p.gender
        ORDER BY p.age_group, p.gender;
    """
    print("\n[Query 7] Patient Demographics...")
    return run_query(sql)


def q8_medications():
    """
    Query 8: Most prescribed medications — count, avg billing, avg stay.
    """
    sql = """
        SELECT
            m.medication_name,
            m.drug_class,
            COUNT(f.visit_id)                                       AS prescription_count,
            ROUND(AVG(f.billing_amount)::numeric, 2)                AS avg_billing,
            ROUND(AVG(f.length_of_stay)::numeric, 1)                AS avg_stay
        FROM public.fact_patient_visits f
        JOIN public.medication m ON f.medication_key = m.medication_key
        GROUP BY m.medication_name, m.drug_class
        ORDER BY prescription_count DESC;
    """
    print("\n[Query 8] Medication Prescriptions...")
    return run_query(sql)


def q9_test_results():
    """
    Query 9: Test result distribution — counts and associated billing.
    """
    sql = """
        SELECT
            t.test_result,
            t.result_category,
            COUNT(f.visit_id)                                       AS total_tests,
            ROUND(SUM(f.billing_amount)::numeric, 2)                AS total_billing,
            ROUND(AVG(f.billing_amount)::numeric, 2)                AS avg_billing,
            ROUND(AVG(f.length_of_stay)::numeric, 1)                AS avg_stay
        FROM public.fact_patient_visits f
        JOIN public.test_results t ON f.test_result_key = t.test_key
        GROUP BY t.test_result, t.result_category
        ORDER BY total_tests DESC;
    """
    print("\n[Query 9] Test Result Distribution...")
    return run_query(sql)


def q10_gender():
    """
    Query 10: Gender summary — unique patients, visits, billing.
    """
    sql = """
        SELECT
            p.gender,
            COUNT(DISTINCT f.patient_key)                           AS unique_patients,
            COUNT(f.visit_id)                                       AS total_visits,
            ROUND(SUM(f.billing_amount)::numeric, 2)                AS total_billing,
            ROUND(AVG(f.billing_amount)::numeric, 2)                AS avg_billing,
            ROUND(AVG(f.length_of_stay)::numeric, 1)                AS avg_stay
        FROM public.fact_patient_visits f
        JOIN public.patient p ON f.patient_key = p.patient_key
        GROUP BY p.gender
        ORDER BY total_visits DESC;
    """
    print("\n[Query 10] Gender Analysis...")
    return run_query(sql)


# =============================================================================
# SECTION 1B — DISTRICT ANALYSIS QUERIES (NEW)
# =============================================================================

def q11_top_districts_by_cases(year=None, top_n=5):
    """
    Query 11: Top districts with case counts and metrics.
    """
    year_filter = f"AND dt.year = {year}" if year else ""
    
    sql = f"""
        SELECT 
            d.district_name,
            d.region,
            d.sub_region,
            d.estimated_population,
            d.is_urban,
            COUNT(f.visit_id) AS total_cases,
            COUNT(DISTINCT f.patient_key) AS unique_patients,
            ROUND(SUM(f.billing_amount)::numeric, 2) AS total_revenue,
            ROUND(AVG(f.billing_amount)::numeric, 2) AS avg_billing,
            ROUND(AVG(f.length_of_stay)::numeric, 1) AS avg_stay_days,
            COUNT(DISTINCT f.condition_key) AS conditions_treated,
            COUNT(DISTINCT f.doctor_key) AS active_doctors,
            COUNT(DISTINCT f.hospital_key) AS active_hospitals,
            ROUND(COUNT(f.visit_id)::numeric / NULLIF(d.estimated_population, 0) * 100000, 1) AS cases_per_100k
        FROM public.fact_patient_visits f
        JOIN public.district d ON f.district_key = d.district_key
        LEFT JOIN public."date" dt ON f.date_key = dt.date_key
        WHERE 1=1 {year_filter}
        GROUP BY d.district_name, d.region, d.sub_region, d.estimated_population, d.is_urban
        ORDER BY total_cases DESC
        LIMIT {top_n};
    """
    print(f"\n[Query 11] Top {top_n} Districts by Cases{' for Year ' + str(year) if year else ''}...")
    return run_query(sql)


def q12_trend_by_disease(disease_name):
    """
    Query 12: Yearly case counts for a specific disease.
    """
    sql = f"""
        SELECT 
            dt.year,
            COUNT(f.visit_id) AS total_cases,
            COUNT(DISTINCT f.patient_key) AS unique_patients,
            COUNT(DISTINCT d.district_key) AS affected_districts,
            ROUND(SUM(f.billing_amount)::numeric, 2) AS total_revenue,
            ROUND(AVG(f.billing_amount)::numeric, 2) AS avg_billing,
            ROUND(AVG(f.length_of_stay)::numeric, 1) AS avg_stay_days
        FROM public.fact_patient_visits f
        JOIN public."date" dt ON f.date_key = dt.date_key
        JOIN public.medical_condition c ON f.condition_key = c.condition_key
        LEFT JOIN public.district d ON f.district_key = d.district_key
        WHERE c.condition_name ILIKE '%{disease_name}%'
        GROUP BY dt.year
        ORDER BY dt.year ASC;
    """
    print(f"\n[Query 12] Trend for Disease: {disease_name}...")
    return run_query(sql)


def q13_facility_summary(facility_id):
    """
    Query 13: Basic facility information.
    """
    if isinstance(facility_id, int) or str(facility_id).isdigit():
        id_condition = f"h.hospital_key = {facility_id}"
    else:
        id_condition = f"h.hospital_name ILIKE '%{facility_id}%'"
    
    sql = f"""
        SELECT 
            h.hospital_key,
            h.hospital_name,
            h.hospital_id,
            h.hospital_type,
            h.city,
            h.state,
            h.country,
            d.district_name,
            d.region,
            d.sub_region,
            COUNT(DISTINCT f.patient_key) AS total_patients,
            COUNT(f.visit_id) AS total_admissions,
            ROUND(SUM(f.billing_amount)::numeric, 2) AS total_revenue,
            ROUND(AVG(f.billing_amount)::numeric, 2) AS avg_billing,
            ROUND(AVG(f.length_of_stay)::numeric, 1) AS avg_stay_days,
            COUNT(DISTINCT f.doctor_key) AS active_doctors,
            COUNT(DISTINCT f.condition_key) AS conditions_treated
        FROM public.fact_patient_visits f
        JOIN public.hospital h ON f.hospital_key = h.hospital_key
        LEFT JOIN public.district d ON f.district_key = d.district_key
        WHERE {id_condition}
        GROUP BY h.hospital_key, h.hospital_name, h.hospital_id, h.hospital_type, 
                 h.city, h.state, h.country, d.district_name, d.region, d.sub_region;
    """
    print(f"\n[Query 13] Facility Summary for: {facility_id}...")
    return run_query(sql)


def q14_facility_conditions(facility_id):
    """
    Query 14: Top conditions at a specific facility.
    """
    if isinstance(facility_id, int) or str(facility_id).isdigit():
        id_condition = f"h.hospital_key = {facility_id}"
    else:
        id_condition = f"h.hospital_name ILIKE '%{facility_id}%'"
    
    sql = f"""
        SELECT 
            c.condition_name,
            COUNT(f.visit_id) AS case_count,
            ROUND(SUM(f.billing_amount)::numeric, 2) AS total_cost,
            ROUND(AVG(f.billing_amount)::numeric, 2) AS avg_cost,
            ROUND(AVG(f.length_of_stay)::numeric, 1) AS avg_stay
        FROM public.fact_patient_visits f
        JOIN public.hospital h ON f.hospital_key = h.hospital_key
        JOIN public.medical_condition c ON f.condition_key = c.condition_key
        WHERE {id_condition}
        GROUP BY c.condition_name
        ORDER BY case_count DESC
        LIMIT 10;
    """
    print(f"\n[Query 14] Top Conditions at Facility: {facility_id}...")
    return run_query(sql)


def q15_facility_trend(facility_id):
    """
    Query 15: Monthly trend at a specific facility.
    """
    if isinstance(facility_id, int) or str(facility_id).isdigit():
        id_condition = f"h.hospital_key = {facility_id}"
    else:
        id_condition = f"h.hospital_name ILIKE '%{facility_id}%'"
    
    sql = f"""
        SELECT 
            dt.year,
            dt.month_name,
            COUNT(f.visit_id) AS admissions,
            ROUND(SUM(f.billing_amount)::numeric, 2) AS revenue
        FROM public.fact_patient_visits f
        JOIN public.hospital h ON f.hospital_key = h.hospital_key
        JOIN public."date" dt ON f.date_key = dt.date_key
        WHERE {id_condition}
        GROUP BY dt.year, dt.month, dt.month_name
        ORDER BY dt.year, dt.month
        LIMIT 24;
    """
    print(f"\n[Query 15] Monthly Trend at Facility: {facility_id}...")
    return run_query(sql)


def q16_high_risk_regions(threshold=100):
    """
    Query 16: Regions above a case threshold.
    """
    sql = f"""
        WITH region_stats AS (
            SELECT 
                d.region,
                d.sub_region,
                COUNT(f.visit_id) AS total_cases,
                COUNT(DISTINCT f.patient_key) AS unique_patients,
                COUNT(DISTINCT d.district_key) AS districts_affected,
                ROUND(SUM(f.billing_amount)::numeric, 2) AS total_revenue,
                ROUND(AVG(f.billing_amount)::numeric, 2) AS avg_billing,
                ROUND(AVG(f.length_of_stay)::numeric, 1) AS avg_stay_days,
                COUNT(DISTINCT f.condition_key) AS conditions_treated,
                COUNT(DISTINCT f.hospital_key) AS active_hospitals,
                COUNT(DISTINCT f.doctor_key) AS active_doctors,
                ROUND(COUNT(f.visit_id)::numeric / NULLIF(COUNT(DISTINCT d.district_key), 0), 1) AS cases_per_district
            FROM public.fact_patient_visits f
            JOIN public.district d ON f.district_key = d.district_key
            GROUP BY d.region, d.sub_region
        )
        SELECT 
            region,
            sub_region,
            total_cases,
            unique_patients,
            districts_affected,
            cases_per_district,
            total_revenue,
            avg_billing,
            avg_stay_days,
            conditions_treated,
            active_hospitals,
            active_doctors,
            CASE 
                WHEN total_cases >= {threshold * 3} THEN 'CRITICAL'
                WHEN total_cases >= {threshold * 2} THEN 'HIGH'
                WHEN total_cases >= {threshold} THEN 'MEDIUM'
                ELSE 'LOW'
            END AS risk_level
        FROM region_stats
        WHERE total_cases >= {threshold}
        ORDER BY total_cases DESC;
    """
    print(f"\n[Query 16] High Risk Regions (Threshold: {threshold} cases)...")
    return run_query(sql)


def q17_district_summary():
    """
    Query 17: Overall district summary statistics.
    """
    sql = """
        SELECT 
            COUNT(DISTINCT d.district_key) AS total_districts,
            COUNT(DISTINCT d.region) AS total_regions,
            COUNT(DISTINCT d.sub_region) AS total_sub_regions,
            SUM(CASE WHEN d.is_urban THEN 1 ELSE 0 END) AS urban_districts,
            SUM(CASE WHEN NOT d.is_urban THEN 1 ELSE 0 END) AS rural_districts,
            SUM(d.estimated_population) AS total_population,
            ROUND(AVG(d.estimated_population)::numeric, 0) AS avg_population_per_district
        FROM public.district d;
    """
    print("\n[Query 17] District Summary Statistics...")
    return run_query(sql)


# =============================================================================
# SECTION 2 — COLOUR PALETTE
# Consistent colours used across all chart pages.
# =============================================================================

COLOURS = {
    "revenue":    ["#2C3E50","#E74C3C","#3498DB","#27AE60",
                   "#F39C12","#9B59B6","#1ABC9C","#E67E22"],
    "conditions": ["#2C3E50","#E74C3C","#3498DB","#27AE60","#F39C12","#9B59B6"],
    "admission":  ["#E74C3C","#F39C12","#27AE60"],
    "age_groups": ["#3498DB","#2ECC71","#E67E22","#9B59B6"],
    "test_normal":"#27AE60",
    "test_inconc":"#F39C12",
    "test_abnorm":"#E74C3C",
    "male":       "#2980B9",
    "female":     "#C0392B",
    "medications":["#1ABC9C","#3498DB","#9B59B6","#E67E22","#E74C3C","#2C3E50"],
    "insurance":  ["#2C3E50","#2980B9","#27AE60","#E67E22","#8E44AD"],
    "doctors":    ["#1ABC9C","#3498DB","#9B59B6","#E67E22","#E74C3C","#2C3E50"],
    "gender":     ["#2980B9","#C0392B"],
    "districts":  ["#2C3E50","#E74C3C","#3498DB","#27AE60","#F39C12","#9B59B6","#1ABC9C","#E67E22"],
    "regions":    ["#2C3E50","#E74C3C","#3498DB","#27AE60"],
    "risk":       {"CRITICAL": "#E74C3C", "HIGH": "#F39C12", "MEDIUM": "#F1C40F", "LOW": "#27AE60"}
}


# =============================================================================
# SECTION 3 — CHART PAGES (IMPROVED FORMATTING)
# =============================================================================

def make_page1(df_monthly, df_conditions, df_admission, df_tests):
    """
    Page 1: Monthly Revenue | Top Conditions | Admission Costs | Test Results
    """
    # ── Check if we have any data for this page ──────────────────────────────
    has_data = False
    
    if df_monthly is not None and not df_monthly.empty and df_monthly["total_revenue"].max() > 0:
        has_data = True
    elif df_conditions is not None and not df_conditions.empty and df_conditions["total_cost"].max() > 0:
        has_data = True
    elif df_admission is not None and not df_admission.empty and df_admission["avg_cost"].max() > 0:
        has_data = True
    elif df_tests is not None and not df_tests.empty and df_tests["total_tests"].sum() > 0:
        has_data = True
    
    if not has_data:
        print("\n⚠️ No data available for Page 1 charts - skipping")
        return
    
    print("\n[DEBUG] make_page1 - DataFrame shapes:")
    print(f"  df_monthly: {df_monthly.shape if df_monthly is not None else 'None'}")
    print(f"  df_conditions: {df_conditions.shape if df_conditions is not None else 'None'}")
    print(f"  df_admission: {df_admission.shape if df_admission is not None else 'None'}")
    print(f"  df_tests: {df_tests.shape if df_tests is not None else 'None'}")
    
    fig = plt.figure(figsize=(16, 11))
    fig.suptitle(
        "Hospital Patient Analysis  —  Page 1 of 4\n"
        "Monthly Revenue  ·  Conditions  ·  Admission Types  ·  Test Results",
        fontsize=14, fontweight="bold", y=0.98
    )
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.30)

    # ── Chart 1: Monthly Revenue Trend (line) ─────────────────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    
    try:
        if df_monthly is not None and not df_monthly.empty and df_monthly["total_revenue"].max() > 0:
            df_monthly["date_label"] = (df_monthly["year"].astype(str)
                                        + "-"
                                        + df_monthly["month_name"].str[:3])

            ax1.plot(
                df_monthly["date_label"],
                df_monthly["total_revenue"],
                marker="o", linewidth=2.5, markersize=8, color="#2C3E50"
            )
            ax1.set_title("Monthly Revenue Trend", fontweight="bold", fontsize=12)
            ax1.set_xlabel("Month", fontsize=10)
            ax1.set_ylabel("Total Revenue (USD)", fontsize=10)
            ax1.tick_params(axis="x", rotation=45, labelsize=9)
            ax1.grid(axis="y", alpha=0.3, linestyle='--')

            max_rev = df_monthly["total_revenue"].max()
            for i, (_, row) in enumerate(df_monthly.iterrows()):
                ax1.text(
                    i, row["total_revenue"] + max_rev * 0.02,
                    f"${row['total_revenue']:,.0f}",
                    ha="center", fontsize=8, fontweight="bold", rotation=45
                )
        else:
            ax1.text(0.5, 0.5, "No monthly revenue data available", 
                     ha="center", va="center", transform=ax1.transAxes, fontsize=12)
            ax1.set_title("Monthly Revenue Trend", fontweight="bold", fontsize=11)
    except Exception as e:
        print(f"⚠️ Error creating Chart 1: {e}")
        ax1.text(0.5, 0.5, "Monthly revenue data unavailable", 
                 ha="center", va="center", transform=ax1.transAxes, fontsize=12)

    # ── Chart 2: Top Conditions by Total Cost (horizontal bar) ───────────────
    ax2 = fig.add_subplot(gs[0, 1])
    
    try:
        if df_conditions is not None and not df_conditions.empty:
            df_conditions_clean = df_conditions.dropna(subset=['total_cost', 'condition_name'])
            
            if not df_conditions_clean.empty and df_conditions_clean["total_cost"].max() > 0:
                df_sorted = df_conditions_clean.sort_values("total_cost", ascending=True).tail(6)

                bars = ax2.barh(
                    df_sorted["condition_name"],
                    df_sorted["total_cost"],
                    color=COLOURS["conditions"][:len(df_sorted)],
                    height=0.6
                )
                ax2.set_title("Top Conditions by Total Cost", fontweight="bold", fontsize=12)
                ax2.set_xlabel("Total Cost (USD)", fontsize=10)
                ax2.invert_yaxis()
                ax2.tick_params(axis='y', labelsize=10)

                max_cost = df_sorted["total_cost"].max()
                for bar in bars:
                    w = bar.get_width()
                    ax2.text(
                        w + max_cost * 0.01,
                        bar.get_y() + bar.get_height() / 2,
                        f"${w:,.0f}", va="center", fontsize=9, fontweight="bold"
                    )
                ax2.set_xlim(0, max_cost * 1.18)
                ax2.grid(axis="x", alpha=0.3, linestyle='--')
            else:
                ax2.text(0.5, 0.5, "No valid condition cost data", 
                         ha="center", va="center", transform=ax2.transAxes, fontsize=12)
                ax2.set_title("Top Conditions by Total Cost", fontweight="bold", fontsize=11)
        else:
            ax2.text(0.5, 0.5, "No condition data available", 
                     ha="center", va="center", transform=ax2.transAxes, fontsize=12)
            ax2.set_title("Top Conditions by Total Cost", fontweight="bold", fontsize=11)
    except Exception as e:
        print(f"⚠️ Error creating Chart 2: {e}")
        ax2.text(0.5, 0.5, f"Error: {str(e)[:50]}", 
                 ha="center", va="center", transform=ax2.transAxes, fontsize=10)
        ax2.set_title("Top Conditions by Total Cost", fontweight="bold", fontsize=11)

    # ── Chart 3: Avg Cost by Admission Type (bar) ─────────────────────────────
    ax3 = fig.add_subplot(gs[1, 0])
    
    try:
        if df_admission is not None and not df_admission.empty:
            df_admission_clean = df_admission.dropna(subset=['avg_cost', 'admission_type'])
            
            if not df_admission_clean.empty and df_admission_clean["avg_cost"].max() > 0:
                bars3 = ax3.bar(
                    df_admission_clean["admission_type"],
                    df_admission_clean["avg_cost"],
                    color=COLOURS["admission"],
                    width=0.5
                )
                ax3.set_title("Average Cost by Admission Type", fontweight="bold", fontsize=12)
                ax3.set_ylabel("Average Cost (USD)", fontsize=10)
                ax3.tick_params(axis='x', labelsize=10)

                max_cost = df_admission_clean["avg_cost"].max()
                for bar in bars3:
                    h = bar.get_height()
                    ax3.text(
                        bar.get_x() + bar.get_width() / 2, h + max_cost * 0.03,
                        f"${h:,.0f}", ha="center", fontsize=9, fontweight="bold"
                    )
                for i, (_, row) in enumerate(df_admission_clean.iterrows()):
                    ax3.text(
                        i, row["avg_cost"] * 0.35,
                        f"Avg stay:\n{row['avg_stay']} days",
                        ha="center", fontsize=8, color="white", fontweight="bold"
                    )
                ax3.set_ylim(0, max_cost * 1.25)
                ax3.grid(axis="y", alpha=0.3, linestyle='--')
            else:
                ax3.text(0.5, 0.5, "No valid admission cost data", 
                         ha="center", va="center", transform=ax3.transAxes, fontsize=12)
                ax3.set_title("Average Cost by Admission Type", fontweight="bold", fontsize=11)
        else:
            ax3.text(0.5, 0.5, "No admission data available", 
                     ha="center", va="center", transform=ax3.transAxes, fontsize=12)
            ax3.set_title("Average Cost by Admission Type", fontweight="bold", fontsize=11)
    except Exception as e:
        print(f"⚠️ Error creating Chart 3: {e}")
        ax3.text(0.5, 0.5, f"Error: {str(e)[:50]}", 
                 ha="center", va="center", transform=ax3.transAxes, fontsize=10)
        ax3.set_title("Average Cost by Admission Type", fontweight="bold", fontsize=11)

    # ── Chart 4: Test Results Distribution (pie) ──────────────────────────────
    ax4 = fig.add_subplot(gs[1, 1])
    
    try:
        if df_tests is not None and not df_tests.empty:
            test_summary = df_tests.groupby("test_result")["total_tests"].sum()
            
            if test_summary.sum() > 0:
                colors = []
                for result in test_summary.index:
                    if result == "Normal":
                        colors.append(COLOURS["test_normal"])
                    elif result == "Inconclusive":
                        colors.append(COLOURS["test_inconc"])
                    elif result == "Abnormal":
                        colors.append(COLOURS["test_abnorm"])
                    else:
                        colors.append("#95A5A6")

                wedges, texts, autotexts = ax4.pie(
                    test_summary.values,
                    labels=test_summary.index,
                    colors=colors,
                    autopct="%1.1f%%",
                    startangle=90,
                    pctdistance=0.78,
                    wedgeprops={"edgecolor": "white", "linewidth": 2}
                )
                for at in autotexts:
                    at.set_fontsize(11)
                    at.set_color("white")
                    at.set_fontweight("bold")
                for t in texts:
                    t.set_fontsize(11)
                    t.set_fontweight("bold")
                ax4.set_title("Test Results Distribution", fontweight="bold", fontsize=12)
            else:
                ax4.text(0.5, 0.5, "No test results data", 
                         ha="center", va="center", transform=ax4.transAxes, fontsize=12)
                ax4.set_title("Test Results Distribution", fontweight="bold", fontsize=11)
        else:
            ax4.text(0.5, 0.5, "No test results data available", 
                     ha="center", va="center", transform=ax4.transAxes, fontsize=12)
            ax4.set_title("Test Results Distribution", fontweight="bold", fontsize=11)
    except Exception as e:
        print(f"⚠️ Error creating Chart 4: {e}")
        ax4.text(0.5, 0.5, f"Error: {str(e)[:50]}", 
                 ha="center", va="center", transform=ax4.transAxes, fontsize=10)
        ax4.set_title("Test Results Distribution", fontweight="bold", fontsize=11)

    plt.tight_layout()
    os.makedirs("charts", exist_ok=True)
    plt.savefig("charts/hospital_analysis_page1.png", dpi=150, bbox_inches="tight")
    print("\n  Page 1 saved: charts/hospital_analysis_page1.png")
    plt.show()


def make_page2(df_insurance, df_demographics, df_medications, df_gender):
    """
    Page 2: Insurance | Age Demographics | Medications | Gender
    """
    # ── Check if we have any data for this page ──────────────────────────────
    has_data = False
    
    if df_insurance is not None and not df_insurance.empty and df_insurance["patients"].max() > 0:
        has_data = True
    elif df_demographics is not None and not df_demographics.empty and df_demographics["patient_count"].max() > 0:
        has_data = True
    elif df_medications is not None and not df_medications.empty and df_medications["prescription_count"].max() > 0:
        has_data = True
    elif df_gender is not None and not df_gender.empty and df_gender["total_visits"].max() > 0:
        has_data = True
    
    if not has_data:
        print("\n⚠️ No data available for Page 2 charts - skipping")
        return
    
    print("\n[DEBUG] make_page2 - DataFrame shapes:")
    print(f"  df_insurance: {df_insurance.shape if df_insurance is not None else 'None'}")
    print(f"  df_demographics: {df_demographics.shape if df_demographics is not None else 'None'}")
    print(f"  df_medications: {df_medications.shape if df_medications is not None else 'None'}")
    print(f"  df_gender: {df_gender.shape if df_gender is not None else 'None'}")
    
    fig = plt.figure(figsize=(16, 11))
    fig.suptitle(
        "Hospital Patient Analysis  —  Page 2 of 4\n"
        "Insurance  ·  Demographics  ·  Medications  ·  Gender",
        fontsize=14, fontweight="bold", y=0.98
    )
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.30)

    # ── Chart 5: Insurance — Patients & Avg Billing (dual axis bar) ───────────
    ax5  = fig.add_subplot(gs[0, 0])
    ax5b = ax5.twinx()
    
    try:
        if df_insurance is not None and not df_insurance.empty:
            df_insurance_clean = df_insurance.dropna(subset=['patients', 'avg_bill', 'insurance_provider'])
            
            if not df_insurance_clean.empty and df_insurance_clean["patients"].max() > 0:
                x5    = range(len(df_insurance_clean))
                width = 0.35

                ax5.bar(
                    [i - width / 2 for i in x5],
                    df_insurance_clean["patients"],
                    width=width,
                    color=COLOURS["insurance"],
                    label="Patients"
                )
                ax5b.bar(
                    [i + width / 2 for i in x5],
                    df_insurance_clean["avg_bill"],
                    width=width,
                    color="#AED6F1",
                    alpha=0.9,
                    label="Avg Billing"
                )
                ax5.set_title("Insurance: Patients & Avg Billing", fontweight="bold", fontsize=12)
                ax5.set_ylabel("Number of Patients", color="#2C3E50", fontsize=10)
                ax5b.set_ylabel("Avg Billing (USD)", color="#2980B9", fontsize=10)
                ax5.set_xticks(list(x5))
                ax5.set_xticklabels(
                    df_insurance_clean["insurance_provider"], rotation=15, ha="right", fontsize=9
                )
                p1 = mpatches.Patch(color=COLOURS["insurance"][0], label="Patients (left)")
                p2 = mpatches.Patch(color="#AED6F1", label="Avg Billing (right)")
                ax5.legend(handles=[p1, p2], fontsize=8, loc="upper right")
                ax5.grid(axis="y", alpha=0.2, linestyle='--')
            else:
                ax5.text(0.5, 0.5, "No valid insurance data", 
                         ha="center", va="center", transform=ax5.transAxes, fontsize=12)
                ax5.set_title("Insurance: Patients & Avg Billing", fontweight="bold", fontsize=11)
        else:
            ax5.text(0.5, 0.5, "No insurance data available", 
                     ha="center", va="center", transform=ax5.transAxes, fontsize=12)
            ax5.set_title("Insurance: Patients & Avg Billing", fontweight="bold", fontsize=11)
    except Exception as e:
        print(f"⚠️ Error creating Chart 5: {e}")
        ax5.text(0.5, 0.5, f"Error: {str(e)[:50]}", 
                 ha="center", va="center", transform=ax5.transAxes, fontsize=10)
        ax5.set_title("Insurance: Patients & Avg Billing", fontweight="bold", fontsize=11)

    # ── Chart 6: Patients by Age Group (bar) ─────────────────────────────────
    ax6 = fig.add_subplot(gs[0, 1])
    
    try:
        if df_demographics is not None and not df_demographics.empty:
            df_demographics_clean = df_demographics.dropna(subset=['patient_count', 'age_group'])
            
            if not df_demographics_clean.empty:
                age_summary = (
                    df_demographics_clean
                    .groupby("age_group", as_index=False)
                    .agg(patient_count=("patient_count", "sum"),
                         avg_billing=("avg_billing", "mean"))
                )

                age_order = ["Under 18", "18-35", "36-60", "Over 60"]
                age_summary["sort_key"] = pd.Categorical(
                    age_summary["age_group"], categories=age_order, ordered=True
                )
                age_summary = age_summary.sort_values("sort_key").reset_index(drop=True)

                x6 = range(len(age_summary))

                if not age_summary.empty and age_summary["patient_count"].max() > 0:
                    bars6 = ax6.bar(
                        list(x6),
                        age_summary["patient_count"],
                        width=0.5,
                        color=COLOURS["age_groups"][: len(age_summary)],
                    )
                    ax6.set_title("Patients by Age Group", fontweight="bold", fontsize=12)
                    ax6.set_ylabel("Number of Patients", fontsize=10)
                    ax6.set_xticks(list(x6))
                    ax6.set_xticklabels(age_summary["age_group"], fontsize=10)

                    for bar in bars6:
                        h = bar.get_height()
                        ax6.text(
                            bar.get_x() + bar.get_width() / 2, h + age_summary["patient_count"].max() * 0.02,
                            f"{int(h):,}", ha="center", fontsize=9, fontweight="bold"
                        )
                    ax6.grid(axis="y", alpha=0.3, linestyle='--')
                else:
                    ax6.text(0.5, 0.5, "No valid demographic data", 
                             ha="center", va="center", transform=ax6.transAxes, fontsize=12)
                    ax6.set_title("Patients by Age Group", fontweight="bold", fontsize=11)
        else:
            ax6.text(0.5, 0.5, "No demographic data available", 
                     ha="center", va="center", transform=ax6.transAxes, fontsize=12)
            ax6.set_title("Patients by Age Group", fontweight="bold", fontsize=11)
    except Exception as e:
        print(f"⚠️ Error creating Chart 6: {e}")
        ax6.text(0.5, 0.5, f"Error: {str(e)[:50]}", 
                 ha="center", va="center", transform=ax6.transAxes, fontsize=10)
        ax6.set_title("Patients by Age Group", fontweight="bold", fontsize=11)

    # ── Chart 7: Most Prescribed Medications (horizontal bar) ─────────────────
    ax7 = fig.add_subplot(gs[1, 0])
    
    try:
        if df_medications is not None and not df_medications.empty:
            df_medications_clean = df_medications.dropna(subset=['prescription_count', 'medication_name'])
            
            if not df_medications_clean.empty and df_medications_clean["prescription_count"].max() > 0:
                df_med_sorted = (
                    df_medications_clean
                    .sort_values("prescription_count", ascending=True)
                    .tail(6)
                )

                bars7 = ax7.barh(
                    df_med_sorted["medication_name"],
                    df_med_sorted["prescription_count"],
                    color=COLOURS["medications"][: len(df_med_sorted)],
                    height=0.6
                )
                ax7.set_title("Most Prescribed Medications", fontweight="bold", fontsize=12)
                ax7.set_xlabel("Number of Prescriptions", fontsize=10)
                ax7.invert_yaxis()
                ax7.tick_params(axis='y', labelsize=10)

                max_count = df_med_sorted["prescription_count"].max()
                for bar in bars7:
                    w = bar.get_width()
                    ax7.text(
                        w + max_count * 0.01,
                        bar.get_y() + bar.get_height() / 2,
                        f"{int(w):,}", va="center", fontsize=9, fontweight="bold"
                    )
                ax7.set_xlim(0, max_count * 1.18)
                ax7.grid(axis="x", alpha=0.3, linestyle='--')
            else:
                ax7.text(0.5, 0.5, "No valid medication data", 
                         ha="center", va="center", transform=ax7.transAxes, fontsize=12)
                ax7.set_title("Most Prescribed Medications", fontweight="bold", fontsize=11)
        else:
            ax7.text(0.5, 0.5, "No medication data available", 
                     ha="center", va="center", transform=ax7.transAxes, fontsize=12)
            ax7.set_title("Most Prescribed Medications", fontweight="bold", fontsize=11)
    except Exception as e:
        print(f"⚠️ Error creating Chart 7: {e}")
        ax7.text(0.5, 0.5, f"Error: {str(e)[:50]}", 
                 ha="center", va="center", transform=ax7.transAxes, fontsize=10)
        ax7.set_title("Most Prescribed Medications", fontweight="bold", fontsize=11)

    # ── Chart 8: Gender — Visits & Avg Billing (dual axis bar) ────────────────
    ax8  = fig.add_subplot(gs[1, 1])
    ax8b = ax8.twinx()
    
    try:
        if df_gender is not None and not df_gender.empty:
            df_gender_clean = df_gender.dropna(subset=['total_visits', 'avg_billing', 'gender'])
            
            if not df_gender_clean.empty and df_gender_clean["total_visits"].max() > 0:
                x8    = range(len(df_gender_clean))
                width8 = 0.35

                bars8 = ax8.bar(
                    [i - width8 / 2 for i in x8],
                    df_gender_clean["total_visits"],
                    width=width8,
                    color=COLOURS["gender"],
                    label="Total Visits"
                )
                ax8b.bar(
                    [i + width8 / 2 for i in x8],
                    df_gender_clean["avg_billing"],
                    width=width8,
                    color="#AED6F1",
                    alpha=0.9,
                    label="Avg Billing"
                )
                ax8.set_title("Gender: Visits & Avg Billing", fontweight="bold", fontsize=12)
                ax8.set_ylabel("Total Visits", color="#2C3E50", fontsize=10)
                ax8b.set_ylabel("Avg Billing (USD)", color="#2980B9", fontsize=10)
                ax8.set_xticks(list(x8))
                ax8.set_xticklabels(df_gender_clean["gender"], fontsize=11)

                for bar in bars8:
                    h = bar.get_height()
                    ax8.text(
                        bar.get_x() + bar.get_width() / 2,
                        h + df_gender_clean["total_visits"].max() * 0.02,
                        f"{int(h):,}", ha="center", fontsize=9, fontweight="bold"
                    )

                p1 = mpatches.Patch(color=COLOURS["gender"][0], label="Visits (left)")
                p2 = mpatches.Patch(color="#AED6F1", label="Avg Billing (right)")
                ax8.legend(handles=[p1, p2], fontsize=8, loc="upper right")
                ax8.grid(axis="y", alpha=0.2, linestyle='--')
            else:
                ax8.text(0.5, 0.5, "No valid gender data", 
                         ha="center", va="center", transform=ax8.transAxes, fontsize=12)
                ax8.set_title("Gender: Visits & Avg Billing", fontweight="bold", fontsize=11)
        else:
            ax8.text(0.5, 0.5, "No gender data available", 
                     ha="center", va="center", transform=ax8.transAxes, fontsize=12)
            ax8.set_title("Gender: Visits & Avg Billing", fontweight="bold", fontsize=11)
    except Exception as e:
        print(f"⚠️ Error creating Chart 8: {e}")
        ax8.text(0.5, 0.5, f"Error: {str(e)[:50]}", 
                 ha="center", va="center", transform=ax8.transAxes, fontsize=10)
        ax8.set_title("Gender: Visits & Avg Billing", fontweight="bold", fontsize=11)

    plt.tight_layout()
    plt.savefig("charts/hospital_analysis_page2.png", dpi=150, bbox_inches="tight")
    print("  Page 2 saved: charts/hospital_analysis_page2.png")
    plt.show()


def make_page3(df_doctors, df_demographics, df_conditions, df_admission):
    """
    Page 3: Doctor Workload | Cost Per Visit | Condition Summary | Admission Summary
    """
    # ── Check if we have any data for this page ──────────────────────────────
    has_data = False
    
    if df_doctors is not None and not df_doctors.empty and df_doctors["patients_handled"].max() > 0:
        has_data = True
    elif df_conditions is not None and not df_conditions.empty and df_conditions["cost_per_visit"].max() > 0:
        has_data = True
    elif df_conditions is not None and not df_conditions.empty and df_conditions["patient_count"].max() > 0:
        has_data = True
    elif df_admission is not None and not df_admission.empty and df_admission["visits"].max() > 0:
        has_data = True
    
    if not has_data:
        print("\n⚠️ No data available for Page 3 charts - skipping")
        return
    
    print("\n[DEBUG] make_page3 - DataFrame shapes:")
    print(f"  df_doctors: {df_doctors.shape if df_doctors is not None else 'None'}")
    print(f"  df_demographics: {df_demographics.shape if df_demographics is not None else 'None'}")
    print(f"  df_conditions: {df_conditions.shape if df_conditions is not None else 'None'}")
    print(f"  df_admission: {df_admission.shape if df_admission is not None else 'None'}")
    
    fig = plt.figure(figsize=(16, 11))
    fig.suptitle(
        "Hospital Patient Analysis  —  Page 3 of 4\n"
        "Doctors  ·  Cost Per Visit  ·  Conditions  ·  Admission Summary",
        fontsize=14, fontweight="bold", y=0.98
    )
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.30)

    # ── Chart 9: Doctor Workload (horizontal bar) ──────────────────────────────
    ax9 = fig.add_subplot(gs[0, 0])
    
    try:
        if df_doctors is not None and not df_doctors.empty:
            df_doctors_clean = df_doctors.dropna(subset=['patients_handled', 'doctor_name'])
            
            if not df_doctors_clean.empty and df_doctors_clean["patients_handled"].max() > 0:
                df_doc_sorted = (
                    df_doctors_clean
                    .sort_values("patients_handled", ascending=True)
                    .tail(8)
                )
                
                if not df_doc_sorted.empty and df_doc_sorted["patients_handled"].max() > 0:
                    bars9 = ax9.barh(
                        df_doc_sorted["doctor_name"],
                        df_doc_sorted["patients_handled"],
                        color=COLOURS["doctors"][: min(len(df_doc_sorted), len(COLOURS["doctors"]))],
                        height=0.6
                    )
                    ax9.set_title("Doctor Workload (Patients Handled)", fontweight="bold", fontsize=12)
                    ax9.set_xlabel("Number of Patients", fontsize=10)
                    ax9.invert_yaxis()
                    ax9.tick_params(axis='y', labelsize=9)

                    max_value = df_doc_sorted["patients_handled"].max()
                    for bar in bars9:
                        w = bar.get_width()
                        ax9.text(
                            w + max_value * 0.01,
                            bar.get_y() + bar.get_height() / 2,
                            f"{int(w):,}", va="center", fontsize=9, fontweight="bold"
                        )
                    ax9.set_xlim(0, max_value * 1.18)
                    ax9.grid(axis="x", alpha=0.3, linestyle='--')
                else:
                    ax9.text(0.5, 0.5, "No valid doctor data after sorting", 
                             ha="center", va="center", transform=ax9.transAxes, fontsize=12)
                    ax9.set_title("Doctor Workload (Patients Handled)", fontweight="bold", fontsize=11)
            else:
                ax9.text(0.5, 0.5, "No valid doctor workload data", 
                         ha="center", va="center", transform=ax9.transAxes, fontsize=12)
                ax9.set_title("Doctor Workload (Patients Handled)", fontweight="bold", fontsize=11)
        else:
            ax9.text(0.5, 0.5, "No doctor data available", 
                     ha="center", va="center", transform=ax9.transAxes, fontsize=12)
            ax9.set_title("Doctor Workload (Patients Handled)", fontweight="bold", fontsize=11)
    except Exception as e:
        print(f"⚠️ Error creating Chart 9: {e}")
        ax9.text(0.5, 0.5, f"Error: {str(e)[:50]}", 
                 ha="center", va="center", transform=ax9.transAxes, fontsize=10)
        ax9.set_title("Doctor Workload (Patients Handled)", fontweight="bold", fontsize=11)

    # ── Chart 10: Cost Per Visit by Condition (bar) ───────────────────────────
    ax10 = fig.add_subplot(gs[0, 1])
    
    try:
        if df_conditions is not None and not df_conditions.empty:
            df_conditions_clean = df_conditions.dropna(subset=['cost_per_visit', 'condition_name'])
            
            if not df_conditions_clean.empty and df_conditions_clean["cost_per_visit"].max() > 0:
                df_cond_cost = df_conditions_clean.sort_values("cost_per_visit", ascending=False).head(6)
                
                if not df_cond_cost.empty and df_cond_cost["cost_per_visit"].max() > 0:
                    ax10.set_xticks(range(len(df_cond_cost)))
                    bars10 = ax10.bar(
                        range(len(df_cond_cost)),
                        df_cond_cost["cost_per_visit"],
                        color=COLOURS["conditions"][: len(df_cond_cost)],
                        width=0.5
                    )
                    ax10.set_title("Cost Per Visit by Condition", fontweight="bold", fontsize=12)
                    ax10.set_ylabel("Cost Per Visit (USD)", fontsize=10)
                    ax10.set_xticklabels(
                        df_cond_cost["condition_name"], rotation=25, ha="right", fontsize=9
                    )

                    max_value = df_cond_cost["cost_per_visit"].max()
                    for bar in bars10:
                        h = bar.get_height()
                        ax10.text(
                            bar.get_x() + bar.get_width() / 2,
                            h + max_value * 0.02,
                            f"${h:,.0f}", ha="center", fontsize=8, fontweight="bold"
                        )
                    ax10.set_ylim(0, max_value * 1.22)
                    ax10.grid(axis="y", alpha=0.3, linestyle='--')
                else:
                    ax10.text(0.5, 0.5, "No valid cost data", 
                             ha="center", va="center", transform=ax10.transAxes, fontsize=12)
                    ax10.set_title("Cost Per Visit by Condition", fontweight="bold", fontsize=11)
            else:
                ax10.text(0.5, 0.5, "No valid condition data", 
                         ha="center", va="center", transform=ax10.transAxes, fontsize=12)
                ax10.set_title("Cost Per Visit by Condition", fontweight="bold", fontsize=11)
        else:
            ax10.text(0.5, 0.5, "No condition data available", 
                      ha="center", va="center", transform=ax10.transAxes, fontsize=12)
            ax10.set_title("Cost Per Visit by Condition", fontweight="bold", fontsize=11)
    except Exception as e:
        print(f"⚠️ Error creating Chart 10: {e}")
        ax10.text(0.5, 0.5, f"Error: {str(e)[:50]}", 
                  ha="center", va="center", transform=ax10.transAxes, fontsize=10)
        ax10.set_title("Cost Per Visit by Condition", fontweight="bold", fontsize=11)

    # ── Chart 11: Patients & Avg Stay by Condition (dual axis bar) ────────────
    ax11  = fig.add_subplot(gs[1, 0])
    ax11b = ax11.twinx()
    
    try:
        if df_conditions is not None and not df_conditions.empty:
            df_conditions_clean = df_conditions.dropna(subset=['patient_count', 'avg_stay_days', 'condition_name'])
            
            if not df_conditions_clean.empty and df_conditions_clean["patient_count"].max() > 0:
                df_cond2 = df_conditions_clean.sort_values("patient_count", ascending=False).head(6)
                
                if not df_cond2.empty and df_cond2["patient_count"].max() > 0:
                    x11   = range(len(df_cond2))
                    w11   = 0.35

                    ax11.bar(
                        [i - w11 / 2 for i in x11],
                        df_cond2["patient_count"],
                        width=w11,
                        color=COLOURS["conditions"],
                        label="Patients"
                    )
                    ax11b.bar(
                        [i + w11 / 2 for i in x11],
                        df_cond2["avg_stay_days"],
                        width=w11,
                        color="#BDC3C7",
                        alpha=0.85,
                        label="Avg Stay"
                    )
                    ax11.set_title("Patients & Avg Stay by Condition", fontweight="bold", fontsize=12)
                    ax11.set_ylabel("Number of Patients", color="#2C3E50", fontsize=10)
                    ax11b.set_ylabel("Avg Stay (days)", color="#7F8C8D", fontsize=10)
                    ax11.set_xticks(list(x11))
                    ax11.set_xticklabels(
                        df_cond2["condition_name"], rotation=25, ha="right", fontsize=9
                    )

                    for bar in ax11.patches:
                        h = bar.get_height()
                        ax11.text(
                            bar.get_x() + bar.get_width() / 2,
                            h + df_cond2["patient_count"].max() * 0.01,
                            f"{int(h):,}", ha="center", fontsize=8
                        )

                    p1 = mpatches.Patch(color=COLOURS["conditions"][0], label="Patients (left)")
                    p2 = mpatches.Patch(color="#BDC3C7", label="Avg Stay days (right)")
                    ax11.legend(handles=[p1, p2], fontsize=8, loc="upper left")
                    ax11.grid(axis="y", alpha=0.2, linestyle='--')
                else:
                    ax11.text(0.5, 0.5, "No valid condition data", 
                             ha="center", va="center", transform=ax11.transAxes, fontsize=12)
                    ax11.set_title("Patients & Avg Stay by Condition", fontweight="bold", fontsize=11)
            else:
                ax11.text(0.5, 0.5, "No condition data available", 
                          ha="center", va="center", transform=ax11.transAxes, fontsize=12)
                ax11.set_title("Patients & Avg Stay by Condition", fontweight="bold", fontsize=11)
        else:
            ax11.text(0.5, 0.5, "No condition data available", 
                      ha="center", va="center", transform=ax11.transAxes, fontsize=12)
            ax11.set_title("Patients & Avg Stay by Condition", fontweight="bold", fontsize=11)
    except Exception as e:
        print(f"⚠️ Error creating Chart 11: {e}")
        ax11.text(0.5, 0.5, f"Error: {str(e)[:50]}", 
                  ha="center", va="center", transform=ax11.transAxes, fontsize=10)
        ax11.set_title("Patients & Avg Stay by Condition", fontweight="bold", fontsize=11)

    # ── Chart 12: Admission Type — Visits & Avg Stay (dual axis bar) ──────────
    ax12  = fig.add_subplot(gs[1, 1])
    ax12b = ax12.twinx()
    
    try:
        if df_admission is not None and not df_admission.empty:
            df_admission_clean = df_admission.dropna(subset=['visits', 'avg_stay', 'admission_type'])
            
            if not df_admission_clean.empty and df_admission_clean["visits"].max() > 0:
                x12  = range(len(df_admission_clean))
                w12  = 0.35

                ax12.bar(
                    [i - w12 / 2 for i in x12],
                    df_admission_clean["visits"],
                    width=w12,
                    color=COLOURS["admission"],
                    label="Visits"
                )
                ax12b.bar(
                    [i + w12 / 2 for i in x12],
                    df_admission_clean["avg_stay"],
                    width=w12,
                    color="#AED6F1",
                    alpha=0.9,
                    label="Avg Stay"
                )
                ax12.set_title("Admission Type: Visits & Avg Stay", fontweight="bold", fontsize=12)
                ax12.set_ylabel("Number of Visits", color="#2C3E50", fontsize=10)
                ax12b.set_ylabel("Avg Stay (days)", color="#2980B9", fontsize=10)
                ax12.set_xticks(list(x12))
                ax12.set_xticklabels(df_admission_clean["admission_type"], fontsize=10)

                for bar in ax12.patches:
                    h = bar.get_height()
                    ax12.text(
                        bar.get_x() + bar.get_width() / 2,
                        h + df_admission_clean["visits"].max() * 0.02,
                        f"{int(h):,}", ha="center", fontsize=9, fontweight="bold"
                    )

                p1 = mpatches.Patch(color=COLOURS["admission"][0], label="Visits (left)")
                p2 = mpatches.Patch(color="#AED6F1", label="Avg Stay (right)")
                ax12.legend(handles=[p1, p2], fontsize=8, loc="upper right")
                ax12b.legend(fontsize=8, loc="upper left")
                ax12.grid(axis="y", alpha=0.2, linestyle='--')
            else:
                ax12.text(0.5, 0.5, "No valid admission data", 
                         ha="center", va="center", transform=ax12.transAxes, fontsize=12)
                ax12.set_title("Admission Type: Visits & Avg Stay", fontweight="bold", fontsize=11)
        else:
            ax12.text(0.5, 0.5, "No admission data available", 
                      ha="center", va="center", transform=ax12.transAxes, fontsize=12)
            ax12.set_title("Admission Type: Visits & Avg Stay", fontweight="bold", fontsize=11)
    except Exception as e:
        print(f"⚠️ Error creating Chart 12: {e}")
        ax12.text(0.5, 0.5, f"Error: {str(e)[:50]}", 
                  ha="center", va="center", transform=ax12.transAxes, fontsize=10)
        ax12.set_title("Admission Type: Visits & Avg Stay", fontweight="bold", fontsize=11)

    plt.tight_layout()
    plt.savefig("charts/hospital_analysis_page3.png", dpi=150, bbox_inches="tight")
    print("  Page 3 saved: charts/hospital_analysis_page3.png")
    plt.show()


def make_page4(df_top_districts, df_disease_trend, df_high_risk, df_district_summary):
    """
    Page 4: District Analysis — Top Districts | Disease Trend | High Risk Regions | District Summary
    """
    # ── Check if we have any data for this page ──────────────────────────────
    has_data = False
    
    if df_top_districts is not None and not df_top_districts.empty and df_top_districts["total_cases"].max() > 0:
        has_data = True
    elif df_disease_trend is not None and not df_disease_trend.empty and df_disease_trend["total_cases"].max() > 0:
        has_data = True
    elif df_high_risk is not None and not df_high_risk.empty and df_high_risk["total_cases"].max() > 0:
        has_data = True
    elif df_district_summary is not None and not df_district_summary.empty:
        has_data = True
    
    if not has_data:
        print("\n⚠️ No district data available for Page 4 charts - skipping")
        return
    
    print("\n[DEBUG] make_page4 - DataFrame shapes:")
    print(f"  df_top_districts: {df_top_districts.shape if df_top_districts is not None else 'None'}")
    print(f"  df_disease_trend: {df_disease_trend.shape if df_disease_trend is not None else 'None'}")
    print(f"  df_high_risk: {df_high_risk.shape if df_high_risk is not None else 'None'}")
    print(f"  df_district_summary: {df_district_summary.shape if df_district_summary is not None else 'None'}")
    
    fig = plt.figure(figsize=(16, 11))
    fig.suptitle(
        "Hospital Patient Analysis  —  Page 4 of 4\n"
        "District Analysis  ·  Top Districts  ·  Disease Trends  ·  Risk Regions",
        fontsize=14, fontweight="bold", y=0.98
    )
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.30)

    # ── Chart 13: Top Districts by Cases (horizontal bar) ─────────────────────
    ax13 = fig.add_subplot(gs[0, 0])
    
    try:
        if df_top_districts is not None and not df_top_districts.empty:
            df_top_districts_clean = df_top_districts.dropna(subset=['total_cases', 'district_name'])
            
            if not df_top_districts_clean.empty and df_top_districts_clean["total_cases"].max() > 0:
                df_top = df_top_districts_clean.sort_values("total_cases", ascending=True).tail(6)
                
                bars13 = ax13.barh(
                    df_top["district_name"],
                    df_top["total_cases"],
                    color=COLOURS["districts"][:len(df_top)],
                    height=0.6
                )
                ax13.set_title("Top Districts by Case Volume", fontweight="bold", fontsize=12)
                ax13.set_xlabel("Number of Cases", fontsize=10)
                ax13.invert_yaxis()
                ax13.tick_params(axis='y', labelsize=9)

                max_cases = df_top["total_cases"].max()
                for bar in bars13:
                    w = bar.get_width()
                    ax13.text(
                        w + max_cases * 0.01,
                        bar.get_y() + bar.get_height() / 2,
                        f"{int(w):,}", va="center", fontsize=9, fontweight="bold"
                    )
                ax13.set_xlim(0, max_cases * 1.18)
                ax13.grid(axis="x", alpha=0.3, linestyle='--')
            else:
                ax13.text(0.5, 0.5, "No valid district data", 
                         ha="center", va="center", transform=ax13.transAxes, fontsize=12)
                ax13.set_title("Top Districts by Case Volume", fontweight="bold", fontsize=11)
        else:
            ax13.text(0.5, 0.5, "No district data available", 
                      ha="center", va="center", transform=ax13.transAxes, fontsize=12)
            ax13.set_title("Top Districts by Case Volume", fontweight="bold", fontsize=11)
    except Exception as e:
        print(f"⚠️ Error creating Chart 13: {e}")
        ax13.text(0.5, 0.5, f"Error: {str(e)[:50]}", 
                  ha="center", va="center", transform=ax13.transAxes, fontsize=10)
        ax13.set_title("Top Districts by Case Volume", fontweight="bold", fontsize=11)

    # ── Chart 14: Disease Trend Over Years (line chart) ──────────────────────
    ax14 = fig.add_subplot(gs[0, 1])
    
    try:
        if df_disease_trend is not None and not df_disease_trend.empty:
            df_disease_trend_clean = df_disease_trend.dropna(subset=['year', 'total_cases'])
            
            if not df_disease_trend_clean.empty and df_disease_trend_clean["total_cases"].max() > 0:
                ax14.plot(
                    df_disease_trend_clean["year"],
                    df_disease_trend_clean["total_cases"],
                    marker="o", linewidth=2.5, markersize=8, color="#E74C3C"
                )
                ax14.set_title("Disease Case Trend Over Years", fontweight="bold", fontsize=12)
                ax14.set_xlabel("Year", fontsize=10)
                ax14.set_ylabel("Number of Cases", fontsize=10)
                ax14.grid(axis="y", alpha=0.3, linestyle='--')
                ax14.set_xticks(df_disease_trend_clean["year"])
                ax14.tick_params(axis='x', labelsize=10)

                max_cases = df_disease_trend_clean["total_cases"].max()
                for i, (_, row) in enumerate(df_disease_trend_clean.iterrows()):
                    ax14.text(
                        row["year"], row["total_cases"] + max_cases * 0.02,
                        f"{int(row['total_cases']):,}", ha="center", fontsize=9, fontweight="bold"
                    )
            else:
                ax14.text(0.5, 0.5, "No valid disease trend data", 
                         ha="center", va="center", transform=ax14.transAxes, fontsize=12)
                ax14.set_title("Disease Case Trend Over Years", fontweight="bold", fontsize=11)
        else:
            ax14.text(0.5, 0.5, "No disease trend data available", 
                      ha="center", va="center", transform=ax14.transAxes, fontsize=12)
            ax14.set_title("Disease Case Trend Over Years", fontweight="bold", fontsize=11)
    except Exception as e:
        print(f"⚠️ Error creating Chart 14: {e}")
        ax14.text(0.5, 0.5, f"Error: {str(e)[:50]}", 
                  ha="center", va="center", transform=ax14.transAxes, fontsize=10)
        ax14.set_title("Disease Case Trend Over Years", fontweight="bold", fontsize=11)

    # ── Chart 15: High Risk Regions (horizontal bar with colors) ─────────────
    ax15 = fig.add_subplot(gs[1, 0])
    
    try:
        if df_high_risk is not None and not df_high_risk.empty:
            df_high_risk_clean = df_high_risk.dropna(subset=['total_cases', 'region'])
            
            if not df_high_risk_clean.empty and df_high_risk_clean["total_cases"].max() > 0:
                df_risk = df_high_risk_clean.sort_values("total_cases", ascending=True)
                
                colors = []
                for _, row in df_risk.iterrows():
                    colors.append(COLOURS["risk"].get(row["risk_level"], "#95A5A6"))
                
                bars15 = ax15.barh(
                    df_risk["region"],
                    df_risk["total_cases"],
                    color=colors,
                    height=0.6
                )
                ax15.set_title("High Risk Regions by Case Volume", fontweight="bold", fontsize=12)
                ax15.set_xlabel("Number of Cases", fontsize=10)
                ax15.invert_yaxis()
                ax15.tick_params(axis='y', labelsize=10)

                max_cases = df_risk["total_cases"].max()
                for bar in bars15:
                    w = bar.get_width()
                    ax15.text(
                        w + max_cases * 0.01,
                        bar.get_y() + bar.get_height() / 2,
                        f"{int(w):,}", va="center", fontsize=9, fontweight="bold"
                    )
                ax15.set_xlim(0, max_cases * 1.18)
                ax15.grid(axis="x", alpha=0.3, linestyle='--')
                
                # Add risk level legend
                risk_patches = []
                for risk_level, color in COLOURS["risk"].items():
                    if risk_level in df_risk["risk_level"].values:
                        risk_patches.append(mpatches.Patch(color=color, label=risk_level))
                if risk_patches:
                    ax15.legend(handles=risk_patches, fontsize=8, loc="lower right")
            else:
                ax15.text(0.5, 0.5, "No valid risk region data", 
                         ha="center", va="center", transform=ax15.transAxes, fontsize=12)
                ax15.set_title("High Risk Regions by Case Volume", fontweight="bold", fontsize=11)
        else:
            ax15.text(0.5, 0.5, "No high risk regions identified", 
                      ha="center", va="center", transform=ax15.transAxes, fontsize=12)
            ax15.set_title("High Risk Regions by Case Volume", fontweight="bold", fontsize=11)
    except Exception as e:
        print(f"⚠️ Error creating Chart 15: {e}")
        ax15.text(0.5, 0.5, f"Error: {str(e)[:50]}", 
                  ha="center", va="center", transform=ax15.transAxes, fontsize=10)
        ax15.set_title("High Risk Regions by Case Volume", fontweight="bold", fontsize=11)

    # ── Chart 16: District Summary Stats (cards) ─────────────────────────────
    ax16 = fig.add_subplot(gs[1, 1])
    ax16.axis("off")
    ax16.set_title("District Summary Statistics", fontweight="bold", fontsize=12)
    
    try:
        if df_district_summary is not None and not df_district_summary.empty:
            stats = df_district_summary.iloc[0]
            
            summary_text = f"""
        📊 DISTRICT OVERVIEW
        ─────────────────────
        Total Districts      : {int(stats['total_districts']):,}
        Total Regions        : {int(stats['total_regions']):,}
        Total Sub-Regions    : {int(stats['total_sub_regions']):,}
        
        🏙️   Urban/Rural Split
        ─────────────────────
        Urban Districts      : {int(stats['urban_districts']):,}
        Rural Districts      : {int(stats['rural_districts']):,}
        
        👥 Population
        ─────────────────────
        Total Population     : {int(stats['total_population']):,}
        Avg per District     : {int(stats['avg_population_per_district']):,}
        """
            
            ax16.text(0.1, 0.5, summary_text, 
                      transform=ax16.transAxes, fontsize=11, verticalalignment='center',
                      fontfamily='monospace')
        else:
            ax16.text(0.5, 0.5, "No district summary data available", 
                      ha="center", va="center", transform=ax16.transAxes, fontsize=10)
    except Exception as e:
        print(f"⚠️ Error creating Chart 16: {e}")
        ax16.text(0.5, 0.5, f"Error: {str(e)[:50]}", 
                  ha="center", va="center", transform=ax16.transAxes, fontsize=8)

    plt.tight_layout()
    os.makedirs("charts", exist_ok=True)
    plt.savefig("charts/hospital_analysis_page4.png", dpi=150, bbox_inches="tight")
    print("  Page 4 saved: charts/hospital_analysis_page4.png")
    plt.show()


# =============================================================================
# SECTION 4 — TERMINAL SUMMARY REPORT
# =============================================================================

def print_summary(df1, df2, df4, df5, df6, df8, df9, df10, 
                  df_top_districts=None, df_high_risk=None, df_district_summary=None):
    """
    Prints a readable text report of all key findings to the terminal.
    Expanded with district statistics.
    """
    line   = "-" * 58
    dline  = "=" * 58

    total_revenue  = df1["total_revenue"].sum()
    total_patients = df1["total_patients"].sum()
    total_visits   = df10["total_visits"].sum()

    print(f"\n{dline}")
    print("  HOSPITAL ANALYSIS — SUMMARY REPORT")
    print("  Star Schema · imdb database · public schema")
    print(dline)
    print(f"\n  Total Patients       : {total_patients:>10,.0f}")
    print(f"  Total Visits         : {total_visits:>10,.0f}")
    print(f"  Total Revenue        : ${total_revenue:>12,.2f}")
    print(f"  Avg Monthly Revenue  : ${df1['total_revenue'].mean():>12,.2f}")
    print(f"  Overall Avg Billing  : ${df1['avg_billing'].mean():>12,.2f}")
    print(f"  Overall Avg Stay     : {df1['avg_stay_days'].mean():>8.1f} days")

    # Monthly revenue
    print(f"\n{line}")
    print("  MONTHLY REVENUE")
    print(line)
    max_rev = df1["total_revenue"].max()
    for _, row in df1.iterrows():
        bar = "█" * int(row["total_revenue"] / max_rev * 28)
        print(f"  {row['year']}-{row['month_name'][:3]:<5} "
              f"${row['total_revenue']:>12,.2f}  "
              f"{bar}  ({int(row['total_patients'])} patients)")

    # Top conditions
    print(f"\n{line}")
    print("  TOP MEDICAL CONDITIONS BY COST")
    print(line)
    max_cost = df2["total_cost"].max()
    for _, row in df2.head(6).iterrows():
        bar = "█" * int(row["total_cost"] / max_cost * 28)
        print(f"  {row['condition_name']:<20} "
              f"${row['total_cost']:>12,.2f}  "
              f"{bar}  ({int(row['patient_count'])} patients)")

    # Insurance
    print(f"\n{line}")
    print("  INSURANCE PROVIDERS")
    print(line)
    max_pts = df4["patients"].max()
    for _, row in df4.iterrows():
        bar = "█" * int(row["patients"] / max_pts * 28)
        print(f"  {row['insurance_provider']:<20} "
              f"{int(row['patients']):>4} patients  "
              f"${row['avg_bill']:>10,.2f} avg  "
              f"{bar}")

    # Admission types
    print(f"\n{line}")
    print("  ADMISSION TYPES")
    print(line)
    max_vis = df5["visits"].max()
    for _, row in df5.iterrows():
        bar = "█" * int(row["visits"] / max_vis * 28)
        print(f"  {row['admission_type']:<12} "
              f"{int(row['visits']):>5} visits  "
              f"${row['avg_cost']:>10,.2f} avg cost  "
              f"{row['avg_stay']:>4} days avg  "
              f"{bar}")

    # Top doctors
    print(f"\n{line}")
    print("  TOP DOCTORS BY PATIENT VOLUME")
    print(line)
    max_doc = df6["patients_handled"].max()
    for _, row in df6.head(5).iterrows():
        bar = "█" * int(row["patients_handled"] / max_doc * 28)
        print(f"  {str(row['doctor_name'])[:22]:<24} "
              f"{int(row['patients_handled']):>3} patients  "
              f"${row['total_revenue']:>12,.2f} revenue  "
              f"{bar}")

    # Medications
    print(f"\n{line}")
    print("  MOST PRESCRIBED MEDICATIONS")
    print(line)
    max_rx = df8["prescription_count"].max()
    for _, row in df8.head(5).iterrows():
        bar = "█" * int(row["prescription_count"] / max_rx * 28)
        print(f"  {str(row['medication_name'])[:22]:<24} "
              f"{int(row['prescription_count']):>4} prescriptions  "
              f"${row['avg_billing']:>10,.2f} avg  "
              f"{bar}")

    # Test results
    print(f"\n{line}")
    print("  TEST RESULTS DISTRIBUTION")
    print(line)
    total_tests = df9["total_tests"].sum()
    for _, row in df9.iterrows():
        pct = 100 * row["total_tests"] / total_tests
        bar = "█" * int(pct / 2)
        print(f"  {row['test_result']:<14} "
              f"{int(row['total_tests']):>5} tests  "
              f"({pct:5.1f}%)  {bar}")

    # Gender
    print(f"\n{line}")
    print("  GENDER BREAKDOWN")
    print(line)
    total_v = df10["total_visits"].sum()
    for _, row in df10.iterrows():
        pct = 100 * row["total_visits"] / total_v
        bar = "█" * int(pct / 2)
        print(f"  {row['gender']:<10} "
              f"{int(row['total_visits']):>6} visits  "
              f"${row['avg_billing']:>10,.2f} avg  "
              f"({pct:5.1f}%)  {bar}")

    # ── District Statistics (NEW) ────────────────────────────────────────────
    if df_top_districts is not None and not df_top_districts.empty:
        print(f"\n{line}")
        print("  🏆 TOP DISTRICTS BY CASES")
        print(line)
        for _, row in df_top_districts.head(5).iterrows():
            bar = "█" * int(row["total_cases"] / df_top_districts["total_cases"].max() * 28)
            print(f"  {row['district_name']:<20} "
                  f"{int(row['total_cases']):>5} cases  "
                  f"${row['total_revenue']:>12,.2f} revenue  "
                  f"{bar}  ({int(row['unique_patients'])} patients)")
            
            if 'cases_per_100k' in row:
                print(f"  {'':20}  Cases per 100k: {row['cases_per_100k']}  "
                      f"Region: {row['region']}  "
                      f"{'Urban' if row['is_urban'] else 'Rural'}")

    if df_high_risk is not None and not df_high_risk.empty:
        print(f"\n{line}")
        print("  ⚠️ HIGH RISK REGIONS")
        print(line)
        for _, row in df_high_risk.head(3).iterrows():
            risk_symbol = {
                'CRITICAL': '🔴',
                'HIGH': '🟠',
                'MEDIUM': '🟡'
            }.get(row['risk_level'], '⚪')
            print(f"  {risk_symbol} {row['region']:<15} "
                  f"{int(row['total_cases']):>6} cases  "
                  f"{row['risk_level']:<8}  "
                  f"{row['districts_affected']} districts  "
                  f"{row['cases_per_district']:.1f} avg/district")

    if df_district_summary is not None and not df_district_summary.empty:
        stats = df_district_summary.iloc[0]
        print(f"\n{line}")
        print("  📊 DISTRICT OVERVIEW")
        print(line)
        print(f"  Total Districts        : {int(stats['total_districts']):,}")
        print(f"  Total Regions          : {int(stats['total_regions']):,}")
        print(f"  Total Sub-Regions      : {int(stats['total_sub_regions']):,}")
        print(f"  Urban Districts        : {int(stats['urban_districts']):,}")
        print(f"  Rural Districts        : {int(stats['rural_districts']):,}")
        print(f"  Total Population       : {int(stats['total_population']):,}")
        print(f"  Avg Population/District: {int(stats['avg_population_per_district']):,}")

    print(f"\n{dline}\n")


def save_summary_to_file(df1, df2, df4, df5, df6, df8, df9, df10,
                         df11, df16, df17):
    """
    Generates a text-based Summary Report and saves it to a file
    inside a 'reports/' directory. Expanded with district statistics.
    """
    os.makedirs("reports", exist_ok=True)
    report_filepath = "reports/hospital_analysis_summary.txt"

    line   = "-" * 58
    dline  = "=" * 58

    total_revenue  = df1["total_revenue"].sum()
    total_patients = df1["total_patients"].sum()
    total_visits   = df10["total_visits"].sum()

    with open(report_filepath, "w", encoding="utf-8") as f:
        f.write(f"{dline}\n")
        f.write("  HOSPITAL ANALYSIS — AUTOMATED SUMMARY REPORT\n")
        f.write("  Star Schema · imdb database · public schema\n")
        f.write(f"{dline}\n")
        f.write(f"\n  Report Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"\n  Total Patients       : {total_patients:>10,.0f}\n")
        f.write(f"  Total Visits         : {total_visits:>10,.0f}\n")
        f.write(f"  Total Revenue        : ${total_revenue:>12,.2f}\n")
        f.write(f"  Avg Monthly Revenue  : ${df1['total_revenue'].mean():>12,.2f}\n")
        f.write(f"  Overall Avg Billing  : ${df1['avg_billing'].mean():>12,.2f}\n")
        f.write(f"  Overall Avg Stay     : {df1['avg_stay_days'].mean():>8.1f} days\n")

        # Monthly revenue
        f.write(f"\n{line}\n  MONTHLY REVENUE\n{line}\n")
        max_rev = df1["total_revenue"].max()
        for _, row in df1.iterrows():
            bar = "█" * int(row["total_revenue"] / max_rev * 28)
            f.write(f"  {row['year']}-{row['month_name'][:3]:<5} "
                    f"${row['total_revenue']:>12,.2f}  "
                    f"{bar}  ({int(row['total_patients'])} patients)\n")

        # Top conditions
        f.write(f"\n{line}\n  TOP MEDICAL CONDITIONS BY COST\n{line}\n")
        max_cost = df2["total_cost"].max()
        for _, row in df2.head(6).iterrows():
            bar = "█" * int(row["total_cost"] / max_cost * 28)
            f.write(f"  {row['condition_name']:<20} "
                    f"${row['total_cost']:>12,.2f}  "
                    f"{bar}  ({int(row['patient_count'])} patients)\n")

        # Insurance
        f.write(f"\n{line}\n  INSURANCE PROVIDERS\n{line}\n")
        max_pts = df4["patients"].max()
        for _, row in df4.iterrows():
            bar = "█" * int(row["patients"] / max_pts * 28)
            f.write(f"  {row['insurance_provider']:<20} "
                    f"{int(row['patients']):>4} patients  "
                    f"${row['avg_bill']:>10,.2f} avg  "
                    f"{bar}\n")

        # Admission types
        f.write(f"\n{line}\n  ADMISSION TYPES\n{line}\n")
        max_vis = df5["visits"].max()
        for _, row in df5.iterrows():
            bar = "█" * int(row["visits"] / max_vis * 28)
            f.write(f"  {row['admission_type']:<12} "
                    f"{int(row['visits']):>5} visits  "
                    f"${row['avg_cost']:>10,.2f} avg cost  "
                    f"{row['avg_stay']:>4} days avg  "
                    f"{bar}\n")

        # Top doctors
        f.write(f"\n{line}\n  TOP DOCTORS BY PATIENT VOLUME\n{line}\n")
        max_doc = df6["patients_handled"].max()
        for _, row in df6.head(5).iterrows():
            bar = "█" * int(row["patients_handled"] / max_doc * 28)
            f.write(f"  {str(row['doctor_name'])[:22]:<24} "
                    f"{int(row['patients_handled']):>3} patients  "
                    f"${row['total_revenue']:>12,.2f} revenue  "
                    f"{bar}\n")

        # Medications
        f.write(f"\n{line}\n  MOST PRESCRIBED MEDICATIONS\n{line}\n")
        max_rx = df8["prescription_count"].max()
        for _, row in df8.head(5).iterrows():
            bar = "█" * int(row["prescription_count"] / max_rx * 28)
            f.write(f"  {str(row['medication_name'])[:22]:<24} "
                    f"{int(row['prescription_count']):>4} prescriptions  "
                    f"${row['avg_billing']:>10,.2f} avg  "
                    f"{bar}\n")

        # Test results
        f.write(f"\n{line}\n  TEST RESULTS DISTRIBUTION\n{line}\n")
        total_tests = df9["total_tests"].sum()
        for _, row in df9.iterrows():
            pct = 100 * row["total_tests"] / total_tests
            bar = "█" * int(pct / 2)
            f.write(f"  {row['test_result']:<14} "
                    f"{int(row['total_tests']):>5} tests  "
                    f"({pct:5.1f}%)  {bar}\n")

        # Gender
        f.write(f"\n{line}\n  GENDER BREAKDOWN\n{line}\n")
        total_v = df10["total_visits"].sum()
        for _, row in df10.iterrows():
            pct = 100 * row["total_visits"] / total_v
            bar = "█" * int(pct / 2)
            f.write(f"  {row['gender']:<10} "
                    f"{int(row['total_visits']):>6} visits  "
                    f"${row['avg_billing']:>10,.2f} avg  "
                    f"({pct:5.1f}%)  {bar}\n")

        # ── District Statistics (NEW) ────────────────────────────────────────
        if df11 is not None and not df11.empty:
            f.write(f"\n{line}\n  🏆 TOP DISTRICTS BY CASES\n{line}\n")
            for _, row in df11.head(5).iterrows():
                bar = "█" * int(row["total_cases"] / df11["total_cases"].max() * 28)
                f.write(f"  {row['district_name']:<20} "
                        f"{int(row['total_cases']):>5} cases  "
                        f"${row['total_revenue']:>12,.2f} revenue  "
                        f"{bar}  ({int(row['unique_patients'])} patients)\n")
                if 'cases_per_100k' in row:
                    f.write(f"  {'':20}  Cases per 100k: {row['cases_per_100k']}  "
                            f"Region: {row['region']}  "
                            f"{'Urban' if row['is_urban'] else 'Rural'}\n")

        if df16 is not None and not df16.empty:
            f.write(f"\n{line}\n  ⚠️ HIGH RISK REGIONS\n{line}\n")
            for _, row in df16.head(3).iterrows():
                risk_symbol = {
                    'CRITICAL': '🔴',
                    'HIGH': '🟠',
                    'MEDIUM': '🟡'
                }.get(row['risk_level'], '⚪')
                f.write(f"  {risk_symbol} {row['region']:<15} "
                        f"{int(row['total_cases']):>6} cases  "
                        f"{row['risk_level']:<8}  "
                        f"{row['districts_affected']} districts  "
                        f"{row['cases_per_district']:.1f} avg/district\n")

        if df17 is not None and not df17.empty:
            stats = df17.iloc[0]
            f.write(f"\n{line}\n  📊 DISTRICT OVERVIEW\n{line}\n")
            f.write(f"  Total Districts        : {int(stats['total_districts']):,}\n")
            f.write(f"  Total Regions          : {int(stats['total_regions']):,}\n")
            f.write(f"  Total Sub-Regions      : {int(stats['total_sub_regions']):,}\n")
            f.write(f"  Urban Districts        : {int(stats['urban_districts']):,}\n")
            f.write(f"  Rural Districts        : {int(stats['rural_districts']):,}\n")
            f.write(f"  Total Population       : {int(stats['total_population']):,}\n")
            f.write(f"  Avg Population/District: {int(stats['avg_population_per_district']):,}\n")

        f.write(f"\n{dline}\n")
        
    print(f"✅ Text summary report saved: {report_filepath}")


# =============================================================================
# SECTION 5 — MAIN ENTRY POINT
# =============================================================================

def run_full_analysis():
    """
    Runs all queries, prints the terminal summary,
    and generates all chart pages including district analysis.
    """
    print("=" * 58)
    print("  HOSPITAL PATIENT ANALYSIS")
    print("  Database: imdb  |  Schema: public  |  Star Schema")
    print("=" * 58)
    print("\nRunning queries...\n")

    # ── Run all queries ───────────────────────────────────────────────────────
    df1  = q1_monthly_revenue()
    df2  = q2_conditions()
    df4  = q4_insurance()
    df5  = q5_admission_types()
    df6  = q6_doctors()
    df7  = q7_demographics()
    df8  = q8_medications()
    df9  = q9_test_results()
    df10 = q10_gender()
    df11 = q11_top_districts_by_cases(year=None, top_n=10)
    df12 = q12_trend_by_disease("Diabetes")  # Example disease
    df16 = q16_high_risk_regions(threshold=10)  # Adjust threshold as needed
    df17 = q17_district_summary()

    # ── Guard: check fact table returned data ─────────────────────────────────
    if df1.empty:
        print("\nNo data returned from q1_monthly_revenue().")
        print("Check that public.fact_patient_visits exists and contains rows.")
        return

    # ── Terminal report ───────────────────────────────────────────────────────
    print_summary(df1, df2, df4, df5, df6, df8, df9, df10,
                  df11, df16, df17)

    # ── Save report to file ───────────────────────────────────────────────────
    save_summary_to_file(df1, df2, df4, df5, df6, df8, df9, df10,
                         df11, df16, df17)

    # ── Charts ────────────────────────────────────────────────────────────────
    print("\nGenerating charts (conditional - only if data available)...\n")
    make_page1(df1, df2, df5, df9)
    make_page2(df4, df7, df8, df10)
    make_page3(df6, df7, df2, df5)
    make_page4(df11, df12, df16, df17)

    print("\n✅ Analysis complete.")
    print("Charts saved in: charts/")
    print("  charts/hospital_analysis_page1.png")
    print("  charts/hospital_analysis_page2.png")
    print("  charts/hospital_analysis_page3.png")
    print("  charts/hospital_analysis_page4.png")


if __name__ == "__main__":
    run_full_analysis()