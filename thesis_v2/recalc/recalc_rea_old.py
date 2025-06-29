import asyncio
import os.path
from dataclasses import dataclass
from itertools import product

import pandas as pd
import tqdm

from src.configs.datasets import SPIDER_ALL, BIRD_SMALL, BIRD_ALL, BEAVER_ALL
from src.eval.metrics import RelaxedExecAcc, NewRelaxedExecAcc
from src.util.async_utils import apply_async
from src.util.file_utils import read_json
from src.util.log_util import configure_logging

configure_logging()

df = pd.read_csv("thesis_v2/thesis_scores_v2.csv")

preds_dir = "thesis_v2/pred_data"

models = list(df["model"].unique())
print("Models:", models)

itrs = list(df["itr"].unique())
print("Itrs:", itrs)

tmps = list(df["tmp"].unique())
print("Tmps:", tmps)

dsts = list(df["dst"].unique())
print("Dsts:", dsts)

dst_idxs = df[["model", "itr", "tmp", "dst", "ds_idx"]].groupby(["model", "dst", "tmp", "itr"]).max().to_dict()[
    "ds_idx"]

GOLD_DATASETS = {
    "spider": SPIDER_ALL,
    "bird": BIRD_ALL,
    "beaver": BEAVER_ALL
}

id_tuples = product(models, dsts, tmps, itrs)


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


def load_golds():
    golds_dict = {}
    for ds in dsts:
        data = read_json(GOLD_DATASETS[ds].get_test_path())
        gold_sqls = list(map(lambda x: (x['db_id'], x["query"]), data))
        golds_dict[ds] = gold_sqls
    return golds_dict


golds = load_golds()


def load_preds():
    preds_dict = {}
    for id_tuple in id_tuples:
        print("Loading", id_tuple)
        model, ds, tmp, itr = id_tuple
        max_id = dst_idxs[id_tuple]
        model_ds_dir = os.path.join(preds_dir, f"{model}_{ds}_all", "pred")
        pred_file = os.path.join(model_ds_dir, f"pred_{tmp}_{itr}.txt")
        pred_sqls = read_file(pred_file)
        assert len(pred_sqls) == max_id + 1
        assert len(pred_sqls) == len(golds[ds])
        preds_dict[id_tuple] = pred_sqls
    return preds_dict


def get_gold_sql(dp: Datapoint) -> str:
    return golds[dp.dst][dp.dst_idx]


preds = load_preds()


def get_pred_sql(dp: Datapoint) -> str:
    return preds[dp.id_tuple][dp.dst_idx]


# df = df.head(50)

rea_dict = {
    "spider": RelaxedExecAcc("rea", SPIDER_ALL),
    "bird": RelaxedExecAcc("bird", BIRD_ALL),
    "beaver": RelaxedExecAcc("beaver", BEAVER_ALL)
}

print(len(df))
print(df[['model', 'ea']].groupby('model').mean())
print(df[['model', 'rea']].groupby('model').mean())

calc_data = []
for idx, row in tqdm.tqdm(df.iterrows(), total=len(df)):
    dp = Datapoint.from_dict(row.to_dict())
    db_id, gold_sql = get_gold_sql(dp)
    pred_sql = get_pred_sql(dp)
    calc_data.append([dp.dst, db_id, gold_sql, pred_sql])
    # df.at[idx, 'rea'] = rea.calc(gold_sql, pred_sql, db_id)


async def calc(tup):
    dst, db_id, gold_sql, pred_sql = tup
    rea = rea_dict[dst]
    res = rea.calc(gold_sql, pred_sql, db_id)
    return res


results = asyncio.run(apply_async(calc, calc_data))

for idx, row in tqdm.tqdm(df.iterrows(), total=len(df)):
    df.at[idx, 'rea'] = results[idx]
print("-" * 10)
print(df[['model', 'ea']].groupby('model').mean())
print(df[['model', 'rea']].groupby('model').mean())

df.to_csv("thesis_v2/recalc/rea_old.csv")
