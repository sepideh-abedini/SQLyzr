import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import seaborn as sns
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from out.dec31.lib import pre_process_df, config_plt

config_plt(plt)
plt.rcParams["legend.fontsize"] = 20

df = pre_process_df("all_scores_v10.csv")
# 2. Aggregation & Pivot
df_agg = df.groupby(['cat', 'model'], observed=True)[['ea', 'rea']].mean().reset_index()

df_ea = df_agg.pivot(index='cat', columns='model', values='ea').fillna(0)
df_rea = df_agg.pivot(index='cat', columns='model', values='rea').fillna(0)
df_delta = df_rea - df_ea

models = df_ea.columns
categories = df_ea.index
n_models = len(models)
x = np.arange(len(categories))

total_width = 0.8
bar_width = total_width / n_models
colors = sns.color_palette("tab10", n_colors=n_models)

fig, ax = plt.subplots(figsize=(12, 9))

# 3. Plotting Loop
for i, model in enumerate(models):
    offset = (i - n_models / 2 + 0.5) * bar_width
    pos = x + offset

    ax.bar(pos, df_ea[model], bar_width,
           color=colors[i], edgecolor='none')

    ax.bar(pos, df_delta[model], bar_width, bottom=df_ea[model],
           color=colors[i], alpha=0.5, hatch='///',
           edgecolor=colors[i], linewidth=0)

# 4. Averages Lines
# Changed color to 'gray' and added alpha=0.6 for a lighter, transparent look
non_overall = categories != "Overall"
avg_ea = df_ea.mean(axis=1)
ax.plot(x[non_overall], avg_ea[non_overall], color='green', marker='o', linestyle='-', linewidth=2, alpha=0.6)

avg_rea = df_rea.mean(axis=1)
ax.plot(x[non_overall], avg_rea[non_overall], color='green', marker='o', linestyle='--', linewidth=2, alpha=0.6)

ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0f%%'))

ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.set_ylabel('Accuracy Score', rotation=-90, labelpad=40)
ax.yaxis.set_label_position("right")
ax.set_xlabel('Category')
# ax.set_title('Execution Accuracy (Solid) vs. Relaxed Gain (Hatched)')

legend_elements = []

for i, model in enumerate(models):
    legend_elements.append(Patch(facecolor=colors[i], edgecolor='none',
                                 label=f'{model} EA'))

    legend_elements.append(Patch(facecolor=colors[i], alpha=0.5, hatch='///',
                                 edgecolor=colors[i], label=f'{model} REA'))

legend_elements.append(Line2D([0], [0], color='green', marker='o', linestyle='-', label='Average EA', alpha=0.6))
legend_elements.append(Line2D([0], [0], color='green', marker='o', linestyle='--', label='Average REA', alpha=0.6))
ax.legend(handles=legend_elements, bbox_to_anchor=(0.84, 1), loc='upper right')

plt.tight_layout()
plt.savefig("earea.png", bbox_inches='tight', dpi=300)
plt.show()

