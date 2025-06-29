import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mtick
from matplotlib.lines import Line2D  # <--- Required for custom legend
from natsort import natsorted

from out.dec31.lib import pre_process_df, config_plt

config_plt(plt)

df = pre_process_df("all_scores_v10.csv")
cats = natsorted(df['cat'].unique())

# Convert tokens to 'k' scale
df['tokens'] = df['tokens'] / 1000

fig, ax = plt.subplots(figsize=(12, 6))

sns.barplot(
    data=df,
    x='cat',
    y='tokens',
    hue='model',
    ax=ax,
    palette="tab10",
    order=cats,
    estimator="mean",
    err_kws={'linewidth': 5}, # Custom width for error lines
    errorbar=("ci", 95),      # Enable 95% CI
    capsize=0.0,
    saturation=1
)

ax.set_ylabel('Token Usage')
ax.set_xlabel('Category')
ax.set_title('')

# Custom formatter: shows '2k' for 2000, or raw number if < 1k (though you divided by 1000)
# Note: Since you divided by 1000, 'x' here is already in thousands.
# If x=2, that means 2000 tokens. The logic below handles the "k" suffix.
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{int(x)}k'))

ax.grid(axis='y', linestyle='--', alpha=0.3)

# --- CUSTOM LEGEND LOGIC ---
handles, labels = ax.get_legend_handles_labels()
ci_handle = Line2D([0], [0], color='black', linewidth=5, label='95% CI')
handles.append(ci_handle)
labels.append('95% CI')

ax.legend(handles=handles, labels=labels, loc='upper left', title=None)
# ---------------------------

plt.tight_layout()
plt.savefig("tuci.png", bbox_inches='tight', dpi=300)
plt.show()