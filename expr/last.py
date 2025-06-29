import json
import re

from tqdm import tqdm

from src.configs.datasets import BIRD_ALL
from src.rel.db_factory import DatabaseFactory
from src.util.log_util import configure_logging

pred_file = "out/simple_bird_bad_msc/output_stage3.json"
gold_file = "data/bird/data.test.small.bad.json"

dbf = DatabaseFactory.get_instance(BIRD_ALL)

configure_logging()

pred_res = []
with open(pred_file, "r") as f:
    pred_data = json.load(f)
    for pred in pred_data:
        match = re.search(r"/([^/]+)/[^/]+\.sqlite$", pred['db_path'])
        db_id = match.group(1)
        sql = pred['sql_pred']
        sql = sql.strip().replace("\n", " ")
        res = dbf.exec_query_sync(db_id, sql)
        pred_res.append((db_id, sql, res))

gold_res = []
with open(gold_file, "r") as f:
    gold_data = json.load(f)
    for gold in gold_data:
        db_id = gold['db_id']
        sql = gold['query']
        res = dbf.exec_query_sync(db_id, sql)
        gold_res.append((db_id, sql, res))

print(len(pred_res))
print(len(gold_res))

count = 0
gnone = 0
for g in tqdm(gold_res, total=len(gold_res)):
    gres = g[2]
    if gres is None:
        gnone += 1
        continue
    for p in pred_res:
        pres = p[2]
        if pres is None:
            continue
        if p[0] != g[0]:
            continue
        if pres == gres:
            print("-----------------------------")
            print(f"GOLD: {g[0]} -> {g[1]}")
            print(f"PRED: {p[0]} -> {p[1]}")
            print(f"GOLD RES: {gres}")
            print(f"PRED RES: {pres}")
            count += 1
            break

print("GNONE: ", gnone)
print("COUNT: ", count)
