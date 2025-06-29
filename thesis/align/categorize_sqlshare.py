import pandas as pd
import tqdm

from src.cat.catter import Catter
from src.parse.parser import SqlParser
from src.util.log_util import configure_logging

configure_logging()

with open("sqlshare.txt", 'r') as f:
    content = f.read()

sqls = content.split("\n")

parser = SqlParser()
catter = Catter()
c = 0

rows = []
with open("errors.txt", 'w') as f:
    for sql in tqdm.tqdm(sqls, total=len(sqls)):
        ast = parser.parse(sql)
        cat, sub = catter.categorize(sql)
        rows.append({
            'sql': sql,
            'cat': cat.name,
            'sub': sub.name
        })
        if not ast:
            c += 1
            f.write(sql + "\n")
    print(c)
    print(len(sqls))

df = pd.DataFrame(rows)
df.to_csv("new_sqlshare_cats_v2.csv")
