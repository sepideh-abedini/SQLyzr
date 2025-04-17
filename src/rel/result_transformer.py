from abc import ABC, abstractmethod
from dataclasses import replace, dataclass

from src.rel.sql_data import SqlExecResult
from src.rel.sql_processor import SqlMatchingProcessor


@dataclass
class ResultTransformer(SqlMatchingProcessor, ABC):
    priority: int = 0

    @abstractmethod
    def transform_result(self, data: SqlExecResult) -> SqlExecResult:
        pass

    def __str__(self):
        return self.__class__.__name__

    def __lt__(self, other):
        return self.priority < other.priority


class IgnoreListOrderTransformer(ResultTransformer):

    def __init__(self):
        super().__init__(2)

    def transform_result(self, data: SqlExecResult) -> SqlExecResult:
        if data.res:
            return replace(data, res=frozenset(data.res))
        return data

    def msg(self) -> str:
        return "The order of rows in the result set should be fixed."


class IgnoreColOrderTransformer(ResultTransformer):
    def __init__(self):
        super().__init__(1)

    def transform_result(self, data: SqlExecResult) -> SqlExecResult:
        if data.res:
            return replace(data, res=list(map(lambda tuple: frozenset(map(lambda col: str(col), tuple)), data.res)))
        return data

    def msg(self) -> str:
        return "The order of columns in the result set should be fixed."
