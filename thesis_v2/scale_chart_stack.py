import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

scales = [1, 10, 20, 50, 100]
dfs = []
for scale in scales:
    df = pd.read_csv(f"scale/scores_s{scale}.csv")
    df['scale'] = scale
    # Create a total column for the full height of the bar
    df['total'] = df['et'] + df['get']
    dfs.append(df)

combined = pd.concat(dfs, ignore_index=True)

# 1. Plot the Total (ET + GET) first
ax = sns.barplot(data=combined, x='scale', hue="model", y='total',
                 estimator="mean", errorbar=None)

colors = sns.color_palette("tab10", n_colors=2)
# 2. Apply hatching to the top part (GET)
for patch in ax.patches:
    patch.set_hatch('///')

# 3. Overlay the ET part (solid) on top
sns.barplot(data=combined, x='scale', hue="model", y='et',
            estimator="mean", errorbar=None, ax=ax, saturation=1)

# Clean up legend (remove duplicates from double plotting)
handles, labels = ax.get_legend_handles_labels()
plt.legend(handles[:len(combined['model'].unique())],
           labels[:len(combined['model'].unique())], title='Model')

plt.ylabel("et (solid) + get (///)")
plt.show()
