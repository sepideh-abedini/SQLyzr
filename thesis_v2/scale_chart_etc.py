import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import matplotlib.ticker as mtick

from thesis.lib import config_plt

scales = [1, 10, 20, 50, 100, 500, 1000]

config_plt(plt)

dfs = []
for scale in scales:
    df = pd.read_csv(f"scale/scores_s{scale}.csv")
    df['scale'] = scale
    dfs.append(df)

combined = pd.concat(dfs, ignore_index=True)

print(combined[['model', 'scale', 'plt']].groupby(['model', 'scale']).mean())

plt.figure(figsize=(10, 6))

ax = sns.barplot(data=combined, x='scale', hue="model", y="plt", estimator="mean", saturation=1)
ax.set_ylim(0, 1)  # set y-axis limits
ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

means = combined.groupby(['model', 'scale'])['plt'].mean().reset_index()

plt.ylabel("Execution Time \n Consistency")
plt.xlabel("Scale factor")

plt.savefig(f"scale-etc.png", bbox_inches='tight', dpi=300)
plt.show()
