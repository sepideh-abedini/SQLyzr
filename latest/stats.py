import sys

import pandas as pd


def main(input):
    df = pd.read_csv(input)
    print(df.groupby("sub").size())


if __name__ == '__main__':
    main(sys.argv[1])
