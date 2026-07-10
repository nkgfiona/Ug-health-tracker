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
# ─────────────────────────────────────────────────────────────────────────────

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
# SECTION 2 — COLOUR PALETTE
# Consistent colours used across all three chart pages.
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
}


# =============================================================================
# SECTION 3 — CHART PAGES
# =============================================================================

def make_page1(df_monthly, df_conditions, df_admission, df_tests):
    """
    Page 1: Monthly Revenue | Top Conditions | Admission Costs | Test Results

    Parameters (named clearly to match what is passed):
        df_monthly   — from q1_monthly_revenue()
        df_conditions— from q2_conditions()
        df_admission — from q5_admission_types()
        df_tests     — from q9_test_results()
    """
    fig = plt.figure(figsize=(16, 11))
    fig.suptitle(
        "Hospital Patient Analysis  —  Page 1 of 3\n"
        "Monthly Revenue  ·  Conditions  ·  Admission Types  ·  Test Results",
        fontsize=13, fontweight="bold", y=0.98
    )
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.42, wspace=0.35)

    # ── Chart 1: Monthly Revenue Trend (line) ─────────────────────────────────
    ax1 = fig.add_subplot(gs[0, 0])

    df_monthly["date_label"] = (df_monthly["year"].astype(str)
                                + "-"
                                + df_monthly["month_name"].str[:3])

    ax1.plot(
        df_monthly["date_label"],
        df_monthly["total_revenue"],
        marker="o", linewidth=2, markersize=7, color="#2C3E50"
    )
    ax1.set_title("Monthly Revenue Trend", fontweight="bold", fontsize=11)
    ax1.set_xlabel("Month")
    ax1.set_ylabel("Total Revenue (USD)")
    ax1.tick_params(axis="x", rotation=45, labelsize=7)
    ax1.grid(axis="y", alpha=0.3)

    # FIX: use enumerate so label position is always a clean 0,1,2...
    # not the DataFrame's original index which can be non-sequential
    for i, (_, row) in enumerate(df_monthly.iterrows()):
        ax1.text(
            i, row["total_revenue"] + df_monthly["total_revenue"].max() * 0.02,
            f"${row['total_revenue']:,.0f}",
            ha="center", fontsize=7, fontweight="bold"
        )

    # ── Chart 2: Top Conditions by Total Cost (horizontal bar) ───────────────
    ax2 = fig.add_subplot(gs[0, 1])

    df_sorted = df_conditions.sort_values("total_cost", ascending=True).tail(6)

    bars = ax2.barh(
        df_sorted["condition_name"],
        df_sorted["total_cost"],
        color=COLOURS["conditions"][:len(df_sorted)],
        height=0.6
    )
    ax2.set_title("Top Conditions by Total Cost", fontweight="bold", fontsize=11)
    ax2.set_xlabel("Total Cost (USD)")
    ax2.invert_yaxis()

    for bar in bars:
        w = bar.get_width()
        ax2.text(
            w + df_sorted["total_cost"].max() * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"${w:,.0f}", va="center", fontsize=8
        )
    ax2.set_xlim(0, df_sorted["total_cost"].max() * 1.18)
    ax2.grid(axis="x", alpha=0.3)

    # ── Chart 3: Avg Cost by Admission Type (bar) ─────────────────────────────
    ax3 = fig.add_subplot(gs[1, 0])

    bars3 = ax3.bar(
        df_admission["admission_type"],
        df_admission["avg_cost"],
        color=COLOURS["admission"],
        width=0.6
    )
    ax3.set_title("Average Cost by Admission Type", fontweight="bold", fontsize=11)
    ax3.set_ylabel("Average Cost (USD)")
    ax3.set_ylim(0, df_admission["avg_cost"].max() * 1.25)

    for bar in bars3:
        h = bar.get_height()
        ax3.text(
            bar.get_x() + bar.get_width() / 2, h + df_admission["avg_cost"].max() * 0.02,
            f"${h:,.0f}", ha="center", fontsize=9, fontweight="bold"
        )
    # Avg stay annotation inside each bar
    for i, (_, row) in enumerate(df_admission.iterrows()):
        ax3.text(
            i, row["avg_cost"] * 0.25,
            f"Avg stay:\n{row['avg_stay']} days",
            ha="center", fontsize=8, color="white", fontweight="bold"
        )
    ax3.grid(axis="y", alpha=0.3)

    # ── Chart 4: Test Results Distribution (pie) ──────────────────────────────
    ax4 = fig.add_subplot(gs[1, 1])

    test_summary = df_tests.groupby("test_result")["total_tests"].sum()

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
        wedgeprops={"edgecolor": "white", "linewidth": 1.5}
    )
    for at in autotexts:
        at.set_fontsize(10)
        at.set_color("white")
        at.set_fontweight("bold")
    for t in texts:
        t.set_fontsize(10)
    ax4.set_title("Test Results Distribution", fontweight="bold", fontsize=11)

    os.makedirs("charts", exist_ok=True)
    plt.savefig("charts/hospital_analysis_page1.png", dpi=150, bbox_inches="tight")
    print("\n  Page 1 saved: charts/hospital_analysis_page1.png")
    plt.show()


