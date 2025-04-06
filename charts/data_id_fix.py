import pandas as pd

name = "dail_beaver_all"
path = f"data/{name}/scores_raw_with_toks.csv"
df = pd.read_csv(path)

g = df.groupby(["itr", "tmp"]).size()
dataset_size = g.iloc[0]
print("Dataset Size", dataset_size)

rows = []
for i, row in df.iterrows():
    row['ds_idx'] = (i % dataset_size)
    rows.append(row)

new_df = pd.DataFrame(rows)
new_df.to_csv(f"{path}.new.csv")


