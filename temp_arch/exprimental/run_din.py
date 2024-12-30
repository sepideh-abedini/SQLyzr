import pandas as pd

from src.exprimental.db_facade import DatabaseFacade
from src.exprimental.tuple_transformer import ColTuple


def main():
    in_file = "data/din/DIN-SQL.csv"

    db_facade = DatabaseFacade("data/spider/database")

    df = pd.read_csv(in_file)
    match = 0

    non_match_ids = []
    for idx, row in df.iterrows():
        db_id = row["DATABASE"]
        pred = row["PREDICTED SQL"]
        gold = row["GOLD SQL"]

        pred_res = db_facade.execute_query(db_id, pred)
        gold_res = db_facade.execute_query(db_id, gold)

        if pred_res == gold_res:
            match += 1
        else:
            non_match_ids.append(idx)
    df = df[df.index.isin(non_match_ids)]
    df.to_csv("data/din/din_non_match.csv", index=True)

    print(match)


if __name__ == "__main__":
    main()
