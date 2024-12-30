import json

import pandas as pd

from src.exprimental.db_facade import DatabaseFacade
from src.exprimental.tuple_transformer import ColTuple


def main():
    pred_path = "data/dail/pred.sql"
    gold_path = "data/spider/dev.json"

    db_facade = DatabaseFacade("data/spider/database")
    df = pd.DataFrame(columns=['NLQ', 'PREDICTED SQL', 'GOLD SQL', 'DATABASE'])
    with open(pred_path) as pred_file, open(gold_path) as gold_file:
        gold_json = json.load(gold_file)
        pred_lines = pred_file.readlines()
        match = 0
        for idx, row in enumerate(gold_json):
            db_id = row['db_id']
            gold = row["query"]
            pred = pred_lines[idx]

            pred_res = db_facade.execute_query(db_id, pred)
            gold_res = db_facade.execute_query(db_id, gold)

            if pred_res == gold_res:
                match += 1
            else:
                df.loc[idx] = [row["question"], pred, gold, db_id]
    df.to_csv("data/dail/dail_non_match.csv")
    print(match)


if __name__ == "__main__":
    main()
