# analysis_from_db.py
# ─────────────────────────────────────────────────────────────────────────────
# Full hospital patient analysis — all queries run from PostgreSQL via Python.
# Results are printed to the terminal and saved as charts.
# ─────────────────────────────────────────────────────────────────────────────

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from database_connection import run_query


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1 — QUERIES
# Each function runs one SQL query and returns a pandas DataFrame.
# ═════════════════════════════════════════════════════════════════════════════

def q1_condition_summary():
    """
    How many patients have each medical condition?
    What is the average age and average billing amount per condition?
    """
    sql = """
        SELECT
            medical_condition,
            COUNT(*)                                    AS total_patients,
            ROUND(AVG(age)::numeric, 1)                 AS avg_age,
            ROUND(AVG(billing_amount)::numeric, 2)      AS avg_billing_usd,
            ROUND(AVG(length_of_stay)::numeric, 1)      AS avg_stay_days
        FROM public.hospital_patients
        GROUP BY medical_condition
        ORDER BY total_patients DESC;
    """
    print("\n[Query 1] Patient count and averages by medical condition...")
    return run_query(sql)


def q2_admission_type_billing():
    """
    How does billing amount and length of stay differ
    between Urgent, Emergency, and Elective admissions?
    """
    sql = """
        SELECT
            admission_type,
            COUNT(*)                                    AS total_patients,
            ROUND(AVG(billing_amount)::numeric, 2)      AS avg_billing_usd,
            ROUND(MIN(billing_amount)::numeric, 2)      AS min_billing_usd,
            ROUND(MAX(billing_amount)::numeric, 2)      AS max_billing_usd,
            ROUND(AVG(length_of_stay)::numeric, 1)      AS avg_stay_days
        FROM public.hospital_patients
        GROUP BY admission_type
        ORDER BY avg_billing_usd DESC;
    """
    print("\n[Query 2] Billing and stay duration by admission type...")
    return run_query(sql)


def q3_age_group_analysis():
    """
    Break patients into age groups.
    Show patient count, most common condition, and average billing per group.
    """
    sql = """
        SELECT
            age_group,
            COUNT(*)                                    AS total_patients,
            ROUND(AVG(billing_amount)::numeric, 2)      AS avg_billing_usd,
            ROUND(AVG(length_of_stay)::numeric, 1)      AS avg_stay_days
        FROM public.hospital_patients
        WHERE age_group IS NOT NULL
        GROUP BY age_group
        ORDER BY
            CASE age_group
                WHEN 'Under 18' THEN 1
                WHEN '18-35'    THEN 2
                WHEN '36-60'    THEN 3
                WHEN 'Over 60'  THEN 4
            END;
    """
    print("\n[Query 3] Patient breakdown by age group...")
    return run_query(sql)


def q4_test_results_by_condition():
    """
    For each medical condition, what percentage of patients
    had Normal, Inconclusive, or Abnormal test results?
    """
    sql = """
        SELECT
            medical_condition,
            test_results,
            COUNT(*)                                        AS patient_count,
            ROUND(
                100.0 * COUNT(*) /
                SUM(COUNT(*)) OVER (PARTITION BY medical_condition),
                1
            )                                               AS pct_of_condition
        FROM public.hospital_patients
        GROUP BY medical_condition, test_results
        ORDER BY medical_condition, test_results;
    """
    print("\n[Query 4] Test results breakdown by medical condition...")
    return run_query(sql)


def q5_gender_condition():
    """
    How is each medical condition distributed between Male and Female patients?
    """
    sql = """
        SELECT
            medical_condition,
            gender,
            COUNT(*)                                    AS patient_count,
            ROUND(AVG(billing_amount)::numeric, 2)      AS avg_billing_usd
        FROM public.hospital_patients
        GROUP BY medical_condition, gender
        ORDER BY medical_condition, gender;
    """
    print("\n[Query 5] Patient count and billing by condition and gender...")
    return run_query(sql)


def q6_top_medications():
    """
    Which medications are most prescribed?
    What is the average billing for each medication?
    """
    sql = """
        SELECT
            medication,
            COUNT(*)                                    AS times_prescribed,
            ROUND(AVG(billing_amount)::numeric, 2)      AS avg_billing_usd,
            ROUND(AVG(length_of_stay)::numeric, 1)      AS avg_stay_days
        FROM public.hospital_patients
        GROUP BY medication
        ORDER BY times_prescribed DESC;
    """
    print("\n[Query 6] Medication prescription frequency and average billing...")
    return run_query(sql)


