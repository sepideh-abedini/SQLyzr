import pandas as pd

df = pd.read_csv("thesis_scores_v1.csv")

# Move s34 to c5
df.loc[df["sub"] == "s34", "cat"] = "c5"

df.to_csv("thesis_scores_v2.csv")
