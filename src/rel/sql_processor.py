from abc import ABC, abstractmethod

from src.rel.sql_data import SqlExecResult


class SqlMatchingProcessor(ABC):
    @abstractmethod
    def msg(self) -> str:
        pass

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.__class__.__name__


class ResultMatcher(SqlMatchingProcessor, ABC):
    @abstractmethod
    def check_res(self, pred: SqlExecResult, gold: SqlExecResult) -> bool:
        pass
