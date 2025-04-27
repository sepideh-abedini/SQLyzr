import re

from tqdm import tqdm

from src.parse.parser import SqlParser
from src.util.str_utils import shrink_whitespaces

data_dir = 'data/sqlshare_data_release/'
# Read the file
with open(data_dir + "queries.non_comment.txt", 'r') as f:
    content = f.read()


def remove_big_comments(sql):
    pat = re.compile(r"(.*)/\*(.*)\*/(.*)$")
    if re.search(pat, sql):
        sql = re.sub(pat, r'\1 \2', sql)
    return sql


sql_queries = [query.strip() for query in re.split(r'\n_+\n', content) if query.strip()]

sql_queries = list(map(lambda query: shrink_whitespaces(query), sql_queries))
sql_queries = list(map(remove_big_comments, tqdm(sql_queries, total=len(sql_queries))))

with open(data_dir + "queries_clean.txt", 'w') as f:
    f.write("\n".join(sql_queries))

print(len(sql_queries))
# print(sql_queries)

# Print each extracted SQL query
# for i, sql in enumerate(sql_queries, 1):
#     print(f"--- Query {i} ---")
#     print(sql)
#     print()
