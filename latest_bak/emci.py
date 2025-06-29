import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mtick
from matplotlib.lines import Line2D
from natsort import natsorted

from out.dec31.lib import pre_process_df, config_plt

# Global style settings
config_plt(plt)

# Load and sort data
df = pre_process_df("all_scores_v10.csv")
cats = natsorted(df['cat'].unique())

# Initialize a single plot
fig, ax = plt.subplots(figsize=(12, 6))

# Generate the barplot for EM
sns.barplot(
    data=df,
    x='cat',
    y='em',
    hue='model',
    ax=ax,
    palette="tab10",
    order=cats,
    estimator="mean",
    err_kws={'linewidth': 5}, # Thick error bars
    errorbar=("ci", 95),      # Enable 95% CI
    capsize=0.0,              # No caps
    saturation=1
)

# Formatting
ax.set_ylabel('Exact Match')
ax.set_xlabel('Category')
ax.set_title('')
ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0f%%'))
ax.grid(axis='y', linestyle='--', alpha=0.3)
ax.set_ylim(0, 100)

# --- CUSTOM LEGEND LOGIC ---
# 1. Get existing handles (the colored bars) and labels
handles, labels = ax.get_legend_handles_labels()

# 2. Create the proxy artist for the error bar (black line)
#    Matches the linewidth used in err_kws above
ci_handle = Line2D([0], [0], color='black', linewidth=5, label='95% CI')

# 3. Append to the legend
handles.append(ci_handle)
labels.append('95% CI')

# 4. Apply the combined legend
ax.legend(handles=handles, labels=labels, loc='upper right', title=None)
# ---------------------------

plt.tight_layout()
plt.savefig("emci.png", bbox_inches='tight', dpi=300)
plt.show()