import pandas as pd

df = pd.read_csv("thesis_scores.csv")

# Move s3 to c1
df.loc[df["sub"] == "s3", "cat"] = "c1"
df.loc[df["sub"] == "s4", "cat"] = "c1"
df.loc[df["sub"] == "s34", "cat"] = "c4"

df.to_csv("thesis_scores_v2.csv")
