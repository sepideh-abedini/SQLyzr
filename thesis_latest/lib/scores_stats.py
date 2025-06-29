import argparse

import pandas as pd
from natsort import index_natsorted, natsorted


def main(in_file):
    df = pd.read_csv(in_file)
    print(df[['model', 'ea']].groupby('model').mean())
    print(df[['model', 'rea']].groupby('model').mean())
    df = df[['cat', 'sub']]
    grouped = df.groupby(['cat', 'sub']).size()
    grouped = grouped.reindex(
        natsorted(grouped.index, key=lambda x: (x[0], x[1]))
    )
    print(grouped)

    # unique_df = df[['cat', 'sub']].drop_duplicates()
    # unique_df = unique_df.iloc[index_natsorted(unique_df['sub'].astype(str))]
    # print(unique_df)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True)
    args = parser.parse_args()
    main(args.i)
