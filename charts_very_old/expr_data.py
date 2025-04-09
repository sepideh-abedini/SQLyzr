import pandas as pd

df = pd.read_csv("charts/all_scores_new.csv")

df = df[(df['dataset'] == "beaver")]
df = df.groupby(['tmp', 'itr', 'model']).sum()
df = df.drop(columns=[col for col in df.columns if col.startswith('Unnamed')])
df = df.drop(columns=["cat", "dataset","sub_cat"])
df = df.reset_index()

df.to_csv("charts/scores_expr.csv")
print(df)

print(len(df))
