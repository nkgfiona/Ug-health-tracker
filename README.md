Uganda Health Tracker: Data Analysis Tool
The Uganda Health Tracker is a Python-based automation tool designed to clean, analyze, and visualize healthcare data. Whether you provide an Excel or CSV file, this program processes the raw data, generates statistical summaries, and exports visual reports into an organized directory.
🚀 Key Features
Automated Data Cleaning: Removes duplicates, handles missing values (imputation), and standardizes column formats.
Statistical Analysis: Calculates mean, median, standard deviation, and range for all numerical metrics.
Visual Insights: Automatically generates and saves:
Bar Charts: Average age categorized by gender.
Line Charts: Trend analysis of records over time.
Scatter Plots: Correlation between age and total recruits.
Report Exporting: All findings and charts are saved to a dedicated report/ folder for easy sharing.
🛠️ Requirements
Before running the program, ensure you have Python installed along with the following libraries:
Bash
pip install pandas seaborn matplotlib openpyxl
pandas: For data manipulation.
seaborn & matplotlib: For generating high-quality charts.
openpyxl: Required for reading .xlsx files.
📂 Project Structure
main.py: The core script containing the DataAnalyzer class.
report/: (Generated automatically) Contains your visual charts and missing value reports.
sample.xlsx: Your input data file.
⚙️ How to Use
Prepare your data: Ensure your file is in .csv or .xlsx format.
Update the path: Open the script and update the file_path variable in the if name == "main": section to point to your specific file:
Python
file_path = r"C:\path\to\your\data.xlsx"
Run the program:
Bash
python main.py
Check the Results:
View the Terminal for a text-based summary and top insights.
Open the report/ folder to find your generated .png charts and the missing_values.csv report.
📊 Data Mapping
For the visualization to work correctly, the program looks for these specific column headers (standardized during cleaning):
elsex: Gender (1 for Male, 2 for Female).
elage: Age of the participants.
eldate: Date of the record.
rcdgtot: Total recruits/count.
📝 License
This project is open-source. Feel free to modify it to suit your specific health data needs.
Author
nkgfiona
Building tools for better health data management in Uganda.
