from itertools import chain, combinations

from src.analyzer.sql_data import SqlParsedData
from src.analyzer.sql_transformer import SqlTransformer
from src.analyzer.terminal_visitor import ValueCollector


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


class LetterCasingTransformer(SqlTransformer):
    @property
    def msg(self) -> str:
        return "The letter case of the literal values in the SQL query should be changed."

    def transform_sql(self, pred: SqlParsedData, gold: SqlParsedData) -> (SqlParsedData, SqlParsedData):
        matching = find_literal_matching(pred, gold)
        if matching:
            refined_sql = pred.sql
            for pred_val, gold_val in matching.items():
                if gold_val is not None:
                    refined_sql = refined_sql.replace(pred_val, gold_val)
            pred.sql = refined_sql
        return pred, gold


def all_subsets(s: set) -> frozenset[frozenset]:
    subsets = frozenset(chain.from_iterable(
        combinations(s, r) for r in range(len(s) + 1)
    ))
    return subsets


