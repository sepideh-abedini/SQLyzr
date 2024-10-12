from evaluator.din_evaluator import db_name
from sql_parser.node import SqlAstNode
from src.dbutil.schema_repo import DatabaseSchemaRepo
from src.prop_collectors.column_collector import ColumnCollector
from src.sql_parser.parser import SqlParser

parser = SqlParser()




a1 = "SELECT strftime(name) from stadium"
# b1 = "SELECT t2.stadium_id from concert as t2 join stadium"

# a1 = "SELECT 'Free Meal Count (Ages 5-17)' / 'Enrollment (Ages 5-17)' FROM frpm WHERE 'Educational Option Type' = 'Continuation School' AND 'Free Meal Count (Ages 5-17)' / 'Enrollment (Ages 5-17)' IS NOT NULL ORDER BY 'Free Meal Count (Ages 5-17)' / 'Enrollment (Ages 5-17)' ASC LIMIT 3"



a2 = "select T1.first_name,T1.last_name from Professionals as T1 join Treatments as T2 on T1.professional_id = T2.professional_id where T2.cost_of_treatment < (select avg(cost_of_treatment) from Treatments)"
b2 = "SELECT T1.first_name,T1.last_name FROM Professionals AS T1 JOIN Treatments AS T2 WHERE cost_of_treatment  <  ( SELECT avg(cost_of_treatment) FROM Treatments )"


class ExactMatchParser:
    def __init__(self):
        self.parser = SqlParser()
        tables_json_path = "data/datasets/spider/tables.json"
        self.db_repo = DatabaseSchemaRepo(tables_json_path)

    def parse(self, sql: str, db_id: str) -> SqlAstNode:
        db_schema = self.db_repo.dbs[db_id]
        column_collector = ColumnCollector(db_schema)
        ast = parser.parse(sql)
        ast.db_schema = db_schema
        ast.accept(column_collector)
        return ast


if __name__ == "__main__":

    db_id = "concert_singer"
    # eparser = ExactMatchParser()
    parser = SqlParser()
    #
    # ast = parser.parse("SELECT School FROM (SELECT T2.School,T1.AvgScrRead, RANK() OVER (PARTITION BY T2.County ORDER BY T1.AvgScrRead DESC) AS rnk FROM satscores AS T1 INNER JOIN schools AS T2 ON T1.cds = T2.CDSCode WHERE T2.Virtual = 'F') ranked_schools WHERE rnk <= 5")
    ast = parser.parse("SELECT a * 2 FROM b")
    # ast1 = eparser.parse(a1, db_id)
    # ast2 = eparser.parse(b1, db_id)
    #
    # print(ast1 == ast2 or ast2 == ast1)
# get head of AST Node created for each pred and gold sql

# gold_ast_root = parser.parse(n1)
# res = gold_ast_root.accept(visitor)
# print(res)
# res = gold_ast_root.accept(column_collector)
# print(res)
# pred_ast_root = parser.parse(n2)
# pred_ast_root.accept(column_collector)

# visitor = ColVisitor()
# # defining visitor on each gold and pred AST Node tree
# gold_cols = gold_ast_root.accept(visitor)
# pred_cols = pred_ast_root.accept(visitor)

# print(gold_ast_root.__hash__())

# print(gold_ast_root == pred_ast_root or pred_ast_root == gold_ast_root)

# draw_graph(gold_ast_root, "gold.png")
# draw_graph(pred_ast_root, "pred.png")


# s = "select c from t where x > 2 AND y > 2"
# ast = parser.parse(s)
# e = ast.select_cores[0].where_clause.expr
# print(e)


