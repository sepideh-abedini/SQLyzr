from abc import abstractmethod, ABC

from src.analyzer.sql_data import SqlParsedData


class SqlTransformer(ABC):
    @abstractmethod
    def transform_sql(self, pred: SqlParsedData, gold: SqlParsedData) -> (SqlParsedData, SqlParsedData):
        pass

    @property
    @abstractmethod
    def msg(self) -> str:
        pass

    def __eq__(self, other):
        return type(self) == type(other)

    def __hash__(self):
        return hash(type(self).__name__)

