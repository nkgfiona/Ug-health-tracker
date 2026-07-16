# main2.py
# Main entry point for the health data project
# Now works with hospital_patients analysis

from analysis2_from_db import run_full_analysis

def main():
    print("=" * 50)
    print("  STAR SCHEMA HOSPITAL PATIENTS ANALYSER")
    print("  Data source: PostgreSQL (imdb)")
    print("=" * 50)
    
    # Run the full analysis (queries + charts + summary)
    run_full_analysis()
    
    print("\n✅ Analysis complete.")

if __name__ == "__main__":
    main()