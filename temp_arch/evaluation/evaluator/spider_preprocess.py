import json
import pandas as pd


def main():
    df = pd.read_csv("data/din/DIN-SQL.csv")
    pred_file = open("data/din/pred.txt", "w")
    for idx, row in df.iterrows():
        pred_file.write(f"{row["PREDICTED SQL"]}\n")
    pred_file.close()


if __name__ == '__main__':
    main()