def q7_insurance_billing():
    """
    Which insurance providers cover the most patients?
    What is the average billing amount per provider?
    """
    sql = """
        SELECT
            insurance_provider,
            COUNT(*)                                    AS total_patients,
            ROUND(AVG(billing_amount)::numeric, 2)      AS avg_billing_usd,
            ROUND(SUM(billing_amount)::numeric, 2)      AS total_billed_usd
        FROM public.hospital_patients
        GROUP BY insurance_provider
        ORDER BY total_patients DESC;
    """
    print("\n[Query 7] Patient count and billing by insurance provider...")
    return run_query(sql)


def q8_high_cost_patients():
    """
    How many patients had billing above the overall average?
    What are their most common conditions and admission types?
    """
    sql = """
        SELECT
            medical_condition,
            admission_type,
            COUNT(*)                                    AS high_cost_count,
            ROUND(AVG(billing_amount)::numeric, 2)      AS avg_billing_usd
        FROM public.hospital_patients
        WHERE billing_amount > (
            SELECT AVG(billing_amount) FROM public.hospital_patients
        )
        GROUP BY medical_condition, admission_type
        ORDER BY high_cost_count DESC
        LIMIT 10;
    """
    print("\n[Query 8] High-cost patients: conditions and admission types...")
    return run_query(sql)


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2 — CHARTS
# Two separate chart pages, each with 4 charts.
# ═════════════════════════════════════════════════════════════════════════════

# Colour palette — consistent across all charts
COLOURS = {
    "conditions":   ["#2C3E50","#E74C3C","#3498DB","#27AE60","#F39C12","#9B59B6"],
    "admission":    ["#E74C3C","#F39C12","#27AE60"],
    "age_groups":   ["#3498DB","#2ECC71","#E67E22","#9B59B6"],
    "test_normal":  "#27AE60",
    "test_inconc":  "#F39C12",
    "test_abnorm":  "#E74C3C",
    "male":         "#2980B9",
    "female":       "#C0392B",
    "medications":  ["#1ABC9C","#3498DB","#9B59B6","#E67E22","#E74C3C"],
    "insurance":    ["#2C3E50","#2980B9","#27AE60","#E67E22","#8E44AD"],
}


