
import matplotlib.pyplot as plt
import pandas as pd
def clean_data(self, file_path):
    # Read the CSV file into a DataFrame
    self.df = pd.read_csv(file_path)
    self.df.drop_duplicates(inplace=True)
    self.df.columns = self.df.columns.str.strip().str.lower().str.replace(' ', '_')
    self.df = self.df.fillna("Unknown")
    return self.df
def bar_grapeh(self, column):
    if column in self.df.columns:
        counts = self.df[column].value_counts().head(5)
        plt.figure(figsize=(10, 6)) # Makes the chart a bit larger/readable
        plt.bar(counts.index, counts.values, color='skyblue')
        plt.xlabel(column.replace(' ', '_').title())    
        plt.ylabel('Count')
        plt.title(f'Top 5 {column.replace("_", " ").title()}')
        plt.xticks(rotation=45, ha='right') # Rotate x-axis labels for better readability
        plt.tight_layout() # Adjust layout to prevent clipping of labels
        plt.savefig('chart1.png') # Save the figure as a PNG file
        print("✅ Chart saved as 'chart1.png'")
        
        plt.show()
    else:
        print(f"❌ Column '{column}' not found. Available columns: {list(self.df.columns)}")
        
def line_chart_over_time(self, date_column, value_column=None):
    if date_column in self.df.columns:
        # 1. Convert column to datetime and sort
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        
        # 2. Group by date
        # If you just want a count of entries per date:
        if value_column is None:
            time_data = self.df.groupby(date_column).size()
            ylabel = "Number of Cases"
        else:
            # If you want to sum a specific column (like 'cases' or 'deaths')
            time_data = self.df.groupby(date_column)[value_column].sum()
            ylabel = value_column.replace('_', ' ').title()

        # 3. Create the Plot
        plt.figure(figsize=(12, 6))
        plt.plot(time_data.index, time_data.values, marker='o', linestyle='-', color='red')
        
        # 4. Labels and Title
        plt.title(f'{ylabel} Over Time', fontsize=14)
        plt.xlabel('Date')
        plt.ylabel(ylabel)
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # 5. Formatting the date on the X-axis
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # 6. Save and Show
        plt.savefig('chart2.png')
        print("✅ Line chart saved as 'chart2.png'")
        plt.show()
    else:
        print(f"❌ Date column '{date_column}' not found.")