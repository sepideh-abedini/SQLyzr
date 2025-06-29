import pandas as pd

df = pd.read_csv("all_scores_v9.csv")

# Move s3 to c2
df.loc[df["sub"] == "s3", "cat"] = "c2"

# Delete s11
mig_dict = {f"s{i}": f"s{i - 1}" for i in range(12, 31)}
df["sub"] = df["sub"].replace(mig_dict)

result = df.groupby("sub").count()
print(result)

df.to_csv("all_scores_v10.csv")
