import matplotlib.pyplot as plt
import pandas as pd

from out.dec31.lib import config_plt

# Load your data
df = pd.read_csv("util_stats.csv")

# --- CONVERSION STEPS ---
# 1. Convert Memory: MB -> GB (Divide by 1024)
df['Max Mem'] = df['Max Mem'] / 1024

# 2. Convert Time: Divide by 1000 (e.g., ms -> s, or s -> 10^3 s)
df['Total CPU Time'] = df['Total CPU Time'] / 1000
df['Total Time'] = df['Total Time'] / 1000

config_plt(plt)

metrics = ['Total CPU Time', 'Max Mem', 'Total Time']
titles = ['Total CPU Time', 'Max Memory Usage', 'Total Execution Time']

y_labels = [
    'Time (1000x s)',
    'Memory (GB)',
    'Time (1000x s)'
]
colors = ['#1f77b4', '#ff7f0e']

fig, axes = plt.subplots(1, 3, figsize=(24, 6))

for i, metric in enumerate(metrics):
    ax = axes[i]

    bars = ax.bar(df['Model'], df[metric], color=colors, width=0.4)

    ax.set_title(titles[i])
    ax.set_ylabel(y_labels[i])

    # if metric == 'Total CPU Time':
    #     ax.set_yscale('log')

    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.set_xlim(-0.8, 1.8)

plt.tight_layout()
plt.savefig("util.png", bbox_inches='tight', dpi=300)
plt.show()