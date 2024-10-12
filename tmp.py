from src.dbutil.schema_repo import DatabaseSchemaRepo
from src.prop_collectors.column_collector import ColumnCollector
from src.sql_parser.parser import SqlParser

s = "SELECT name FROM singer"
sql_parser = SqlParser()
ast = sql_parser.parse(s)

table_json = "data/datasets/spider/tables.json"
db_repo = DatabaseSchemaRepo(table_json)
db_schema = db_repo.dbs['concert_singer']
visitor = ColumnCollector(db_schema)
result = ast.accept(visitor)
print(result)