import pandas as pd

df = pd.read_csv("all_scores_v11.csv")

# Move s3 to c1
df.loc[df["sub"] == "s4", "cat"] = "c1"

result = df.groupby("sub").count()
print(result)

df.to_csv("all_scores_v12.csv")
