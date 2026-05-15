import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt 
        

#df=pd.read_csv('C:\\Users\\KON HONEST\\Desktop\\uganda-health-tracker\\Global_Health_Statistics.csv')
#print(df.columns)
# Grouping by health data by one column (e.g. region). Calculate: total cases, average cases, maximum value
#df=df.groupby('Country')['Prevalence Rate (%)'].agg(['sum', 'mean', 'max'])
#print(df)
#sorted_df=df.sort_values(by='sum', ascending=False)
#print(sorted_df.head(10))
#Add a new column to your dataset for cases per 1000 population. Calculate this by dividing the total cases by the population and multiplying by 100
#df = df.rename(columns={'Incidence Rate (%)': 'Incidence', 'Population Affected': 'Population'})
#country_data = df.groupby('Country')[['Incidence', 'Population']].sum()  
#country_data['Cases per 1000'] = (country_data['Incidence'] / country_data['Population']) * 1000
#country_data_sorted = country_data.sort_values(by='Cases per 1000', ascending=False)
#df=df.drop(columns=['Population Affected'])
#print(df.columns)
#df=df.to_csv('cleaned_health_data.csv', index=False)
df=pd.read_csv('C:\\Users\\KON HONEST\\Desktop\\uganda-health-tracker\\merged_health_results.csv')
#df=pd.read_csv('C:\\Users\\KON HONEST\\Desktop\\uganda-health-tracker\\Global_Health_Statistics.csv')
merged_health_results = pd.read_csv('merged_health_results.csv')
#global_health=pd.read_csv('C:\\Users\\KON HONEST\\Desktop\\uganda-health-tracker\\Global_Health_Statistics.csv')
#merged_health_results.Gender=merged_health_results.Gender.apply(lambda x: 1 if x == 'Male' else 0)
#merged_health_results= merged_health_results.drop(['Country','Year','','Disease Category','Disease Category','Treatment Type','Treatment Type','Availability of Vaccines/Treatment'], axis=1, errors='ignore')
#merged_health_results.corr()

plt.figure(figsize=(10,6))
#sns.barplot(global_health, x='Year', y='Population Affected', hue='Gender')
sns.scatterplot(merged_health_results,x='Education Index', y='DALYs', hue='Gender')
#sns.heatmap(merged_health_results.corr(), cmap='coolwarm')
plt.show()

