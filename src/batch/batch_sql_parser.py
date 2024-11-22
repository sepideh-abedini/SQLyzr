from typing import TypedDict, cast, List

from pandas import DataFrame
from tqdm import tqdm

from src.batch.csv_file_processor import CsvFileProcessor
from src.sql_parser.node import SqlAstNode
from src.sql_parser.parser import SqlParser
from src.util.logger import log


class SqlRow(TypedDict):
    id: int
    sql: str
    db_id: str
    question: str


class BatchSqlParser(CsvFileProcessor):
    """
        Input: Csv['db_id', 'sql', 'question']
        Output: List[SqlAstNode]
    """

    def __init__(self, in_path):
        super().__init__(in_path)
        self.sql_parser = SqlParser()

    def process_df(self, df: DataFrame) -> List[SqlAstNode]:
        asts = []
        for _, row in tqdm(df.iterrows(), desc="SqlProcessor"):
            ast = self.get_ast(cast(SqlRow, row))
            asts.append(ast)
        return asts

    def get_ast(self, row: SqlRow) -> SqlAstNode:
        try:
            ast = self.sql_parser.parse(row['sql'])
            ast.db_id = row['db_id']
            ast.id = row['id']
            ast.question = row['question']
            ast.raw_sql = row['sql']
        except Exception as e:
            log(e)
            log(f"Error parsing: {row['db_id']} -> {row['sql']}")
            ast = None
        return ast

    def get_columns(self):
        return ['id', 'db_id', 'sql', 'question']