def make_page2(df_insurance, df_demographics, df_medications, df_gender):
    """
    Page 2: Insurance | Age Demographics | Medications | Gender

    Parameters:
        df_insurance   — from q4_insurance()
        df_demographics— from q7_demographics()
        df_medications — from q8_medications()
        df_gender      — from q10_gender()
    """
    fig = plt.figure(figsize=(16, 11))
    fig.suptitle(
        "Hospital Patient Analysis  —  Page 2 of 3\n"
        "Insurance  ·  Demographics  ·  Medications  ·  Gender",
        fontsize=13, fontweight="bold", y=0.98
    )
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.38)

    # ── Chart 5: Insurance — Patients & Avg Billing (dual axis bar) ───────────
    ax5  = fig.add_subplot(gs[0, 0])
    ax5b = ax5.twinx()

    x5    = range(len(df_insurance))
    width = 0.35

    ax5.bar(
        [i - width / 2 for i in x5],
        df_insurance["patients"],
        width=width,
        color=COLOURS["insurance"],
        label="Patients"
    )
    ax5b.bar(
        [i + width / 2 for i in x5],
        df_insurance["avg_bill"],
        width=width,
        color="#AED6F1",
        alpha=0.9,
        label="Avg Billing"
    )
    ax5.set_title("Insurance: Patients & Avg Billing", fontweight="bold", fontsize=11)
    ax5.set_ylabel("Number of Patients", color="#2C3E50")
    ax5b.set_ylabel("Avg Billing (USD)", color="#2980B9")
    ax5.set_xticks(list(x5))
    ax5.set_xticklabels(
        df_insurance["insurance_provider"], rotation=20, ha="right", fontsize=8
    )
    p1 = mpatches.Patch(color=COLOURS["insurance"][0], label="Patients (left)")
    p2 = mpatches.Patch(color="#AED6F1", label="Avg Billing (right)")
    ax5.legend(handles=[p1, p2], fontsize=7.5, loc="upper right")
    ax5.grid(axis="y", alpha=0.2)

    # ── Chart 6: Patients by Age Group (bar) ─────────────────────────────────
    ax6 = fig.add_subplot(gs[0, 1])

    # Aggregate demographics by age group only
    age_summary = (
        df_demographics
        .groupby("age_group", as_index=False)
        .agg(patient_count=("patient_count", "sum"),
             avg_billing=("avg_billing", "mean"))
    )

    # Sort age groups in logical order
    age_order = ["Under 18", "18-35", "36-60", "Over 60"]
    age_summary["sort_key"] = pd.Categorical(
        age_summary["age_group"], categories=age_order, ordered=True
    )
    age_summary = age_summary.sort_values("sort_key").reset_index(drop=True)

    x6 = range(len(age_summary))

    # FIX: no offset — single set of bars should sit centred on tick positions
    bars6 = ax6.bar(
        list(x6),
        age_summary["patient_count"],
        width=0.6,
        color=COLOURS["age_groups"][: len(age_summary)],
    )
    ax6.set_title("Patients by Age Group", fontweight="bold", fontsize=11)
    ax6.set_ylabel("Number of Patients")
    ax6.set_xticks(list(x6))
    ax6.set_xticklabels(age_summary["age_group"], fontsize=9)

    for bar in bars6:
        h = bar.get_height()
        ax6.text(
            bar.get_x() + bar.get_width() / 2, h + age_summary["patient_count"].max() * 0.01,
            f"{int(h):,}", ha="center", fontsize=9, fontweight="bold"
        )
    ax6.grid(axis="y", alpha=0.3)

    # ── Chart 7: Most Prescribed Medications (horizontal bar) ─────────────────
    ax7 = fig.add_subplot(gs[1, 0])

    df_med_sorted = (
        df_medications
        .sort_values("prescription_count", ascending=True)
        .tail(6)
    )

    bars7 = ax7.barh(
        df_med_sorted["medication_name"],
        df_med_sorted["prescription_count"],
        color=COLOURS["medications"][: len(df_med_sorted)],
        height=0.6
    )
    ax7.set_title("Most Prescribed Medications", fontweight="bold", fontsize=11)
    ax7.set_xlabel("Number of Prescriptions")
    ax7.invert_yaxis()

    for bar in bars7:
        w = bar.get_width()
        ax7.text(
            w + df_med_sorted["prescription_count"].max() * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{int(w):,}", va="center", fontsize=9
        )
    ax7.set_xlim(0, df_med_sorted["prescription_count"].max() * 1.18)
    ax7.grid(axis="x", alpha=0.3)

    # ── Chart 8: Gender — Visits & Avg Billing (dual axis bar) ────────────────
    ax8  = fig.add_subplot(gs[1, 1])
    ax8b = ax8.twinx()

    x8    = range(len(df_gender))
    width8 = 0.35

    bars8 = ax8.bar(
        [i - width8 / 2 for i in x8],
        df_gender["total_visits"],
        width=width8,
        color=COLOURS["gender"],
        label="Total Visits"
    )
    ax8b.bar(
        [i + width8 / 2 for i in x8],
        df_gender["avg_billing"],
        width=width8,
        color="#AED6F1",
        alpha=0.9,
        label="Avg Billing"
    )
    ax8.set_title("Gender: Visits & Avg Billing", fontweight="bold", fontsize=11)
    ax8.set_ylabel("Total Visits", color="#2C3E50")
    ax8b.set_ylabel("Avg Billing (USD)", color="#2980B9")
    ax8.set_xticks(list(x8))
    ax8.set_xticklabels(df_gender["gender"], fontsize=10)

    for bar in bars8:
        h = bar.get_height()
        ax8.text(
            bar.get_x() + bar.get_width() / 2,
            h + df_gender["total_visits"].max() * 0.01,
            f"{int(h):,}", ha="center", fontsize=9, fontweight="bold"
        )

    p1 = mpatches.Patch(color=COLOURS["gender"][0], label="Visits (left)")
    p2 = mpatches.Patch(color="#AED6F1", label="Avg Billing (right)")
    ax8.legend(handles=[p1, p2], fontsize=7.5, loc="upper right")
    ax8.grid(axis="y", alpha=0.3)

    plt.savefig("charts/hospital_analysis_page2.png", dpi=150, bbox_inches="tight")
    print("  Page 2 saved: charts/hospital_analysis_page2.png")
    plt.show()


