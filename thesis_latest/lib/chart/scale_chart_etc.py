import argparse
import os.path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import matplotlib.ticker as mtick

from thesis.lib import config_plt
from thesis_latest.lib.params import SCALES


def main(in_dir, out_file):
    config_plt(plt)

    dfs = []
    for scale in SCALES:
        df = pd.read_csv(os.path.join(in_dir, f"scores_s{scale}.csv"))
        df['scale'] = scale
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)

    print(combined[['model', 'scale', 'plt']].groupby(['model', 'scale']).mean())

    plt.figure(figsize=(10, 6))

    ax = sns.barplot(data=combined, x='scale', hue="model", y="plt", estimator="mean", saturation=1)
    ax.set_ylim(0, 1)  # set y-axis limits
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

    means = combined.groupby(['model', 'scale'])['plt'].mean().reset_index()

    plt.ylabel("Execution Time \n Consistency")
    plt.xlabel("Scale factor")

    plt.savefig(out_file, bbox_inches='tight', dpi=300)
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True)
    parser.add_argument("-o", required=True)
    args = parser.parse_args()
    main(args.i, args.o)
