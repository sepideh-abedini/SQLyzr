from evaluator.din_evaluator import db_name
from sql_parser.node import SqlAstNode
from src.dbutil.schema_repo import DatabaseSchemaRepo
from src.prop_collectors.column_collector import ColumnCollector
from src.sql_parser.parser import SqlParser

parser = SqlParser()


class ExactMatchParser:
    def __init__(self, tables_json_path):
        self.parser = SqlParser()
        self.db_repo = DatabaseSchemaRepo(tables_json_path)

    def parse(self, sql: str, db_id: str) -> SqlAstNode:
        db_schema = self.db_repo.dbs[db_id]
        column_collector = ColumnCollector(db_schema)
        ast = parser.parse(sql)
        ast.db_schema = db_schema
        ast.accept(column_collector)
        return ast


# if __name__ == "__main__":

    # db_id = "concert_singer"
    # eparser = ExactMatchParser()
    # parser = SqlParser()
    #
    # ast = parser.parse("SELECT School FROM (SELECT T2.School,T1.AvgScrRead, RANK() OVER (PARTITION BY T2.County ORDER BY T1.AvgScrRead DESC) AS rnk FROM satscores AS T1 INNER JOIN schools AS T2 ON T1.cds = T2.CDSCode WHERE T2.Virtual = 'F') ranked_schools WHERE rnk <= 5")
    #ast = parser.parse("SELECT a * 2 FROM b")
    # ast1 = eparser.parse(a, db_id)
    # ast2 = eparser.parse(b, db_id)
    # ast2 = parser.parse(b)
    # print(ast1 == ast2 or ast2 == ast1)
    # ast2 = eparser.parse(pred1, db_id)

    # ast1 = parser.parse(gold2)
    # ast2 = parser.parse(pred2)
    #
    # print(ast1 == ast2 or ast2 == ast1)
