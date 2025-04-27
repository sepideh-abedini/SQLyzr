import re

import matplotlib.pyplot as plt
import pandas as pd
import tqdm

from src.parse.lexer import get_lexer
from src.parse.parser import SqlParser
from src.util.log_util import configure_logging
from src.util.str_utils import shrink_whitespaces
from src.cat.catter import Catter

configure_logging()

data_dir = 'data/sqlshare_data_release/'

with open(data_dir + "trs_manual_fix.txt", 'r') as f:
    content = f.read()

sqls = content.split("\n")

# sql = "SELECT t1.t2 FROM [354].[Gene_Description_and_Methylation_Ratio_Oyster]"
# sql = "SELECT bar FROM [354]"

parser = SqlParser()
catter = Catter()
c = 0

rows = []
with open(data_dir + "errors.txt", 'w') as f:
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
df.to_csv(data_dir + "cats.csv")

# ast = parser.parse(sql)
# print(ast)

# lexer = get_lexer()
#
# lexer.input(sql)
# while True:
#     tok = lexer.token()
#     if not tok:
#         break      # No more input
#     print(tok)


# c = 0
# for sql in sqls:
#     ast = parser.parse(sql)
#     if not ast:
#         c += 1
#
# print(c)
# print(len(sqls))
