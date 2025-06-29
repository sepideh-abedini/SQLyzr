import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mtick
from natsort import natsorted
from latest.lib import pre_process_df, config_plt

config_plt(plt)
df = pre_process_df("all_scores_v10.csv")
cats = natsorted(df['cat'].unique())

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 9), sharex=True, height_ratios=[1, 1])

sns.barplot(
    data=df,
    x='cat',
    y='plc',
    hue='model',
    ax=ax1,
    palette="tab10",
    order=cats,
    estimator="mean",
    errorbar=None,
    saturation=1
)

ax1.set_ylabel('')
ax1.set_xlabel('')
ax1.set_title('Complexity Consistency', pad=20)
ax1.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0f%%'))
ax1.grid(axis='y', linestyle='--', alpha=0.3)
ax1.set_ylim(0, 100)

sns.barplot(
    data=df,
    x='cat',
    y='plt',
    hue='model',
    ax=ax2,
    palette="tab10",
    order=cats,
    estimator="mean",
    errorbar=None,
    saturation=1
)

ax2.set_ylabel('')
ax2.set_xlabel('Category')
ax2.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0f%%'))
ax2.set_title('Execution Time Inconsistency', pad=20)
ax2.grid(axis='y', linestyle='--', alpha=0.3)
ax2.set_ylim(0, 100)

ax2.legend(loc='upper right', title=None)
if ax1.get_legend():
    ax1.get_legend().remove()

fig.supylabel('Efficiency Score', fontsize=24, fontweight='bold', x=1.02, ha='left', rotation=-90)

plt.tight_layout()
plt.savefig("efficiency.png", bbox_inches='tight', dpi=300)
plt.show()
