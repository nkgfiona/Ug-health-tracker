import pandas as pd
df = pd.read_csv(r'C:\Users\KON HONEST\Desktop\uganda-health-tracker\health_data.csv')
print(df.head())
for col in df.columns:
    df[col].fillna("Unknown", inplace=True)
print(df.isnull().sum())
print(f'df:\n{df[["Name", "Age"]]}')