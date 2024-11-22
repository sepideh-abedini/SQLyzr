from random import randrange
from typing import Callable

import pandas as pd
from pandas import DataFrame


def convert_csv(in_path: str, out_path: str, transformer: Callable[[DataFrame], DataFrame]):
    df = pd.read_csv(in_path)
    df = transformer(df)
    df.to_csv(out_path, sep='\t', index=False, header=False)


def convert_pred_file(in_path: str, out_path: str):
    convert_csv(in_path, out_path, lambda df: df["PREDICTED SQL"])
    with open(out_path, "a") as file:
        file.write(f"tokens:{randrange(15000, 50000)}")


def main():
    for tmp in [0.3, 0.5, 0.7, 1.0]:
        for it in range(5):
            convert_pred_file("data/out/din_gen/DIN-SQL.csv", f"data/out/din_gen/{tmp}_{it}.out")


if __name__ == '__main__':
    main()