def make_page1(df1, df2, df3, df4):
    """
    Chart Page 1 — Overview: Conditions, Admission, Age, Test Results
    """
    fig = plt.figure(figsize=(16, 11))
    fig.suptitle(
        "Hospital Patient Analysis  —  Page 1 of 2\n"
        "Conditions · Admissions · Age Groups · Test Results",
        fontsize=13, fontweight="bold", y=0.98
    )
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.42, wspace=0.35)

    # ── Chart 1: Patients per medical condition (horizontal bar) ─────────────
    ax1 = fig.add_subplot(gs[0, 0])
    bars = ax1.barh(
        df1["medical_condition"],
        df1["total_patients"],
        color=COLOURS["conditions"],
        height=0.6
    )
    ax1.set_title("Patients by Medical Condition", fontweight="bold", fontsize=11)
    ax1.set_xlabel("Number of Patients")
    ax1.invert_yaxis()
    for bar in bars:
        w = bar.get_width()
        ax1.text(w + 1, bar.get_y() + bar.get_height()/2,
                 f"{int(w):,}", va="center", fontsize=9)
    ax1.set_xlim(0, df1["total_patients"].max() * 1.18)
    ax1.grid(axis="x", alpha=0.3)

    # ── Chart 2: Average billing by admission type (bar) ─────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    bars2 = ax2.bar(
        df2["admission_type"],
        df2["avg_billing_usd"],
        color=COLOURS["admission"],
        width=0.5
    )
    ax2.set_title("Average Billing by Admission Type", fontweight="bold", fontsize=11)
    ax2.set_ylabel("Average Billing (USD)")
    ax2.set_ylim(0, df2["avg_billing_usd"].max() * 1.2)
    for bar in bars2:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, h + 200,
                 f"${h:,.0f}", ha="center", fontsize=9, fontweight="bold")
    # Add average stay days as a secondary annotation
    for i, (_, row) in enumerate(df2.iterrows()):
        ax2.text(i, 500, f"Avg stay:\n{row['avg_stay_days']} days",
                 ha="center", fontsize=8, color="white", fontweight="bold")
    ax2.grid(axis="y", alpha=0.3)

    # ── Chart 3: Patients and avg billing by age group (grouped) ─────────────
    ax3 = fig.add_subplot(gs[1, 0])
    x     = range(len(df3))
    width = 0.4
    bars3a = ax3.bar(
        [i - width/2 for i in x],
        df3["total_patients"],
        width=width,
        color=COLOURS["age_groups"],
        label="Patients"
    )
    ax3.set_title("Patients & Avg Stay by Age Group", fontweight="bold", fontsize=11)
    ax3.set_ylabel("Number of Patients", color="#2C3E50")
    ax3.set_xticks(list(x))
    ax3.set_xticklabels(df3["age_group"], fontsize=9)

    # Second y-axis for avg stay days
    ax3b = ax3.twinx()
    ax3b.bar(
        [i + width/2 for i in x],
        df3["avg_stay_days"],
        width=width,
        color="#BDC3C7",
        alpha=0.85,
        label="Avg Stay (days)"
    )
    ax3b.set_ylabel("Avg Length of Stay (days)", color="#7F8C8D")

    for bar in bars3a:
        ax3.text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + 2,
                 f"{int(bar.get_height()):,}",
                 ha="center", fontsize=8)

    legend1 = mpatches.Patch(color=COLOURS["age_groups"][0], label="Patients (left axis)")
    legend2 = mpatches.Patch(color="#BDC3C7", label="Avg stay days (right axis)")
    ax3.legend(handles=[legend1, legend2], fontsize=7, loc="upper left")
    ax3.grid(axis="y", alpha=0.2)

    # ── Chart 4: Test results by condition (stacked percentage bar) ───────────
    ax4 = fig.add_subplot(gs[1, 1])
    pivot = df4.pivot(
        index="medical_condition",
        columns="test_results",
        values="pct_of_condition"
    ).fillna(0)

    # Ensure consistent column order
    for col in ["Normal", "Inconclusive", "Abnormal"]:
        if col not in pivot.columns:
            pivot[col] = 0

    pivot = pivot[["Normal", "Inconclusive", "Abnormal"]]
    conditions = pivot.index.tolist()
    normals     = pivot["Normal"].values
    inconcs     = pivot["Inconclusive"].values
    abnormals   = pivot["Abnormal"].values

    ax4.barh(conditions, normals,
             color=COLOURS["test_normal"], label="Normal", height=0.55)
    ax4.barh(conditions, inconcs,
             left=normals,
             color=COLOURS["test_inconc"], label="Inconclusive", height=0.55)
    ax4.barh(conditions, abnormals,
             left=normals + inconcs,
             color=COLOURS["test_abnorm"], label="Abnormal", height=0.55)

    ax4.set_title("Test Results by Condition (%)", fontweight="bold", fontsize=11)
    ax4.set_xlabel("Percentage of Patients (%)")
    ax4.set_xlim(0, 110)
    ax4.legend(fontsize=8, loc="lower right")
    ax4.grid(axis="x", alpha=0.3)
    # Label each segment
    for i, (n, ic, ab) in enumerate(zip(normals, inconcs, abnormals)):
        if n > 5:
            ax4.text(n/2, i, f"{n:.0f}%", ha="center", va="center",
                     fontsize=7, color="white", fontweight="bold")
        if ic > 5:
            ax4.text(n + ic/2, i, f"{ic:.0f}%", ha="center", va="center",
                     fontsize=7, color="white", fontweight="bold")
        if ab > 5:
            ax4.text(n + ic + ab/2, i, f"{ab:.0f}%", ha="center", va="center",
                     fontsize=7, color="white", fontweight="bold")

    os.makedirs("charts", exist_ok=True)
    plt.savefig("charts/hospital_analysis_page1.png", dpi=150, bbox_inches="tight")
    print("\n✅ Page 1 saved → charts/hospital_analysis_page1.png")
    plt.show()


