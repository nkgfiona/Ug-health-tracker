# generate_report.py
# Generates analysis report with charts from the database
# Uses the existing analysis2_from_db.py functions

import os
import sys
#import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Add parent directory to path to import existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import existing functions from analysis2_from_db.py
from analysis2_from_db import (
    q1_monthly_revenue, q2_conditions, q4_insurance,
    q6_doctors, q5_admission_types
)
#from database_connection import run_query


def create_charts(df1, df2, df3):
    """
    Create 3 charts from the query results
    
    Arguments:
        df1: Monthly revenue data
        df2: Conditions data
        df3: Insurance data
    """
    
    # Create charts directory
    os.makedirs('charts', exist_ok=True)
    
    # ── Chart 1: Monthly Revenue Trend ──────────────────────────────────────
    plt.figure(figsize=(12, 6))
    
    # Create date labels safely
    df1['date_label'] = df1['year'].astype(str) + '-' + df1['month_name'].str[:3]
    
    plt.plot(df1['date_label'], df1['total_revenue'], 
             marker='o', linewidth=2.5, markersize=8, color='#2C3E50')
    plt.title('Monthly Revenue Trend', fontsize=14, fontweight='bold')
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Total Revenue (USD)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels safely using positional enumeration (avoids index mismatch crashes)
    max_rev = max(df1['total_revenue'].max(), 1)
    for idx, (_, row) in enumerate(df1.iterrows()):
        plt.text(idx, row['total_revenue'] + max_rev * 0.02,
                 f"${row['total_revenue']:,.0f}", 
                 ha='center', fontsize=8, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('charts/chart1_monthly_revenue.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ Chart 1 saved: charts/chart1_monthly_revenue.png")
    
    # ── Chart 2: Top Conditions by Cost ──────────────────────────────────────
    plt.figure(figsize=(12, 6))
    
    # Sort and get top 6
    df2_sorted = df2.sort_values('total_cost', ascending=True).tail(6)
    
    bars = plt.barh(df2_sorted['condition_name'], df2_sorted['total_cost'],
                    color=['#2C3E50', '#E74C3C', '#3498DB', '#27AE60', '#F39C12', '#9B59B6'][:len(df2_sorted)])
    plt.title('Top Medical Conditions by Total Cost', fontsize=14, fontweight='bold')
    plt.xlabel('Total Cost (USD)', fontsize=12)
    plt.ylabel('Medical Condition', fontsize=12)
    plt.gca().invert_yaxis()
    
    # Add value labels safely
    max_cost = max(df2_sorted['total_cost'].max(), 1)
    for bar in bars:
        w = bar.get_width()
        plt.text(w + max_cost * 0.01,
                 bar.get_y() + bar.get_height()/2,
                 f"${w:,.0f}", va='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('charts/chart2_conditions_by_cost.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ Chart 2 saved: charts/chart2_conditions_by_cost.png")
    
    # ── Chart 3: Insurance Provider Analysis ──────────────────────────────────
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()
    
    x = range(len(df3))
    width = 0.35
    
    bars1 = ax1.bar([i - width/2 for i in x], df3['patients'], width,
                    color='#2C3E50', label='Patients', alpha=0.8)
    #bars2 = ax2.bar([i + width/2 for i in x], df3['avg_bill'], width,
    #                color='#3498DB', label='Avg Billing', alpha=0.8)
    
    ax1.set_xlabel('Insurance Provider', fontsize=12)
    ax1.set_ylabel('Number of Patients', color='#2C3E50', fontsize=12)
    ax2.set_ylabel('Avg Billing (USD)', color='#3498DB', fontsize=12)
    ax1.set_title('Insurance Provider: Patients & Avg Billing', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(df3['insurance_provider'], rotation=15, ha='right')
    
    # Add value labels on bars safely
    max_patients = max(df3['patients'].max(), 1)
    for bar in bars1:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, h + max_patients * 0.02,
                 f"{int(h)}", ha='center', fontsize=8, fontweight='bold')
    
    # Combine legend items to prevent overlap issues
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    ax1.grid(axis='y', alpha=0.2, linestyle='--')
    
    plt.tight_layout()
    plt.savefig('charts/chart3_insurance_analysis.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ Chart 3 saved: charts/chart3_insurance_analysis.png")


def print_summary(df1, df2, df3, df4, df5):
    """Print a summary of key statistics"""
    
    print("\n" + "=" * 60)
    print("📊 HOSPITAL ANALYSIS - KEY STATISTICS")
    print("=" * 60)
    
    # Overall metrics calculated safely (weighted averages prevent skewed stats)
    total_patients = df1['total_patients'].sum() if 'total_patients' in df1.columns else 0
    total_revenue = df1['total_revenue'].sum() if 'total_revenue' in df1.columns else 0
    
    if total_patients > 0:
        avg_billing = (df1['avg_billing'] * df1['total_patients']).sum() / total_patients
        avg_stay = (df1['avg_stay_days'] * df1['total_patients']).sum() / total_patients
    else:
        avg_billing = df1['avg_billing'].mean() if not df1.empty else 0
        avg_stay = df1['avg_stay_days'].mean() if not df1.empty else 0
    
    print("\n📈 OVERALL METRICS")
    print("-" * 40)
    print(f"   Total Patients         : {total_patients:,}")
    print(f"   Total Revenue          : ${total_revenue:,.2f}")
    print(f"   Average Billing        : ${avg_billing:,.2f}")
    print(f"   Average Length of Stay: {avg_stay:.1f} days")
    
    # Top condition (Explicitly sorted in Python to guarantee accuracy)
    if not df2.empty:
        df2_sorted = df2.sort_values('total_cost', ascending=False)
        top_condition = df2_sorted.iloc[0]
        print("\n🏥 TOP MEDICAL CONDITION")
        print("-" * 40)
        print(f"   Condition              : {top_condition['condition_name']}")
        print(f"   Total Cost             : ${top_condition['total_cost']:,.2f}")
        print(f"   Patient Count          : {top_condition['patient_count']:,}")
    
    # Top insurance (Explicitly sorted in Python)
    if not df3.empty:
        df3_sorted = df3.sort_values('total_bill', ascending=False)
        top_insurance = df3_sorted.iloc[0]
        print("\n🏦 TOP INSURANCE PROVIDER")
        print("-" * 40)
        print(f"   Provider               : {top_insurance['insurance_provider']}")
        print(f"   Total Bill             : ${top_insurance['total_bill']:,.2f}")
        print(f"   Patients               : {top_insurance['patients']:,}")
    
    # Top doctor (Explicitly sorted in Python)
    if not df4.empty:
        df4_sorted = df4.sort_values('total_revenue', ascending=False)
        top_doctor = df4_sorted.iloc[0]
        print("\n👨‍⚕️ TOP DOCTOR")
        print("-" * 40)
        print(f"   Doctor                 : {top_doctor['doctor_name']}")
        print(f"   Patients Handled       : {top_doctor['patients_handled']:,}")
        print(f"   Total Revenue          : ${top_doctor['total_revenue']:,.2f}")
    
    # Admission type summary
    if not df5.empty:
        print("\n🏥 ADMISSION TYPE SUMMARY")
        print("-" * 40)
        for _, row in df5.iterrows():
            print(f"   {row['admission_type']:<12} "
                  f"{row['visits']:>4} visits  "
                  f"${row['avg_cost']:>10,.2f} avg  "
                  f"{row['avg_stay']:>4} days avg")


def main():
    """Main execution function"""
    
    print("=" * 60)
    print("📊 HEALTH DATABASE - REPORT GENERATOR")
    print("=" * 60)
    print(f"📅 Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Run queries using existing functions
    print("\n📊 Running analysis queries...")
    
    df1 = q1_monthly_revenue()
    df2 = q2_conditions()
    df3 = q4_insurance()
    df4 = q6_doctors()
    df5 = q5_admission_types()
    
    # Check if data exists
    if df1.empty:
        print("\n❌ No data found in the database.")
        print("   Please run load2_data.py first to load the sample data.")
        return
    
    # Create charts
    print("\n📊 Creating charts...")
    create_charts(df1, df2, df3)
    
    # Print summary
    print_summary(df1, df2, df3, df4, df5)
    
    # Final message
    print("\n" + "=" * 60)
    print(f"✅ Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📁 Charts saved in: charts/")
    print("   • chart1_monthly_revenue.png")
    print("   • chart2_conditions_by_cost.png")
    print("   • chart3_insurance_analysis.png")
    print("=" * 60)


if __name__ == "__main__":
    main()