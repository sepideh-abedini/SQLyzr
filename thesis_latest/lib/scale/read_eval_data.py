import os.path

import pandas as pd

from src.configs.datasets import SPIDER_ALL
from src.util.file_utils import read_json

models = ["din", "dail"]
iters = 3
tmp = 0.2


def read_pred_data(pred_dir):
    pred_data = dict()
    for model in models:
        pred_data[model] = []
        for i in range(iters):
            pred_path = os.path.join(pred_dir, f"{model}_spider_all", "pred", f"pred_{tmp}_{i}.txt")
            with open(pred_path) as f:
                data = f.readlines()
                pred_data[model].append(data)
    return pred_data


def read_eval_data(input_file, pred_dir):
    expr_data = pd.read_csv(input_file)

    gold_data = read_json(SPIDER_ALL.get_test_path())

    pred_data = read_pred_data(pred_dir)

    eval_data = []

    for index, row in expr_data.iterrows():
        model = row['model']
        ds_idx = row['ds_idx']
        ds_idx = int(ds_idx.replace("spider", ""))
        gold_row = gold_data[ds_idx]
        db_id = gold_row['db_id']
        gold_sql = gold_row['query']
        itr = int(row['itr'])
        pred_sql = pred_data[model][itr][ds_idx]

        new_row = {
            "model": model,
            "ds_idx": ds_idx,
            "itr": itr,
            "db_id": db_id,
            "gold": gold_sql,
            "pred": pred_sql,
            "cat": row['cat'],
            "sub": row['sub'],
            "plc": row['plc'],
            "dst": row['dst'],
            "tmp": row['tmp'],
        }
        eval_data.append(new_row)

        print("#" * 100)
        print("GOLD:", gold_sql)
        print("PRED:", pred_sql)

    return eval_data
