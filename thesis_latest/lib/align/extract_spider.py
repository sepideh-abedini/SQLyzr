import argparse

import pandas as pd


def main(in_file, out_file):
    df = pd.read_csv(in_file)
    print(len(df))
    df = df[df['dst'] == "spider"]
    print(len(df))
    df.to_csv(out_file, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True)
    parser.add_argument("-o", required=True)
    args = parser.parse_args()
    main(args.i, args.o)
