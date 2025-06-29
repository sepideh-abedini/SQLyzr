import argparse
import os

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from natsort import natsorted  # or use the re.split method from before
from sympy.printing.pretty.pretty_symbology import line_width

from latest.lib import config_plt


def draw_with_ecdf(in_file, sqlshare_file, out_file):
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
    plt.figure(figsize=(10, 6))

    # 1. Plot the Cumulative Distribution
    sns.ecdfplot(
        data=df_combined,
        x="Category",
        hue="Workload",
        palette=["#3175af", "#ef8636"],  # Matching your original colors
        linewidth=3
    )

    # 2. Highlight the specific 'c3' comparison
    # Note: 'c3' is at index 2 if c1 is index 0
    cat_index = 2
    plt.axvline(x=cat_index, color='gray', linestyle='--', alpha=0.6)

    # Add annotation for SQLShare (80%)
    plt.annotate('80% of SQLShare ≤ c3', xy=(cat_index, 0.8), xytext=(cat_index - 1.5, 0.85),
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5))

    # Add annotation for SQLyzr (50%)
    plt.annotate('50% of SQLyzr ≤ c3', xy=(cat_index, 0.5), xytext=(cat_index + 0.5, 0.45),
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5))

    plt.ylabel("Cumulative Proportion (Percentile)")
    plt.grid(axis='y', linestyle=':', alpha=0.7)
    plt.tight_layout()
    plt.savefig(out_file, dpi=300)
    plt.show()


def draw_boxplot(in_file, sqlshare_file, out_file):
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
    plt.figure(figsize=(10, 6))
    # 1. Map categories to numbers for calculation (c1 -> 1, c2 -> 2, etc.)
    df_combined['cat_num'] = df_combined['Category'].str.extract('(\d+)').astype(int)

    plt.figure(figsize=(10, 5))

    # 2. Create the boxplot
    # We use 'vert=False' to make it easy to compare the horizontal shift
    sns.boxplot(
        data=df_combined,
        x="cat_num",
        y="Workload",
        palette=["#3175af", "#ef8636"],
        width=0.5
    )

    # 3. Clean up the labels to show 'c1', 'c2' instead of '1', '2'
    plt.xlabel("Category")
    plt.xticks(ticks=[1, 2, 3, 4, 5, 6], labels=['c1', 'c2', 'c3', 'c4', 'c5', 'c6'])

    # 4. Add a vertical line at c3 to highlight your 80% vs 50% point
    plt.axvline(x=3, color='red', linestyle='--', alpha=0.5, label='Threshold (c3)')

    plt.title("Workload Distribution Comparison")
    plt.tight_layout()
    plt.savefig(out_file, dpi=300)
    plt.show()


def print_gradual_percentiles(in_file, sqlshare_file):
    # --- Data Loading and Filtering (Same as your drawing functions) ---
    df_sqlyzr = pd.read_csv(in_file)
    df_sqlyzr = df_sqlyzr[(df_sqlyzr['tmp'] == 0.2) & (df_sqlyzr['model'] == "din") & (df_sqlyzr['itr'] == 0)]

    df_sqlshare = pd.read_csv(sqlshare_file)
    df_sqlshare = df_sqlshare[df_sqlshare['cat'] != "c1000"]

    # --- Calculation Helper ---
    def get_ecdf_stats(df, name):
        # 1. Count frequency of each category
        counts = df['cat'].value_counts(normalize=True)
        # 2. Sort by category name (c1, c2, c3...)
        counts = counts.reindex(natsorted(counts.index))
        # 3. Calculate Cumulative Sum (Percentile)
        ecdf = counts.cumsum() * 100

        print(f"\n--- {name} Percentile Distribution ---")
        for cat, percentile in ecdf.items():
            print(f"Category {cat}: {percentile:.2f}% of data is ≤ {cat}")

    # --- Execute Printing ---
    get_ecdf_stats(df_sqlyzr, "SQLyzr")
    get_ecdf_stats(df_sqlshare, "SQLShare")


def main(in_file, sqlshare_file, out_file):
    config_plt(plt)
    # draw_with_ecdf(in_file, sqlshare_file, out_file)
    # draw_boxplot(in_file, sqlshare_file, out_file)
    print_gradual_percentiles(in_file, sqlshare_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True)
    parser.add_argument("-s", required=True)
    parser.add_argument("-o", required=True)
    args = parser.parse_args()
    main(args.i, args.s, args.o)