def make_page2(df5, df6, df7, df8):
    """
    Chart Page 2 — Detail: Gender, Medications, Insurance, High-Cost
    """
    fig = plt.figure(figsize=(16, 11))
    fig.suptitle(
        "Hospital Patient Analysis  —  Page 2 of 2\n"
        "Gender Split · Medications · Insurance · High-Cost Patients",
        fontsize=13, fontweight="bold", y=0.98
    )
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.38)

    # ── Chart 5: Patient count by condition and gender (grouped bar) ──────────
    ax5 = fig.add_subplot(gs[0, 0])
    conditions = df5["medical_condition"].unique()
    males      = df5[df5["gender"] == "Male"].set_index("medical_condition")["patient_count"]
    females    = df5[df5["gender"] == "Female"].set_index("medical_condition")["patient_count"]

    x     = range(len(conditions))
    width = 0.38
    ax5.bar([i - width/2 for i in x],
            [males.get(c, 0) for c in conditions],
            width=width, color=COLOURS["male"], label="Male")
    ax5.bar([i + width/2 for i in x],
            [females.get(c, 0) for c in conditions],
            width=width, color=COLOURS["female"], label="Female")

    ax5.set_title("Patients by Condition and Gender", fontweight="bold", fontsize=11)
    ax5.set_ylabel("Number of Patients")
    ax5.set_xticks(list(x))
    ax5.set_xticklabels(conditions, rotation=25, ha="right", fontsize=8)
    ax5.legend(fontsize=9)
    ax5.grid(axis="y", alpha=0.3)

    # ── Chart 6: Medication prescription frequency (pie) ──────────────────────
    ax6 = fig.add_subplot(gs[0, 1])
    wedges, texts, autotexts = ax6.pie(
        df6["times_prescribed"],
        labels=df6["medication"],
        colors=COLOURS["medications"],
        autopct="%1.1f%%",
        startangle=140,
        pctdistance=0.78,
        wedgeprops={"edgecolor":"white", "linewidth":1.5}
    )
    for at in autotexts:
        at.set_fontsize(9)
        at.set_color("white")
        at.set_fontweight("bold")
    for t in texts:
        t.set_fontsize(9)
    ax6.set_title("Medication Prescription Share", fontweight="bold", fontsize=11)
    # Add avg billing as a legend note
    legend_labels = [
        f"{row['medication']}  (avg ${row['avg_billing_usd']:,.0f})"
        for _, row in df6.iterrows()
    ]
    ax6.legend(legend_labels, loc="lower center",
               bbox_to_anchor=(0.5, -0.18), fontsize=7.5, ncol=2)

    # ── Chart 7: Insurance provider — patients and total billed ───────────────
    ax7  = fig.add_subplot(gs[1, 0])
    ax7b = ax7.twinx()

    x7     = range(len(df7))
    width7 = 0.38
    ax7.bar(
        [i - width7/2 for i in x7],
        df7["total_patients"],
        width=width7,
        color=COLOURS["insurance"],
        label="Patients"
    )
    ax7b.bar(
        [i + width7/2 for i in x7],
        df7["avg_billing_usd"],
        width=width7,
        color="#AED6F1",
        alpha=0.9,
        label="Avg Billing (USD)"
    )
    ax7.set_title("Insurance Provider: Patients & Avg Billing",
                  fontweight="bold", fontsize=11)
    ax7.set_ylabel("Number of Patients", color="#2C3E50")
    ax7b.set_ylabel("Avg Billing (USD)", color="#2980B9")
    ax7.set_xticks(list(x7))
    ax7.set_xticklabels(df7["insurance_provider"], rotation=20, ha="right", fontsize=8)

    p1 = mpatches.Patch(color=COLOURS["insurance"][0], label="Patients (left)")
    p2 = mpatches.Patch(color="#AED6F1", label="Avg billing (right)")
    ax7.legend(handles=[p1, p2], fontsize=7.5, loc="upper right")
    ax7.grid(axis="y", alpha=0.2)

    # ── Chart 8: High-cost patients — heatmap-style count grid ───────────────
    ax8 = fig.add_subplot(gs[1, 1])
    pivot8 = df8.pivot_table(
        index="medical_condition",
        columns="admission_type",
        values="high_cost_count",
        aggfunc="sum",
        fill_value=0
    )
    # Ensure all three admission types present
    for col in ["Urgent", "Emergency", "Elective"]:
        if col not in pivot8.columns:
            pivot8[col] = 0
    pivot8 = pivot8[["Urgent", "Emergency", "Elective"]]

    im = ax8.imshow(pivot8.values, cmap="YlOrRd", aspect="auto")
    ax8.set_xticks(range(len(pivot8.columns)))
    ax8.set_yticks(range(len(pivot8.index)))
    ax8.set_xticklabels(pivot8.columns, fontsize=10)
    ax8.set_yticklabels(pivot8.index, fontsize=9)
    ax8.set_title("High-Cost Patients\n(Above Average Billing)",
                  fontweight="bold", fontsize=11)

    # Annotate each cell
    for row_i in range(pivot8.shape[0]):
        for col_j in range(pivot8.shape[1]):
            val = pivot8.values[row_i, col_j]
            colour = "white" if val > pivot8.values.max() * 0.6 else "black"
            ax8.text(col_j, row_i, str(int(val)),
                     ha="center", va="center",
                     fontsize=10, fontweight="bold", color=colour)

    plt.colorbar(im, ax=ax8, shrink=0.75, label="Patient Count")
    ax8.set_xlabel("Admission Type")

    plt.savefig("charts/hospital_analysis_page2.png", dpi=150, bbox_inches="tight")
    print("✅ Page 2 saved → charts/hospital_analysis_page2.png")
    plt.show()


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3 — TERMINAL SUMMARY REPORT
# Prints a clean readable report of all key findings.
# ═════════════════════════════════════════════════════════════════════════════

