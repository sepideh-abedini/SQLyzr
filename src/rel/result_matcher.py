from abc import ABC, abstractmethod

from src.rel.sql_data import SqlExecResult
from src.rel.sql_processor import SqlMatchingProcessor
from src.rel.tuple_matcher import TupleMatchConf, ListWrapper


class ResultMatcher(SqlMatchingProcessor, ABC):
    @abstractmethod
    def check_res(self, pred: SqlExecResult, gold: SqlExecResult) -> bool:
        pass


class ExactMatcher(ResultMatcher):
    def __init__(self, match_conf: TupleMatchConf = TupleMatchConf()):
        self.match_conf = match_conf

    def __add__(self, other: 'ExactMatcher'):
        if not isinstance(other, ExactMatcher):
            raise ValueError(f"Cannot add {other} to {self}")
        return ExactMatcher(self.match_conf + other.match_conf)

    def msg(self) -> str:
        return "You should fix the query!"

    def check_res(self, pred: SqlExecResult, gold: SqlExecResult) -> bool:
        if pred.res is None:
            return False
        pred_wl = ListWrapper.wrap(pred.res)
        gold_wl = ListWrapper.wrap(gold.res)
        return pred_wl.match(gold_wl, self.match_conf)


class ExtraTupleMatcher(ExactMatcher):
    def __init__(self):
        super().__init__(TupleMatchConf(ignore_extra_tuple=True))

    def msg(self) -> str:
        return "The predicted SQL has extra rows in the result set."


class ExtraColumnsMatcher(ExactMatcher):
    def __init__(self):
        super().__init__(TupleMatchConf(ignore_extra_col=True))

    def msg(self) -> str:
        return "The predicted SQL used extra columns that should be removed."


class IgnoreListOrderMatcher(ExactMatcher):
    def __init__(self):
        super().__init__(TupleMatchConf(ignore_tuples_order=True))

    def msg(self) -> str:
        return "The order of rows in the result set should be fixed."


class IgnoreColOrderMatcher(ExactMatcher):
    def __init__(self):
        super().__init__(TupleMatchConf(ignore_col_order=True))

    def msg(self) -> str:
        return "The order of columns in the result set should be fixed."


class MissingColumnsMatcher(ExactMatcher):
    def __init__(self):
        super().__init__(TupleMatchConf(ignore_missing_col=True))

    def msg(self) -> str:
        return "There are missing columns in the predicted SQL query that should be fixed."
