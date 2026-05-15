git statusimport pandas as pd

df = pd.read_csv('C:\\Users\\KON HONEST\\Desktop\\uganda-health-tracker\\Global_Health_Statistics.csv')

# Sum the population by country
#population_by_country = df.groupby('Country')[['Population Affected']].sum()

#population_by_country.to_csv('population_by_country.csv', index=True)

#def merge_health_data():
    # Load the two files we want to combine
#    df1 = pd.read_csv('C:\\Users\\KON HONEST\\Desktop\\uganda-health-tracker\\cleaned_health_data.csv')
#    df2 = pd.read_csv('C:\\Users\\KON HONEST\\Desktop\\uganda-health-tracker\\population_by_country.csv') 
    
    # Perform the merge on the common 'Country' column
#    merged_df = pd.merge(df1, df2, on='Country') 
    
#    return merged_df

#final_df = merge_health_data()

# Save the final result
#final_df.to_csv('merged_health_results.csv', index=False)
#print("Merge Complete! Check merged_health_results.csv")

# 1. Calculate correlation on NUMBERS only
correlation_matrix = final_df.corr(numeric_only=True)

# 2. Pass that specific matrix into the heatmap
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')

# 3. Add your titles and show
plt.title('Correlation Heatmap of Health Data')
plt.show()