def print_summary(df1, df2, df3, df6, df7):
    line = "─" * 56

    print(f"\n{'═'*56}")
    print("  HOSPITAL PATIENT ANALYSIS — SUMMARY REPORT")
    print("Data source: PostgreSQL → public.hospital_patients")
    print(f"{'═'*56}")

    total = df1["total_patients"].sum()
    print(f"\n  Total patients in database : {total:,}")

    print(f"\n{line}")
    print("  PATIENTS BY MEDICAL CONDITION")
    print(line)
    for _, row in df1.iterrows():
        pct = 100 * row["total_patients"] / total
        bar = "█" * int(pct / 2)
        print(f"  {row['medical_condition']:<14} {int(row['total_patients']):>4} pts "
              f"({pct:4.1f}%)  {bar}")
        print(f"  {'':14}  Avg age: {row['avg_age']} yrs  "
              f"Avg billing: ${row['avg_billing_usd']:,.2f}  "
              f"Avg stay: {row['avg_stay_days']} days")

    print(f"\n{line}")
    print("  BILLING BY ADMISSION TYPE")
    print(line)
    for _, row in df2.iterrows():
        print(f"  {row['admission_type']:<12}  "
              f"Avg: ${row['avg_billing_usd']:>10,.2f}  "
              f"Range: ${row['min_billing_usd']:,.0f} – ${row['max_billing_usd']:,.0f}  "
              f"Avg stay: {row['avg_stay_days']} days")

    print(f"\n{line}")
    print("  PATIENTS BY AGE GROUP")
    print(line)
    for _, row in df3.iterrows():
        print(f"  {row['age_group']:<12}  "
              f"{int(row['total_patients']):>4} patients  "
              f"Avg billing: ${row['avg_billing_usd']:,.2f}  "
              f"Avg stay: {row['avg_stay_days']} days")

    print(f"\n{line}")
    print("  TOP MEDICATIONS")
    print(line)
    for _, row in df6.iterrows():
        print(f"  {row['medication']:<14}  "
              f"Prescribed: {int(row['times_prescribed']):>4}x  "
              f"Avg billing: ${row['avg_billing_usd']:,.2f}  "
              f"Avg stay: {row['avg_stay_days']} days")

    print(f"\n{line}")
    print("  INSURANCE PROVIDERS")
    print(line)
    for _, row in df7.iterrows():
        print(f"  {row['insurance_provider']:<18}  "
              f"{int(row['total_patients']):>4} patients  "
              f"Avg: ${row['avg_billing_usd']:,.2f}  "
              f"Total billed: ${row['total_billed_usd']:,.0f}")

    print(f"\n{'═'*56}\n")


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 4 — MAIN ENTRY POINT
# ═════════════════════════════════════════════════════════════════════════════

def run_full_analysis():
    """
    Runs all 8 queries, prints the summary report,
    and generates both chart pages.
    """
    print("═" * 56)
    print("  RUNNING HOSPITAL PATIENT ANALYSIS")
    print("  Queries executed against PostgreSQL database")
    print("═" * 56)

    # Run all queries
    df1 = q1_condition_summary()
    df2 = q2_admission_type_billing()
    df3 = q3_age_group_analysis()
    df4 = q4_test_results_by_condition()
    df5 = q5_gender_condition()
    df6 = q6_top_medications()
    df7 = q7_insurance_billing()
    df8 = q8_high_cost_patients()

    # Check at least one query returned data
    if df1.empty:
        print("\n❌ No data returned. Make sure you have run load_data.py first.")
        print("   Expected table: public.hospital_patients in health_db")
        return

    # Print terminal summary
    print_summary(df1, df2, df3, df6, df7)

    # Build charts
    print("Generating charts — two pages will open in sequence...\n")
    make_page1(df1, df2, df3, df4)
    make_page2(df5, df6, df7, df8)

    print("\n✅ Full analysis complete.")
    print("   Charts saved in: charts/")
    print("   • charts/hospital_analysis_page1.png")
    print("   • charts/hospital_analysis_page2.png")


if __name__ == "__main__":
    run_full_analysis()
