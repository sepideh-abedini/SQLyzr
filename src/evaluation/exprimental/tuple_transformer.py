from abc import ABC, abstractmethod
from typing import Tuple, List

from src.evaluator.db_facade import DatabaseFacade


class TupleTransformer(ABC):
    def transform_tuple(self, t: Tuple) -> Tuple:
        return t

    def transform(self, tuples: List[Tuple]) -> List[Tuple]:
        return list(map(self.transform_tuple, tuples))


class ReverseTransformer(TupleTransformer):
    def transform_tuple(self, t: Tuple) -> Tuple:
        return t[::-1]


class SortTransformer(TupleTransformer):
    def transform(self, tuples: List[Tuple]) -> List[Tuple]:
        return sorted(tuples)


class PredEvaluator:
    def __init__(self, dbs_dir):
        self.db_facade = DatabaseFacade(dbs_dir)

    def get_results(self, db_id: str, gold_sql: str, pred_sql: str):
        gold_res = self.db_facade.execute_query(db_id, gold_sql)
        pred_res = self.db_facade.execute_query(db_id, pred_sql)
        return gold_res, pred_res

    def eval(self, db_id: str, gold_sql: str, pred_sql: str):
        gold_res, pred_res = self.get_results(db_id, gold_sql, pred_sql)
        return gold_res == pred_res


class TransformerEvaluator(PredEvaluator):
    transformers: List[TupleTransformer]

    def __init__(self, dbs_dir):
        super().__init__(dbs_dir)
        self.transformers = [
            ReverseTransformer(),
            SortTransformer()
        ]

    def eval(self, db_id: str, gold_sql: str, pred_sql: str):
        gold_res, pred_res = self.get_results(db_id, gold_sql, pred_sql)
        if gold_res is None or pred_res is None:
            return gold_res == pred_res
        for transformer in self.transformers:
            t_pred_res = transformer.transform(pred_res)
            if gold_res == t_pred_res:
                print(f"Match with transformer: {transformer.__class__.__name__}")
                return True
        return False
