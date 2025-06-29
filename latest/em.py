import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mtick
from natsort import natsorted

from out.dec31.lib import pre_process_df, config_plt

# Note: Ensure your local environment has the correct path for pre_process_df
# from out.dec31.lib import pre_process_df

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
    errorbar=None,
    saturation=1
)

# Formatting
ax.set_ylabel('Exact Match')
ax.set_xlabel('Category')
ax.set_title('')
ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0f%%'))
ax.grid(axis='y', linestyle='--', alpha=0.3)
ax.set_ylim(0, 100)

# Legend placement
ax.legend(loc='upper right', title=None)

plt.tight_layout()
plt.savefig("em.png", bbox_inches='tight', dpi=300)
plt.show()