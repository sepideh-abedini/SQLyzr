import argparse

import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mtick
from matplotlib.lines import Line2D
from natsort import natsorted

from thesis.lib import config_plt, pre_process_df
from thesis.params import LATEST_SCORES_PATH, OUT_DIR


# --- Helper Function to hide CI for 'overall' ---
def hide_overall_ci(ax, categories, target_cat="overall"):
    """
    Iterates through the lines in the axes.
    If the line corresponds to the 'overall' category position, make it invisible.
    """
    # Find the index of the 'overall' category
    try:
        overall_idx = categories.index(target_cat)
    except ValueError:
        return  # 'overall' not found, nothing to hide

    # Seaborn draws error bars as Line2D objects.
    # The order depends on (n_hues * n_categories).
    # We need to calculate which lines correspond to the 'overall' x-position.

    # Get all lines that are error bars (usually they are simple vertical lines)
    lines = ax.lines

    for line in lines:
        # Get x-coordinates of the line
        x_data = line.get_xdata()

        # Check if the line is positioned at the 'overall' index
        # We use a small epsilon for float comparison because hue shifts bars slightly
        if any(abs(x - overall_idx) < 0.5 for x in x_data):
            line.set_visible(False)


# ------------------------------------------------

def main(in_file, out_file):
    config_plt(plt)
    df = pre_process_df(in_file)
    cats = natsorted(df['cat'].unique())

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True, height_ratios=[1, 1])

    # --- Plot 1: Complexity Consistency ---
    sns.barplot(
        data=df[df['cat'] != 'C6'],
        x='cat',
        y='cc',
        hue='model',
        ax=ax1,
        palette="tab10",
        order=cats,
        estimator="mean",
        err_kws={'linewidth': 5},
        errorbar=("ci", 95),  # Turn ON CI here (95% default)
        capsize=0.0,  # Optional: Adds caps to error bars for visibility
        saturation=1
    )

    hide_overall_ci(ax1, cats, "overall")  # <--- Hide CI for overall

    # -----------

    ax1.set_ylabel('')
    ax1.set_xlabel('')
    ax1.set_title('Complexity Consistency', pad=20)
    ax1.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0f%%'))
    ax1.grid(axis='y', linestyle='--', alpha=0.3)
    ax1.set_ylim(0, 100)
    # ax1.legend(loc='upper right', title=None)

    # --- Plot 2: Execution Time Inconsistency ---
    sns.barplot(
        data=df,
        x='cat',
        y='etc',
        hue='model',
        ax=ax2,
        palette="tab10",
        order=cats,
        estimator="mean",
        err_kws={'linewidth': 5},
        errorbar=("ci", 95),  # Turn ON CI here
        capsize=0.0,
        saturation=1
    )

    hide_overall_ci(ax2, cats, "overall")  # <--- Hide CI for overall

    ax2.set_ylabel('')
    ax2.set_xlabel('Category')
    ax2.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0f%%'))
    ax2.set_title('Execution Time Consistency', pad=20)
    ax2.grid(axis='y', linestyle='--', alpha=0.3)
    ax2.set_ylim(0, 100)

    plt.rcParams["legend.fontsize"] = 20
    handles, labels = ax2.get_legend_handles_labels()
    ci_handle = Line2D([0], [0], color='black', linewidth=5, label='95% CI')
    handles.append(ci_handle)
    labels.append('95% CI')
    ax2.legend(handles=handles, labels=labels, loc='upper right', title=None)
    if ax1.get_legend():
        ax1.get_legend().remove()

    fig.supylabel('Efficiency Score', fontsize=24, fontweight='bold', x=1.02, ha='left', rotation=-90)

    plt.tight_layout()
    plt.savefig(out_file, bbox_inches='tight', dpi=300)
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True)
    parser.add_argument("-o", required=True)
    args = parser.parse_args()
    main(args.i, args.o)
