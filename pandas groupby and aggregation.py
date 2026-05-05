import pandas as pd
df=pd.read_csv('C:\\Users\\KON HONEST\\Desktop\\uganda-health-tracker\\Global_Health_Statistics.csv')
print(df.columns)
# Grouping by health data by one column (e.g. region). Calculate: total cases, average cases, maximum value
df=df.groupby('Country')['Prevalence Rate (%)'].agg(['sum', 'mean', 'max'])
print(df)
sorted_df=df.sort_values(by='sum', ascending=False)
print(sorted_df.head(10))
#Add a new column to your dataset for cases per 1000 population. Calculate this by dividing the total cases by the population and multiplying by 100
df = df.rename(columns={'Incidence Rate (%)': 'Incidence', 'Population Affected': 'Population'})
country_data = df.groupby('Country')[['Incidence', 'Population']].sum()  
country_data['Cases per 1000'] = (country_data['Incidence'] / country_data['Population']) * 1000
country_data_sorted = country_data.sort_values(by='Cases per 1000', ascending=False)

print(country_data_sorted)