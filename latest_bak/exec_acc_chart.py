import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from natsort import natsorted

df = pd.read_csv("all_scores_v10.csv")
df["cat"] = df["cat"].str.upper()
df["sub"] = df["sub"].str.upper()
df = df.dropna(subset=["cat"])
cats = natsorted(df['cat'].unique())
sub_cats = natsorted(df['sub'].unique())
df['cat'] = pd.Categorical(df['cat'], categories=cats, ordered=True)
df['sub'] = pd.Categorical(df['sub'], categories=sub_cats, ordered=True)

num_x = df['cat'].nunique()
fig = plt.figure(figsize=(10, 5))
sns.barplot(df, x='cat', y='ea', hue='model', estimator="mean")
fig.show()
