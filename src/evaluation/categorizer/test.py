from sql_token import SqlToken
import pandas as pd
import json
from input_parser import InputParser
from sql_parser import SqlParser
from sql_statement import process_aliases
from sql_token import IdentifierToken

sql = "select x from bar as b where x = 2"
# sql = "select x ( select y ) intersect select y ( select z )"

# def traverse(state):
#     if len(state.sub_statements) == 0:
#         print(len(state.nested_statements))
#         return 
#     level = 0
#     for s in state.sub_statements:
#         level = max(level, traverse(s))
#     return level


parser = SqlParser()
statement = parser.to_statement(sql)

process_aliases(statement.tokens)


# for t in statement.tokens:
#     if isinstance(t, IdentifierToken):
#         print(t, isinstance(t, SqlToken))
# level = statement.get_nest_level()

# traverse(statement)

# input_parser = InputParser()

# input_parser.load_json("../models/spider/dev.json")
# statements = input_parser.get_statements()

# df = pd.DataFrame(
#     [
#         {
#             'sql': s.get_sql(),
#             'nest_level': s.get_nest_level(),
#             'sub_statements': len(s.sub_statements)
#         }
#         for s in statements
#     ]
# )

# df.to_csv("spider.stats.csv", sep="\t")



