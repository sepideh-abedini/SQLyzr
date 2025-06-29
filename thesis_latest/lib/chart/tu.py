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
    df['tokens'] = df['tokens'] / 1000

    fig, ax = plt.subplots(figsize=(12, 6))

    sns.barplot(
        data=df,
        x='cat',
        y='tokens',
        hue='model',
        ax=ax,
        palette="tab10",
        order=cats,
        estimator="mean",
        errorbar=None,
        saturation=1
    )

    ax.set_ylabel('Token Usage')
    ax.set_xlabel('Category')
    ax.set_title('')
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{int(x)}k' if x >= 1 else f'{int(x * 1000)}'))
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    # ax.set_ylim(0, 100)

    # Legend placement
    ax.legend(loc='upper left', title=None)

    plt.tight_layout()
    plt.savefig(out_file, bbox_inches='tight', dpi=300)
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True)
    parser.add_argument("-o", required=True)
    args = parser.parse_args()
    main(args.i, args.o)