def make_page3(df_doctors, df_demographics, df_conditions, df_admission):
    """
    Page 3: Doctor Workload | Cost Per Visit | Condition Summary | Admission Summary

    Parameters:
        df_doctors    — from q6_doctors()
        df_demographics— from q7_demographics()
        df_conditions — from q2_conditions()
        df_admission  — from q5_admission_types()
    """
    fig = plt.figure(figsize=(16, 11))
    fig.suptitle(
        "Hospital Patient Analysis  —  Page 3 of 3\n"
        "Doctors  ·  Cost Per Visit  ·  Conditions  ·  Admission Summary",
        fontsize=13, fontweight="bold", y=0.98
    )
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.38)

    # ── Chart 9: Doctor Workload (horizontal bar) ──────────────────────────────
    ax9 = fig.add_subplot(gs[0, 0])

    df_doc_sorted = (
        df_doctors
        .sort_values("patients_handled", ascending=True)
        .tail(8)
    )

    bars9 = ax9.barh(
        df_doc_sorted["doctor_name"],
        df_doc_sorted["patients_handled"],
        color=COLOURS["doctors"][: min(len(df_doc_sorted), len(COLOURS["doctors"]))],
        height=0.6
    )
    ax9.set_title("Doctor Workload (Patients Handled)", fontweight="bold", fontsize=11)
    ax9.set_xlabel("Number of Patients")
    ax9.invert_yaxis()

    for bar in bars9:
        w = bar.get_width()
        ax9.text(
            w + df_doc_sorted["patients_handled"].max() * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{int(w):,}", va="center", fontsize=8
        )
    ax9.set_xlim(0, df_doc_sorted["patients_handled"].max() * 1.18)
    ax9.grid(axis="x", alpha=0.3)

    # ── Chart 10: Cost Per Visit by Condition (bar) ───────────────────────────
    ax10 = fig.add_subplot(gs[0, 1])

    df_cond_cost = df_conditions.sort_values("cost_per_visit", ascending=False).head(6)

    # FIX: set_xticks BEFORE set_xticklabels to ensure labels align to bars
    ax10.set_xticks(range(len(df_cond_cost)))
    bars10 = ax10.bar(
        range(len(df_cond_cost)),
        df_cond_cost["cost_per_visit"],
        color=COLOURS["conditions"][: len(df_cond_cost)],
        width=0.6
    )
    ax10.set_title("Cost Per Visit by Condition", fontweight="bold", fontsize=11)
    ax10.set_ylabel("Cost Per Visit (USD)")
    ax10.set_xticklabels(
        df_cond_cost["condition_name"], rotation=25, ha="right", fontsize=9
    )

    for bar in bars10:
        h = bar.get_height()
        ax10.text(
            bar.get_x() + bar.get_width() / 2,
            h + df_cond_cost["cost_per_visit"].max() * 0.02,
            f"${h:,.0f}", ha="center", fontsize=8, fontweight="bold"
        )
    ax10.set_ylim(0, df_cond_cost["cost_per_visit"].max() * 1.22)
    ax10.grid(axis="y", alpha=0.3)

    # ── Chart 11: Patients & Avg Stay by Condition (dual axis bar) ────────────
    ax11  = fig.add_subplot(gs[1, 0])
    ax11b = ax11.twinx()

    df_cond2 = df_conditions.sort_values("patient_count", ascending=False).head(6)
    x11   = range(len(df_cond2))
    w11   = 0.35

    bars11 = ax11.bar(
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
    ax11.set_title("Patients & Avg Stay by Condition", fontweight="bold", fontsize=11)
    ax11.set_ylabel("Number of Patients", color="#2C3E50")
    ax11b.set_ylabel("Avg Stay (days)", color="#7F8C8D")
    ax11.set_xticks(list(x11))
    ax11.set_xticklabels(
        df_cond2["condition_name"], rotation=25, ha="right", fontsize=8
    )

    for bar in bars11:
        h = bar.get_height()
        ax11.text(
            bar.get_x() + bar.get_width() / 2,
            h + df_cond2["patient_count"].max() * 0.01,
            f"{int(h):,}", ha="center", fontsize=8
        )

    p1 = mpatches.Patch(color=COLOURS["conditions"][0], label="Patients (left)")
    p2 = mpatches.Patch(color="#BDC3C7", label="Avg Stay days (right)")
    ax11.legend(handles=[p1, p2], fontsize=7.5, loc="upper left")
    ax11.grid(axis="y", alpha=0.2)

    # ── Chart 12: Admission Type — Visits & Avg Stay (dual axis bar) ──────────
    ax12  = fig.add_subplot(gs[1, 1])
    ax12b = ax12.twinx()

    x12  = range(len(df_admission))
    w12  = 0.35

    bars12 = ax12.bar(
        [i - w12 / 2 for i in x12],
        df_admission["visits"],
        width=w12,
        color=COLOURS["admission"],
        label="Visits"
    )
    ax12b.bar(
        [i + w12 / 2 for i in x12],
        df_admission["avg_stay"],
        width=w12,
        color="#AED6F1",
        alpha=0.9,
        label="Avg Stay"
    )
    ax12.set_title("Admission Type: Visits & Avg Stay", fontweight="bold", fontsize=11)
    ax12.set_ylabel("Number of Visits", color="#2C3E50")
    ax12b.set_ylabel("Avg Stay (days)", color="#2980B9")
    ax12.set_xticks(list(x12))
    ax12.set_xticklabels(df_admission["admission_type"], fontsize=10)

    for bar in bars12:
        h = bar.get_height()
        ax12.text(
            bar.get_x() + bar.get_width() / 2,
            h + df_admission["visits"].max() * 0.01,
            f"{int(h):,}", ha="center", fontsize=9, fontweight="bold"
        )

    p1 = mpatches.Patch(color=COLOURS["admission"][0], label="Visits (left)")
    p2 = mpatches.Patch(color="#AED6F1", label="Avg Stay (right)")
    ax12.legend(handles=[p1, p2], fontsize=7.5, loc="upper right")
    ax12b.legend(fontsize=7.5, loc="upper left")
    ax12.grid(axis="y", alpha=0.3)

    plt.savefig("charts/hospital_analysis_page3.png", dpi=150, bbox_inches="tight")
    print("  Page 3 saved: charts/hospital_analysis_page3.png")
    plt.show()


# =============================================================================
# SECTION 4 — TERMINAL SUMMARY REPORT
# =============================================================================

def print_summary(df1, df2, df4, df5, df6, df8, df9, df10):
    """
    Prints a readable text report of all key findings to the terminal.

    Parameters:
        df1  — monthly revenue    df2  — conditions
        df4  — insurance          df5  — admission types
        df6  — doctors            df8  — medications
        df9  — test results       df10 — gender
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

    print(f"\n{dline}\n")

def save_summary_to_file(df1, df2, df4, df5, df6, df8, df9, df10):
    """
    Generates a text-based Summary Report and saves it to a file 
    inside a 'reports/' directory.
    """
    # Create a reports directory if it doesn't exist
    os.makedirs("reports", exist_ok=True)
    report_filepath = "reports/hospital_analysis_summary.txt"

    # Define layout elements
    line   = "-" * 58
    dline  = "=" * 58

    total_revenue  = df1["total_revenue"].sum()
    total_patients = df1["total_patients"].sum()
    total_visits   = df10["total_visits"].sum()

    # Open the file in write ('w') mode using UTF-8 encoding for block arrows
    with open(report_filepath, "w", encoding="utf-8") as f:
        f.write(f"{dline}\n")
        f.write("  HOSPITAL ANALYSIS — SUMMARY REPORT\n")
        f.write("  Star Schema · imdb database · public schema\n")
        f.write(f"{dline}\n")
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

        f.write(f"\n{dline}\n")
        
    print(f"✅ Text summary report saved: {report_filepath}")
# =============================================================================
# SECTION 5 — MAIN ENTRY POINT
# =============================================================================

def run_full_analysis():
    """
    Runs all 10 queries, prints the terminal summary,
    and generates all three chart pages.
    """
    print("=" * 58)
    print("  HOSPITAL PATIENT ANALYSIS")
    print("  Database: imdb  |  Schema: public  |  Star Schema")
    print("=" * 58)
    print("\nRunning queries...\n")

    # ── Run all queries ───────────────────────────────────────────────────────
    df1  = q1_monthly_revenue()
    df2  = q2_conditions()
    #df3  = q3_hospitals()       # available but not used in charts (optional)
    df4  = q4_insurance()
    df5  = q5_admission_types()
    df6  = q6_doctors()
    df7  = q7_demographics()
    df8  = q8_medications()
    df9  = q9_test_results()
    df10 = q10_gender()

    # ── Guard: check fact table returned data ─────────────────────────────────
    if df1.empty:
        print("\nNo data returned from q1_monthly_revenue().")
        print("Check that public.fact_patient_visits exists and contains rows.")
        return

    # ── Terminal report ───────────────────────────────────────────────────────
    print_summary(df1, df2, df4, df5, df6, df8, df9, df10)
    
    # ── Save report to file ───────────────────────────────────────────────────
    os.makedirs("reports", exist_ok=True)
    report_path = "reports/hospital_analysis_summary.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("==========================================================\n")
        f.write("  HOSPITAL ANALYSIS — AUTOMATED SUMMARY REPORT\n")
        f.write("==========================================================\n")
        f.write(f"Total Patients Analyzed : {df1['total_patients'].sum():,}\n")
        f.write(f"Total Generated Revenue : ${df1['total_revenue'].sum():,.2f}\n")
        f.write("==========================================================\n")
    print(f"✅ Text summary report saved: {report_path}")

    # ── Charts ────────────────────────────────────────────────────────────────
    print("\nGenerating charts (3 pages)...\n")
    make_page1(df1, df2, df5, df9)
    make_page2(df4, df7, df8, df10)
    make_page3(df6, df7, df2, df5)

    print("\nAnalysis complete.")
    print("Charts saved in:charts/")
    print("  charts/hospital_analysis_page1.png")
    print("  charts/hospital_analysis_page2.png")
    print("  charts/hospital_analysis_page3.png")


if __name__ == "__main__":
    run_full_analysis()