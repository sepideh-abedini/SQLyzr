import argparse

import pandas as pd
from natsort import index_natsorted


def main(in_file):
    df = pd.read_csv(in_file)
    unique_df = df[['cat', 'sub']].drop_duplicates()
    unique_df = unique_df.iloc[index_natsorted(unique_df['sub'].astype(str))]
    print(unique_df)
    # print(df[['cat','sub']].drop_duplicates())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True)
    args = parser.parse_args()
    main(args.i)
