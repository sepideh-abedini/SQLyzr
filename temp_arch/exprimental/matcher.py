from dataclasses import dataclass, replace
from typing import Tuple, Iterable

import pandas as pd

from src.evaluation.evaluator.exact_match import ExactMatchParser
from src.exprimental.col_collector import ColCollector
from src.exprimental.col_corrector import ColCorrector
from src.exprimental.db_facade import DatabaseFacade
from src.sql_parser.node import SqlAstNode
from src.visitor.str_visitor import StringVisitor


@dataclass
class ResultMatcher:
    in_file: str
    db_dir: str

    def __init__(self, in_file, db_dir):
        self.in_file = in_file
        self.db_dir = db_dir
        self.parser = ExactMatchParser("data/spider/tables.json")
        self.db_facade = DatabaseFacade(self.db_dir)
        self.string_visitor = StringVisitor()

    def correct_cols(self, pred: SqlData, gold: SqlData):
        if not pred.ast:
            return pred, gold
        col_visitor = ColCollector()
        gold_cols = gold.ast.accept(col_visitor)
        pred_cols = pred.ast.accept(col_visitor)
        cand_cols = gold_cols - pred_cols
        col_corrector = ColCorrector(pred.ast.db_schema, cand_cols)
        col_corrections = pred.ast.accept(col_corrector)
        refined_sql = pred.sql
        # if len(col_corrections.items()) > 0:
        #     print(f"CORRECTING COLUMNS: {col_corrections}")
        for wrong_col, correct_col in col_corrections.items():
            refined_sql = refined_sql.replace(wrong_col, correct_col)
        pred.sql = refined_sql
        return pred, gold

    def refine_sql(self, pred: SqlData, gold: SqlData):
        pred, gold = self.replace_literals_with_gold(pred, gold)
        pred, gold = self.delete_limit(pred, gold)
        return pred, gold

    def get_result_data(self, db_id: str, sql: str) -> SqlData:
        ast = self.parser.parse(sql, db_id)
        res = self.db_facade.execute_query(db_id, sql)
        return SqlData(sql, ast, res)

    def run(self):
        runtime_errors = 0
        df = pd.read_csv(self.in_file, index_col=0)
        match = 0
        total = 0
        for idx, row in df.iterrows():
            total += 1
            db_id = row["DATABASE"]
            pred_sql = row["PREDICTED SQL"]
            gold_sql = row["GOLD SQL"]

            pred = self.get_result_data(db_id, pred_sql)
            gold = self.get_result_data(db_id, gold_sql)

            pred, gold = self.refine_sql(pred, gold)

            pred = self.get_result_data(db_id, pred.sql)
            gold = self.get_result_data(db_id, gold.sql)

            if self.match(pred, gold):
                match += 1
                continue

            pred, gold = self.correct_cols(pred, gold)

            pred = self.get_result_data(db_id, pred.sql)
            gold = self.get_result_data(db_id, gold.sql)

            if pred.res is None:
                runtime_errors += 1

            if self.match(pred, gold):
                match += 1
            else:
                print(f"idx = {idx}")
                print(f"nl = \"{row['NLQ']}\"")
                print(f"db_id = \"{db_id}\"")
                print(f"org_pred = \"{pred_sql}\"")
                print(f"org_gold = \"{gold_sql}\"")
                print(f"pred = \"{pred.sql}\"")
                print(f"gold = \"{gold.sql}\"")
                print("-----------------------------------")
                print(f"PRED: \t{pred.res and list(map(lambda p: list(p), pred.res))}")
                print(f"GOLD: \t{list(map(lambda p: list(p), gold.res))}")
                print("#################################\n")
        print(runtime_errors)
        return match, total

    def match(self, pred: SqlData, gold: SqlData):
        return pred.res == gold.res
