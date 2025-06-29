import os
from dataclasses import dataclass
from itertools import product
from typing import Callable

import pandas as pd
import tqdm

from src.configs.datasets import SPIDER_ALL, BIRD_ALL, BEAVER_ALL
from src.util.file_utils import read_json

PREDS_DIR = "thesis_latest/data/pred_data"
GOLDS_DIR = "thesis_latest/data/gold_data"

GOLD_DATASETS = {
    "spider": SPIDER_ALL,
    "bird": BIRD_ALL,
    "beaver": BEAVER_ALL
}


@dataclass
class Datapoint:
    dst: str
    dst_idx: int
    itr: int
    model: str
    tmp: float

    @staticmethod
    def from_dict(d: dict) -> 'Datapoint':
        dst = d['dst']
        ds_idx = d['ds_idx']
        itr = d['itr']
        model = d['model']
        tmp = d['tmp']
        dp = Datapoint(dst=dst, dst_idx=ds_idx, itr=itr, model=model, tmp=tmp)
        return dp

    @property
    def id_tuple(self):
        return self.model, self.dst, self.tmp, self.itr


def read_file(p):
    with open(p, "r") as f:
        return f.readlines()


def load_golds(dsts):
    golds_dict = {}
    for ds in dsts:
        data = read_json(GOLD_DATASETS[ds].get_test_path())
        gold_sqls = list(map(lambda x: (x['db_id'], x["query"]), data))
        golds_dict[ds] = gold_sqls
    return golds_dict


def load_preds(id_tuples, max_dst_idxs, golds_dict):
    preds_dict = {}
    for id_tuple in id_tuples:
        print("Loading", id_tuple)
        model, ds, tmp, itr = id_tuple
        max_id = max_dst_idxs[id_tuple]
        model_ds_dir = os.path.join(PREDS_DIR, f"{model}_{ds}_all", "pred")
        pred_file = os.path.join(model_ds_dir, f"pred_{tmp}_{itr}.txt")
        pred_sqls = read_file(pred_file)
        assert len(pred_sqls) == max_id + 1
        assert len(pred_sqls) == len(golds_dict[ds])
        preds_dict[id_tuple] = pred_sqls
    return preds_dict


def get_gold_sql(golds_dict, dp: Datapoint) -> str:
    return golds_dict[dp.dst][dp.dst_idx]


def get_pred_sql(preds_dict, dp: Datapoint) -> str:
    return preds_dict[dp.id_tuple][dp.dst_idx]


def load_scores(scores_file):
    df = pd.read_csv(scores_file)
    models = list(df["model"].unique())
    print("Models:", models)
    itrs = list(df["itr"].unique())
    print("Itrs:", itrs)
    tmps = list(df["tmp"].unique())
    print("Tmps:", tmps)
    dsts = list(df["dst"].unique())
    print("Dsts:", dsts)

    max_dst_idxs = df[["model", "itr", "tmp", "dst", "ds_idx"]].groupby(["model", "dst", "tmp", "itr"]).max().to_dict()[
        "ds_idx"]

    id_tuples = product(models, dsts, tmps, itrs)

    golds_dict = load_golds(dsts)

    preds_dict = load_preds(id_tuples, max_dst_idxs, golds_dict)

    return golds_dict, preds_dict


def process_scores(scores_file: str, processor: Callable[[str, str, str], str], col: str, out_file: str):
    golds_dict, preds_dict = load_scores(scores_file)

    df = pd.read_csv(scores_file)
    for idx, row in tqdm.tqdm(df.iterrows(), total=len(df)):
        dp = Datapoint.from_dict(row.to_dict())
        db_id, gold_sql = get_gold_sql(golds_dict, dp)
        pred_sql = get_pred_sql(preds_dict, dp)
        new_val = processor(db_id, pred_sql, gold_sql)
        df.at[idx, col] = new_val

    df.to_csv(out_file)
