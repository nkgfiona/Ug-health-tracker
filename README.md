🇺🇬 Uganda Health Tracker
A comprehensive health data analytics project that demonstrates the evolution of healthcare data management from basic data analysis to a scalable PostgreSQL data warehouse. The project showcases how raw healthcare data can be cleaned, analyzed, stored, and transformed into actionable insights for healthcare professionals and decision-makers.
________________________________________
📖 Project Overview
The Uganda Health Tracker was developed in two phases, with each phase building upon the previous one to demonstrate the progression from traditional data analysis to modern data warehousing.
•	Phase 0 focuses on cleaning, analyzing, and visualizing healthcare data using Python.
•	Phase 1 extends the project by introducing a PostgreSQL data warehouse designed using a Star Schema, enabling advanced SQL analytics, better performance, and scalable reporting.
Together, these phases demonstrate the complete journey of healthcare data—from raw records to analytical insights.
________________________________________
🎯 Project Objectives
The project aims to:
•	Clean and prepare healthcare datasets for analysis.
•	Generate statistical summaries and visual reports.
•	Store healthcare data in a relational PostgreSQL database.
•	Design and implement a Star Schema data warehouse.
•	Perform advanced SQL-based healthcare analytics.
•	Support data-driven decision making through reporting and visualization.
________________________________________
🚀 Project Phases
📊 Phase 0 – Data Analysis & Visualization
Phase 0 focuses on exploratory data analysis using Python. The project processes healthcare data stored in CSV or Excel files, performs data cleaning, computes descriptive statistics, and generates visual reports.
Key Features
•	Automated data cleaning
•	Missing value handling
•	Duplicate removal
•	Statistical analysis
•	Data visualization using charts
•	Automated report generation
Technologies Used
•	Python
•	Pandas
•	Matplotlib
•	Seaborn
•	OpenPyXL
Output
Phase 0 produces:
•	Statistical summaries
•	Missing values report
•	Charts and graphs
•	Cleaned datasets
To run Phase 0:
python main.py
________________________________________
🗄️ Phase 1 – Data Warehouse & Analytics
Phase 1 transforms the project into a relational data warehouse by migrating healthcare data into PostgreSQL using a Star Schema. This phase supports efficient querying, advanced analytics, and modular reporting.
Key Features
•	PostgreSQL database
•	Star Schema design
•	One fact table with ten dimension tables
•	SQL analytical queries
•	Geographic analysis
•	Modular reporting
•	Improved scalability and performance
Technologies Used
•	PostgreSQL
•	SQL
•	Python
•	SQLAlchemy
•	Pandas
•	Matplotlib
•	psycopg2
Output
Phase 1 generates:
•	SQL analytical reports
•	Revenue analysis
•	Disease trend analysis
•	Geographic insights
•	Hospital performance metrics
•	Visual dashboards and charts
To run Phase 1:
pip install -r requirements.txt
psql -d postgres -c "CREATE DATABASE imdb;"
psql -d imdb -f database/schema.sql
python config.py
python database_connection.py
python database/load2_data.py
python queries/analysis2_from_db.py
python reports/generate_report.py
python main2.py
Note: Replace imdb with your project database name if you have used a different name.
________________________________________
🔄 Progression from Phase 0 to Phase 1
Feature	Phase 0	Phase 1
Data Storage	CSV / Excel Files	PostgreSQL Database
Data Structure	Single Flat Dataset	Star Schema Data Warehouse
Data Processing	Python Scripts	SQL + Python
Analysis	Basic Statistics	Advanced SQL Analytics
Query Performance	File-Based Processing	Indexed Database Queries
Geographic Analysis	Not Available	District & Regional Analysis
Data Integrity	Limited	Referential Integrity
Reporting	Basic Reports	Modular Analytical Reports
Scalability	Limited	High
Charts	Basic Visualizations	Advanced Multi-page Reports
The transition from Phase 0 to Phase 1 demonstrates how healthcare analytics can evolve from standalone scripts into a scalable decision-support system capable of handling more complex analytical workloads.
________________________________________
📁 Repository Structure
uganda-health-tracker/
│
├── 01_phase0_data_analysis/
│   ├── main.py
│   ├── report/
│   ├── sample.xlsx
│   └── README.md
│
├── 02_phase1_health_database/
│   ├── database/
│   │   ├── schema.sql
│   │   └── load2_data.py
│   ├── queries/
│   │   └── analysis_queries.sql
│   ├── reports/
│   │   ├── generate_report.py
│   │   └── charts/
│   ├── main2.py
│   ├── database_connection.py
│   ├── config.py
│   ├── requirements.txt
│   ├── erd_diagram.png
│   └── README.md
│
├── .gitignore
└── README.md
________________________________________
📈 Analytical Capabilities
Across both phases, the Uganda Health Tracker can answer questions such as:
Patient Analysis
•	What is the age and gender distribution of patients?
•	Which districts have the highest patient populations?
•	How do patient visits change over time?
Clinical Analysis
•	Which medical conditions are most common?
•	Which diseases require the highest treatment costs?
•	Which doctors manage the highest patient volumes?
Financial Analysis
•	What is the monthly revenue trend?
•	Which insurance providers contribute the highest revenue?
•	What is the average billing amount per patient?
Geographic Analysis
•	Which districts have the highest disease burden?
•	Which regions require additional healthcare resources?
•	How are healthcare services distributed geographically?
________________________________________
🛠️ Requirements
Phase 0
pip install pandas matplotlib seaborn openpyxl
Phase 1
pip install -r requirements.txt
________________________________________
🧪 Testing
To verify the project setup:
Phase 0
python main.py
________________________________________
🚀 Future Development
Future versions of the Uganda Health Tracker may include:
•	Interactive Streamlit dashboards
•	Automated ETL pipelines
•	Real-time healthcare data streaming
•	Machine learning for disease prediction
•	User authentication and role-based access
•	Cloud database deployment
________________________________________
🤝 Contributing
Contributions are welcome. If you would like to improve the project, feel free to fork the repository, create a feature branch, and submit a pull request.
________________________________________
📄 License
This project is open-source and is intended for educational purposes. You are free to modify and extend it for your own healthcare analytics projects.
________________________________________
👩‍💻 Author
Nakabugo K Fiona
•	GitHub: nkgfiona
•	Email: jclovefiona@gmail.com
________________________________________
Acknowledgements
This project was developed using:
•	PostgreSQL
•	Python
•	Pandas
•	Matplotlib
•	SQLAlchemy
Special appreciation goes to the Uganda Ministry of Health for inspiring the healthcare use case used throughout this project.

