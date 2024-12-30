import pandas as pd

from src.exprimental.matcher.sql_data import SqlInputData, SqlExecResult
from src.exprimental.transformer_detector import TransformerDetector

# skips = [469, 470, 471, 472]
skips = []
class BatchMatcher:

    def __init__(self, tables_path: str, db_dir: str):
        self.detector = TransformerDetector()

    def run(self, in_file: str):
        df = pd.read_csv(in_file, index_col=0)
        match = 0
        total = 0
        for idx, row in df.iterrows():
            # if idx <= 460:
            #     continue
            # if idx in skips:
            #     continue
            total += 1
            db_id = row["DATABASE"]
            pred_sql = row["PREDICTED SQL"]
            gold_sql = row["GOLD SQL"]
            print("#################################\n")
            print(f"idx = {idx}")
            print(f"pred = {pred_sql}")
            print(f"gold = {gold_sql}")

            pred = SqlInputData(db_id, pred_sql)
            gold = SqlInputData(db_id, gold_sql)

            procs = self.detector.find_working_sub(pred, gold)

            if procs:
                print(f"nl = \"{row['NLQ']}\"")
                match += 1
                print(f"Working procs: {procs}")
            print("#################################\n")
        return match, total

    def print_pred_gold_res(self, pred: SqlExecResult, gold: SqlExecResult):
        print(f"db_id = \"{pred.db_id}\"")
        print(f"pred = \"{pred.sql}\"")
        print(f"gold = \"{gold.sql}\"")
        print("-----------------------------------")
        print(f"PRED: \t{pred.res and list(map(lambda p: list(p), pred.res))}")
        print(f"GOLD: \t{list(map(lambda p: list(p), gold.res))}")
