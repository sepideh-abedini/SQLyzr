import argparse
import os.path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from thesis.lib import config_plt
from thesis_latest.lib.params import SCALES


def main(in_dir, out_file):
    config_plt(plt)
    dfs = []
    for scale in SCALES:
        df = pd.read_csv(os.path.join(in_dir, f"scores_s{scale}.csv"))
        df['scale'] = scale
        df['gets'] = df['get'] / 1000
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)

    plt.figure(figsize=(10, 6))

    sns.barplot(data=combined, x='scale', y="gets", estimator="mean", saturation=1, errorbar=None)
    plt.ylabel("Gold Execution Time (s)")
    plt.xlabel("Scale factor")
    plt.savefig(out_file, bbox_inches='tight', dpi=300)
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True)
    parser.add_argument("-o", required=True)
    args = parser.parse_args()
    main(args.i, args.o)
