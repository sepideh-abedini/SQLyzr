from evaluator.din_evaluator import db_name
from sql_parser.node import SqlAstNode
from src.dbutil.schema_repo import DatabaseSchemaRepo
from src.prop_collectors.column_collector import ColumnCollector
from src.sql_parser.parser import SqlParser

parser = SqlParser()




gold1 = "SELECT count(*) FROM student AS T1 JOIN has_pet AS T2 ON T1.stuid  =  T2.stuid JOIN pets AS T3 ON T2.petid  =  T3.petid WHERE T1.sex  =  'F' AND T3.pettype  =  'dog'"
pred1 = "select count(*) from Student as T1 join Has_Pet as T2 on T1.StuID = T2.StuID join Pets as T3 on T2.PetID = T3.PetID where T3.PetType = 'terminal' Or T1.Sex = 'terminal'"


g = "SELECT CAST((SELECT COUNT(T1.atom_id) FROM connected AS T1 INNER JOIN bond AS T2 ON T1.bond_id = T2.bond_id GROUP BY T2.bond_type ORDER BY COUNT(T2.bond_id) DESC LIMIT 1 ) AS REAL) * 100 / ( SELECT COUNT(atom_id) FROM connected )"


gold2= "SELECT major ,  age FROM student WHERE stuid NOT IN (SELECT T1.stuid FROM student AS T1 JOIN has_pet AS T2 ON T1.stuid  =  T2.stuid JOIN pets AS T3 ON T3.petid  =  T2.petid WHERE T3.pettype  =  'cat')"
pred2= "select Age,Major from Student where StuID not in (select T1.StuID from Student as T1 join Has_Pet as T2 on T1.StuID = T2.StuID join Pets as T3 on T2.PetID = T3.PetID where T3.PetType = 'terminal')"

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

    db_id = "pets_1"
    eparser = ExactMatchParser()
    parser = SqlParser()
    #
    # ast = parser.parse("SELECT School FROM (SELECT T2.School,T1.AvgScrRead, RANK() OVER (PARTITION BY T2.County ORDER BY T1.AvgScrRead DESC) AS rnk FROM satscores AS T1 INNER JOIN schools AS T2 ON T1.cds = T2.CDSCode WHERE T2.Virtual = 'F') ranked_schools WHERE rnk <= 5")
    #ast = parser.parse("SELECT a * 2 FROM b")
    # ast1 = eparser.parse(gold1, db_id)
    # ast2 = eparser.parse(pred1, db_id)
    ast2 = parser.parse(g)
    # print(ast1 == ast2 or ast2 == ast1)
    # ast2 = eparser.parse(pred1, db_id)

    # ast1 = parser.parse(gold2)
    # ast2 = parser.parse(pred2)
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


