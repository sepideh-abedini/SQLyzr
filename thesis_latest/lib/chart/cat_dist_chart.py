import argparse

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from natsort import natsorted


def main(in_file, out_file):
    df = pd.read_csv(in_file)
    df['Category'] = df['cat']
    df = df[df['Category'] != "c1000"]
    print(df.groupby('Category')['Category'].value_counts())
    vc = df['sub'].value_counts()
    print(vc.sum())
    vc = vc.reindex(natsorted(vc.index))
    vc.to_csv("sub_counts.csv")
    print(vc)
    print(df['sub'].value_counts().sum())
    print(df['sub'].value_counts(normalize=True))
    print(df['sub'].value_counts(normalize=True).sum())
    print(len(df))
    plt.figure(figsize=(5, 5))
    sns.countplot(data=df, x="Category", order=natsorted(df["Category"].unique()))
    plt.savefig(out_file, bbox_inches='tight', dpi=300)
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True)
    parser.add_argument("-o", required=True)
    args = parser.parse_args()
    main(args.i, args.o)
