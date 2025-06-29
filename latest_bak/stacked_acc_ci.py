import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import seaborn as sns
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

# Assuming 'pre_process_df' and 'config_plt' are available from your library
from out.dec31.lib import pre_process_df, config_plt

config_plt(plt)
plt.rcParams["legend.fontsize"] = 18

df = pre_process_df("all_scores_v10.csv", False)

# --- MODIFIED SECTION: Calculate Means and Confidence Intervals ---
# 1. Group by category and model, then calculate count, mean, and std dev
stats = df.groupby(['cat', 'model'], observed=True)[['ea', 'rea']].agg(['mean', 'count', 'std'])

# 2. Calculate 95% Confidence Interval (Margin of Error)
# Formula: 1.96 * (std / sqrt(count))
ci95 = 1.96 * stats.xs('std', level=1, axis=1) / np.sqrt(stats.xs('count', level=1, axis=1))
means = stats.xs('mean', level=1, axis=1)

# Reset index to make 'cat' and 'model' columns again for pivoting
means = means.reset_index()
ci95 = ci95.reset_index()

# 3. Pivot Data for Plotting
# Values (Heights)
df_ea = means.pivot(index='cat', columns='model', values='ea').fillna(0)
df_rea = means.pivot(index='cat', columns='model', values='rea').fillna(0)
df_delta = df_rea - df_ea

# Errors (CI bars)
df_ea_err = ci95.pivot(index='cat', columns='model', values='ea').fillna(0)
df_rea_err = ci95.pivot(index='cat', columns='model', values='rea').fillna(0)
# ---------------------------------------------------------------

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

    current_err = df_rea_err[model].copy()
    if 'Overall' in current_err.index:
        current_err.loc['Overall'] = np.nan

    # Plot EA (Base Bar) with Error Bars
    ax.bar(pos, df_ea[model], bar_width, color=colors[i], edgecolor='none')

    ax.bar(pos, df_delta[model], bar_width, bottom=df_ea[model],
           yerr=current_err, capsize=5, error_kw={'elinewidth': 1.5, 'ecolor': 'black'},
           color=colors[i], alpha=0.5, hatch='///',
           edgecolor=colors[i], linewidth=0)

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

legend_elements = []

for i, model in enumerate(models):
    legend_elements.append(Patch(facecolor=colors[i], edgecolor='none',
                                 label=f'{model} EA'))

    legend_elements.append(Patch(facecolor=colors[i], alpha=0.5, hatch='///',
                                 edgecolor=colors[i], label=f'{model} REA'))

legend_elements.append(Line2D([0], [0], color='green', marker='o', linestyle='-',
                              label='Average EA', alpha=0.6))
legend_elements.append(Line2D([0], [0], color='green', marker='o', linestyle='--',
                              label='Average REA', alpha=0.6))

ci_handle = ax.errorbar([np.nan], [np.nan], xerr=[0.5], fmt='none', ecolor='black', elinewidth=1.5, capsize=5,
                        label='95% CI')
legend_elements.append(ci_handle)

ax.legend(handles=legend_elements, bbox_to_anchor=(0.825, 1), loc='upper right')

plt.tight_layout()
plt.savefig("eareaci.png", bbox_inches='tight', dpi=300)
plt.show()
