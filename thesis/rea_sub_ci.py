import os

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import seaborn as sns
from matplotlib.lines import Line2D  # <--- Required for custom legend
from natsort import natsorted

from thesis.lib import config_plt, pre_process_df
from thesis.params import LATEST_SCORES_PATH, OUT_DIR


config_plt(plt)


def get_global_max_subs(df, all_cats):
    max_len = 0
    for c in all_cats:
        subs = df[df['cat'] == c]['sub'].unique()
        subs = [s for s in subs if s not in ["S0", "Overall"]]
        if len(subs) > max_len:
            max_len = len(subs)
    return max_len


def draw_chunk(df, cat_chunk, max_subs, chunk_idx):
    rows = len(cat_chunk)

    metrics = ['em', 'ea', 'rea']
    titles = {
        'em': 'Exact Match (EM)',
        'ea': 'Execution Accuracy (EA)',
        'rea': 'Relaxed Execution Accuracy (REA)'
    }
    fig, axes = plt.subplots(rows, len(metrics), figsize=(24, 28), sharey=True, squeeze=False)

    for r, c in enumerate(cat_chunk):
        df_c = df[df['cat'] == c]
        cats = natsorted(df_c['sub'].unique())
        if "S0" in cats: cats.remove("S0")

        for col, metric in enumerate(metrics):
            ax = axes[r][col]

            sns.barplot(
                data=df_c,
                x='sub',
                y=metric,
                hue='model',
                ax=ax,
                palette="tab10",
                order=cats,
                estimator="mean",
                err_kws={'linewidth': 5},  # Thick error bars
                errorbar=("ci", 95),  # Enable 95% CI
                capsize=0.0,  # No caps
                saturation=1
            )

            ax.set_ylabel('')
            ax.set_xlabel('')

            if r == 0:
                ax.set_title(titles[metric], fontsize=28, pad=20)
            else:
                ax.set_title('')

            ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0f%%'))
            ax.set_ylim(0, 100)
            ax.grid(axis='y', linestyle='--', alpha=0.3)

            if col == len(metrics) - 1:
                # Add category label on the right side
                ax.text(1.05, 0.5, c, transform=ax.transAxes,
                        fontsize=32, fontweight='bold', va='center', ha='left', rotation=-90)

            # X-Axis Standardization
            ax.set_xlim(-0.5, max_subs - 0.5)

            # --- LEGEND HANDLING ---
            # We only put the legend on the very first plot (top-left)
            if r == 0 and col == 0:
                # 1. Get existing handles
                handles, labels = ax.get_legend_handles_labels()

                # 2. Create proxy for CI
                ci_handle = Line2D([0], [0], color='black', linewidth=5, label='95% CI')

                # 3. Append and set
                handles.append(ci_handle)
                labels.append('95% CI')

                ax.legend(handles=handles, labels=labels, loc='upper right', title=None, fontsize=18)
            else:
                if ax.get_legend():
                    ax.get_legend().remove()

    # Shared X-Label at the bottom of the entire figure
    fig.supxlabel('Sub-Category', y=0.01, fontsize=24, fontweight='bold')

    # Add label for Y-axis (Score) generally if desired, or relying on per-row/col logic
    # fig.supylabel('Score', x=0.08, fontsize=24, fontweight='bold')

    plt.tight_layout()
    # Add padding for the sup-xlabel
    plt.subplots_adjust(bottom=0.05)

    output_name = f"grid{chunk_idx}.png"  # Simplified name to avoid too long filenames
    plt.savefig(os.path.join(OUT_DIR, output_name), bbox_inches='tight', dpi=300)
    print(f"Saved {output_name}")
    plt.show()


df = pre_process_df(LATEST_SCORES_PATH)

# for m in ["ea", "rea"]:
#     fdf = df[['cat', 'sub', 'model', m]]
#     sub_stats = (
#         fdf.groupby(['cat', 'sub', 'model'])[m]
#         .agg(mu='mean', n='count')
#         .reset_index()
#     )
#
#     cat_mu = (
#         df.groupby(['cat', 'model'])[m]
#         .mean()
#         .rename('cat_mu')
#         .reset_index()
#     )
#
#     stats = sub_stats.merge(cat_mu, on='cat')
#     stats['w'] = stats['n'] / stats.groupby('cat')['n'].transform('sum')
#
#     weighted_std = (
#         stats.groupby('cat')
#         .apply(lambda x: np.sqrt((x['w'] * (x['mu'] - x['cat_mu']) ** 2).sum()))
#         .rename('weighted_std')
#     )
#     print(m, weighted_std)
#
# weighted_std
# x = df[['cat', 'model', m]].groupby(['cat', 'model']).mean()[m]
# print(x)

cats = natsorted(df['cat'].unique())
if "Overall" in cats:
    cats.remove("Overall")

max_subs = get_global_max_subs(df, cats)

chunk_size = 6
cat_chunks = [cats[i:i + chunk_size] for i in range(0, len(cats), chunk_size)]

for i, chunk in enumerate(cat_chunks):
    draw_chunk(df, chunk, max_subs, i)
