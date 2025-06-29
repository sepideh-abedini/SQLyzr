import argparse

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
from natsort import natsorted

from thesis.lib import config_plt, pre_process_df


def main(in_file, out_file):
    config_plt(plt)

    df = pre_process_df(in_file)
    cats = natsorted(df['cat'].unique())

    fig, ax = plt.subplots(figsize=(12, 6))

    sns.barplot(
        data=df,
        x='cat',
        y='etc',
        hue='model',
        ax=ax,
        palette="tab10",
        order=cats,
        estimator="mean",
        errorbar=("ci", 95),
        saturation=1,
        err_kws={'linewidth': 5},
        capsize=0.0,
    )

    ax.set_ylabel('Execution Time\n Consistency')
    ax.set_xlabel('Category')
    ax.set_title('')
    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0f%%'))
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    # ax.set_ylim(0, 100)

    # Legend placement
    ax.legend(title=None)

    plt.tight_layout()
    plt.savefig(out_file, bbox_inches='tight', dpi=300)
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True)
    parser.add_argument("-o", required=True)
    args = parser.parse_args()
    main(args.i, args.o)
