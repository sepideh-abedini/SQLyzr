import re
from abc import ABC, abstractmethod

from src.exprimental.col_collector import ColCollector
from src.exprimental.col_corrector import ColCorrector

from src.exprimental.matcher.sql_data import SqlParsedData, SqlInputData
from src.exprimental.matcher.sql_processor import SqlMatchingProcessor
from src.exprimental.terminal_visitor import ValueCollector


class SqlTransformer(SqlMatchingProcessor, ABC):
    @abstractmethod
    def transform_sql(self, pred: SqlParsedData, gold: SqlParsedData) -> (SqlParsedData, SqlParsedData):
        pass

    def __str__(self):
        return self.__class__.__name__


class LimitRemoverTransformer(SqlTransformer):
    def delete_limit(self, sql: str) -> str:
        return re.sub(r'(.*)limit\s*([^\s]*)(.*)', r"\1\3", sql, flags=re.IGNORECASE)

    def transform_sql(self, pred: SqlParsedData, gold: SqlParsedData) -> (SqlParsedData, SqlParsedData):
        pred.sql = self.delete_limit(pred.sql)
        gold.sql = self.delete_limit(gold.sql)
        return pred, gold


def str_match(s1: str, s2: str):
    return s1.lower() == s2.lower()


def find_literal_matching(pred: SqlParsedData, gold: SqlParsedData):
    visitor = ValueCollector()
    if gold.ast is None or pred.ast is None:
        return None
    gold_vals = gold.ast.accept(visitor)
    pred_vals = pred.ast.accept(visitor)
    matching = {}
    for pred_val in pred_vals:
        for gold_val in gold_vals:
            if str_match(pred_val, gold_val):
                matching[pred_val] = gold_val
            elif pred_val not in matching:
                matching[pred_val] = None
    if len(matching.values()) == len(pred_vals):
        # if len(matching.values()) > 0:
        #     print(f"Full literal matching found:{matching}")
        return matching
    else:
        # if len(matching.values()) > 0:
        #     print(f"Partial literal matching found:{matching}")
        return None


class LiteralCorrectorTransformer(SqlTransformer):
    def transform_sql(self, pred: SqlParsedData, gold: SqlParsedData) -> (SqlParsedData, SqlParsedData):
        matching = find_literal_matching(pred, gold)
        if matching:
            refined_sql = pred.sql
            for pred_val, gold_val in matching.items():
                if gold_val is not None:
                    refined_sql = refined_sql.replace(pred_val, gold_val)
            pred.sql = refined_sql
        return pred, gold


class ColCorrectorTransformer(SqlTransformer):
    def transform_sql(self, pred: SqlParsedData, gold: SqlParsedData) -> (SqlParsedData, SqlParsedData):
        if not pred.ast or not gold.ast:
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
