import os

import pandas as pd
import tqdm

from src.cat.catter import Catter
from src.util.file_utils import write_json, read_json
from src.util.log_util import configure_logging

configure_logging()

models = ["din", "dail"]
dss = ["spider", "bird", "beaver"]
iters = 3
tmp = 0.2

pred_data_dir = "pred_data"
gold_data_dir = "gold_data"


def read_pred_data():
    pred_data = dict()
    for ds in dss:
        ds_pred_data = dict()
        for model in models:
            ds_pred_data[model] = []
            for i in range(iters):
                pred_path = os.path.join(pred_data_dir, f"{model}_{ds}_all", "pred", f"pred_{tmp}_{i}.txt")
                with open(pred_path) as f:
                    data = f.readlines()
                    ds_pred_data[model].append(data)
        pred_data[ds] = ds_pred_data
    return pred_data


def read_gold_data():
    gold_data = dict()
    for ds in dss:
        gold_data[ds] = read_json(f'{gold_data_dir}/{dss[0]}.data.test.json')
    return gold_data


df = pd.read_csv("thesis_scores.csv")
pred_data = read_pred_data()
gold_data = read_gold_data()

model = "din"
itr = 0
catter = Catter()

errs = 0
new_rows = []
for i, row in tqdm.tqdm(df.iterrows(), total=len(df)):
    row_dict = row.to_dict()
    ds = row_dict['dst']
    ds_idx = row_dict['ds_idx']
    itr = row_dict['itr']
    tmp = row_dict['tmp']
    pred_sql = pred_data[ds][model][itr][ds_idx]
    gold_sql = gold_data[ds][ds_idx]['query']
    print("#" * 100)
    print("Gold", gold_sql)
    print("Pred", pred_sql)
    try:
        cat = catter.get_category(pred_sql)
        sub = catter.get_sub_category(pred_sql)
        print("cat", cat, "sub", sub)
        row_dict['pcat'] = cat.name
        row_dict['psub'] = sub.name
    except Exception as e:
        print("ERROR", e)
        print(gold_sql)
        print(pred_sql)
        row_dict['pcat'] = ""
        row_dict['psub'] = ""
        errs += 1
    new_rows.append(row_dict)

print("NUM ERRS", errs)
df = pd.DataFrame(new_rows)
df.to_csv(f'catted.csv', index=False)
