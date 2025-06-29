import pandas as pd

df = pd.read_csv("catted.csv")
print(df.keys())
print(len(df))
df['pcat'] = df['pcat'].fillna("c1")
print("Na pcat", df['pcat'].isna().sum())

df['gold_cat_idx'] = df['cat'].str.replace('c', '', regex=False).astype(int)
df['pred_cat_idx'] = df['pcat'].str.replace('c', '', regex=False).astype(int)
df['pred_cat_lt_gold'] = (df['pred_cat_idx'] <= df['gold_cat_idx']).astype(int)
df['plc'] = df['pred_cat_lt_gold'] * df['rea']

df['pred_et_lt_gold'] = df.apply(lambda e: int((e['et'] / e['get']) < 1.46), axis=1)
df["plt"] = df['pred_et_lt_gold'] * df['rea']

df.to_csv("consist_scores.csv")
