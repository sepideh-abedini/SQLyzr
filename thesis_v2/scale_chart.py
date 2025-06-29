import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from thesis.lib import config_plt

scales = [1, 10, 20, 50, 100, 500, 1000]

config_plt(plt)

dfs = []
for scale in scales:
    df = pd.read_csv(f"scale/scores_s{scale}.csv")
    df['scale'] = scale
    df['gets'] = df['get'] / 1000
    dfs.append(df)

combined = pd.concat(dfs, ignore_index=True)

plt.figure(figsize=(10, 6))

sns.barplot(data=combined, x='scale', hue="model", y="gets", estimator="mean", saturation=1,errorbar=None)
plt.ylabel("Gold Execution Time (s)")
plt.xlabel("Scale factor")
plt.savefig(f"scale-get.png", bbox_inches='tight', dpi=300)
plt.show()
