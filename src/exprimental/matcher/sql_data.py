from dataclasses import dataclass
from typing import Iterable, Tuple, Optional

from src.sql_parser.node import SqlAstNode


@dataclass
class SqlInputData:
    db_id: str
    sql: str

    def to_parsed(self, ast: SqlAstNode):
        return SqlParsedData(db_id=self.db_id, sql=self.sql, ast=ast)


@dataclass
class SqlParsedData(SqlInputData):
    ast: SqlAstNode

    def to_result(self, res: Iterable[Tuple]):
        return SqlExecResult(db_id=self.db_id, sql=self.sql, ast=self.ast, res=res)


@dataclass
class SqlExecResult(SqlParsedData):
    res: Optional[Iterable[Tuple]]
