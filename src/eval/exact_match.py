from src.util.schema_repo import DatabaseSchemaRepo
from src.eval.column_collector import ColumnCollector
from src.parse.node import SqlAstNode
from src.parse.parser import SqlParser

parser = SqlParser()


class ExactMatchParser:
    def __init__(self, tables_json_path):
        self.parser = SqlParser()
        self.db_repo = DatabaseSchemaRepo(tables_json_path)

    def parse(self, sql: str, db_id: str) -> SqlAstNode:
        db_schema = self.db_repo.dbs[db_id]
        column_collector = ColumnCollector(db_schema)
        ast = parser.parse(sql)
        if ast:
            # draw_graph(ast, "graph")
            ast.db_schema = db_schema
            ast.accept(column_collector)
        return ast
