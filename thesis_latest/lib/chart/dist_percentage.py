import argparse
import os

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from natsort import natsorted  # or use the re.split method from before
from sympy.printing.pretty.pretty_symbology import line_width

from latest.lib import config_plt


def draw_with_histplot(in_file, sqlshare_file, out_file):
    df_sqlyzr = pd.read_csv(in_file)
    df_sqlyzr = df_sqlyzr[(df_sqlyzr['tmp'] == 0.2) & (df_sqlyzr['model'] == "din") & (df_sqlyzr['itr'] == 0)]
    df_sqlyzr['Workload'] = 'SQLyzr'

    df_sqlshare = pd.read_csv(sqlshare_file)
    df_sqlshare = df_sqlshare[df_sqlshare['cat'] != "c1000"]
    df_sqlshare['Workload'] = 'SQLShare'

    df_combined = pd.concat([df_sqlyzr, df_sqlshare], ignore_index=True)
    df_combined["Category"] = df_combined['cat']

    sorted_order = natsorted(df_combined['Category'].unique())

    df_combined['Category'] = pd.Categorical(df_combined['Category'], categories=sorted_order, ordered=True)
    plt.figure(figsize=(10, 6))

    # sns.histplot(
    #     data=df_combined,
    #     x="Category",
    #     hue="Workload",
    #     hue_order=["SQLyzr", "SQLShare"],
    #     multiple="dodge",
    #     stat="percent",
    #     common_norm=False,
    #     shrink=0.8,
    #     hue_norm=None,
    #     alpha=1.0,
    #     edgecolor="red",
    #     linewidth=0,
    #     # kde=True
    # )

    sns.displot(
        data=df_combined,
        x="Category",
        hue="Workload",
        cumulative=True,
    )
    # sns.histplot(
    #     data=df_combined,
    #     x="Category",
    #     hue="Workload",
    #     hue_order=["SQLyzr", "SQLShare"],
    #     multiple="dodge",
    #     stat="percent",
    #     common_norm=False,
    #     shrink=0.8,
    #     hue_norm=None,
    #     alpha=1.0,
    #     edgecolor="red",
    #     linewidth=0,
    #     # kde=True
    # )
    # Inside draw_with_histplot

    plt.ylabel("Percentage within\n Workload (%)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(out_file, dpi=300)
    plt.show()


def main(in_file, sqlshare_file, out_file):
    config_plt(plt)
    draw_with_histplot(in_file, sqlshare_file, out_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True)
    parser.add_argument("-s", required=True)
    parser.add_argument("-o", required=True)
    args = parser.parse_args()
    main(args.i, args.s, args.o)
