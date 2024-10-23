import json
import re
from lib import remove_all_nested_queries, get_where_clause, get_where_clause_operators, get_db_id

path = "dev.json"

sql = "select * from bar where x in ( select count ( * ) from baz )"

tokens = ["select", "*","from","perpetrator", "where", "location", "=", "tehran"]

x = remove_all_nested_queries(tokens)
where_clause = get_where_clause(x)
where_clause_operators = get_where_clause_operators(where_clause)
db_id = get_db_id(tokens)
print(db_id)
    
# tokens = tokenize(sql)

# with open (path, 'r') as f:
#     values = json.load(f)
#     #sql_toks = values["query_toks"]
#     if "WHERE" in toks:
#         tags.append("sp+filtering")
#         index = toks.index("WHERE")
#         where_toks = toks[index:]
        
        
        
        
     