import pandas as pd
from natsort import natsorted

file_path = "thesis_aligned.csv"

df = pd.read_csv(file_path)

# print(df.groupby("sub")['sub'].count())
print(print(df.groupby("sub")['sub'].count().loc[natsorted(df["sub"].unique())]))

df.loc[df["sub"] == "s34", "sub"] = "s28_tmp"
df.loc[df["sub"] == "s33", "sub"] = "s34"
df.loc[df["sub"] == "s32", "sub"] = "s33"
df.loc[df["sub"] == "s31", "sub"] = "s32"
df.loc[df["sub"] == "s30", "sub"] = "s31"
df.loc[df["sub"] == "s29", "sub"] = "s30"
df.loc[df["sub"] == "s28", "sub"] = "s29"
df.loc[df["sub"] == "s28_tmp", "sub"] = "s28"

print(print(df.groupby("sub")['sub'].count().loc[natsorted(df["sub"].unique())]))
# df.loc[df["sub"] == "s33", "sub"] = "s34"
# df.loc[df["sub"] == "s32", "sub"] = "s34"
#
df.to_csv("thesis_aligned_v2.csv")
