import re

import tqdm

from src.cat.tag_extractor import TagExtractor
from src.parse.parser import SqlParser
from src.util.log_util import configure_logging

configure_logging()

data_dir = 'data/sqlshare_data_release/'

with open(data_dir + "trs_manual_fix.txt", 'r') as f:
    sqls = f.readlines()

parser = SqlParser()

EX_KEYS = [
    "pivot",
    "insert into",
    "delete from",
    "cross apply",
    "with cube",
    "stuff",
    "option",
    "datetimefromparts",
    "datefromparts",
    "datepart",
    " for "
    "all",
    "update",
    "right(",
    "(values",
    "create view"
]

res = {}


def exclude(sql):
    global res
    for key in EX_KEYS:
        if key in sql.lower():
            res[key] = res.setdefault(key, 0) + 1
            return True
    if "from" not in sql.lower():
        res["from"] = res.setdefault(key, 0) + 1
        return True
    return False


c = 0
failed_parse = []
for i, sql in tqdm.tqdm(enumerate(sqls), total=len(sqls)):
    ast = parser.parse(sql)
    if not ast:
        c += 1
        print(i)
        print(sql)
        failed_parse.append(sql)
print(f"Total:  {len(sqls)}")
print(f"Failed: {c}")

excluded_fails = 0
for sql in failed_parse:
    if exclude(sql):
        excluded_fails += 1
print(f"Excluded: {excluded_fails}")
print(res)
