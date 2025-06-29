import pandas as pd

df = pd.read_csv("sqlyzr_c1_s3.csv")

print(len(df))

print(df['itr'].unique())


df['ds_idx'] = df['dst'].astype(str) + df['ds_idx'].astype(str)
df = df.groupby(['ds_idx'], as_index=False).first()
print(len(df))
df = df[['cat']]
counts = df['cat'].value_counts().sort_index()
print(counts)
