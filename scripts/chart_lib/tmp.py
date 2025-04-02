import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Sample DataFrame with hue column 'z'
df = pd.DataFrame({
    'x': ['A', 'A', 'B', 'B', 'C', 'C'],
    'y': [10, 15, 20, 25, 15, 10],
    'z': ['Group 1', 'Group 2', 'Group 1', 'Group 2', 'Group 1', 'Group 2']
})

# Compute mean for each group (z)
group_means = df.groupby("z")["y"].mean()

# Create bar plot
plt.figure(figsize=(7, 5))
ax = sns.barplot(data=df, x="x", y="y", hue="z", estimator=np.mean)

# Get bar width from Seaborn's plot
bar_width = 0.4  # Adjust width to match Seaborn's bars
x_positions = range(len(group_means))

# Get colors from the Seaborn plot
palette = sns.color_palette()

# Manually add side-by-side bars for the overall mean
for i, (group, mean_value) in enumerate(group_means.items()):
    ax.bar(len(df["x"].unique()), mean_value, width=bar_width, label=f"Overall {group}", color=palette[i])

# Adjust legend to include manually added bars
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles, labels)

# Title
plt.title("Bar Plot with Hue and Manually Added Side-by-Side Overall Means")
plt.xticks(list(range(len(df["x"].unique()))) + [len(df["x"].unique())], list(df["x"].unique()) + ["Mean"])

plt.show()
