# main.py
# Main entry point for the health data project
# Now works with hospital_patients analysis

from analysis_from_db import run_full_analysis

def main():
    print("=" * 50)
    print("  UGANDA HEALTH DATA ANALYSER")
    print("  Data source: PostgreSQL (health_db)")
    print("=" * 50)
    
    # Run the full analysis (queries + charts + summary)
    run_full_analysis()
    
    print("\n✅ Analysis complete.")

if __name__ == "__main__":
    main()