import json
import os.path

import pandas as pd
from pandas import DataFrame

from src.configs.config_loader import load_config
from src.gpt.gateway.batch.batch_client import GptBatchClient
from src.util.model_utils import read_jsonl

client = GptBatchClient()


def read_bid(path):
    with open(path) as file:
        return file.read()


data_dir = "data/dail_bird_all/pred"


def get_time_for_file(tmp, itr, file):
    bid = read_bid(os.path.join(data_dir, f"pred_{tmp}_{itr}.txt.{file}.jsonl.bid"))
    batch = client.retrieve_batch(bid)
    return batch.completed_at - batch.created_at


data = read_jsonl("data/dail_bird_logs/timing.jsonl")

timings = dict()

for row in data:
    ts = row['record']['time']['timestamp']
    idx = row['record']['extra']['idx']
    idx_timing = timings.setdefault(idx, dict())
    if "start" in row['record']['extra']:
        idx_timing['start'] = ts
    if "finish" in row['record']['extra']:
        idx_timing['finish'] = ts

df = pd.DataFrame.from_dict(timings, orient="index")
df['diff'] = df['finish'] - df['start']
conf = load_config("confs/dail/dail.bird.all.json")

stats = []

for run_conf in conf.eval_conf.get_run_confs():
    filtered_df = df[df.index.str.contains(f"{run_conf.temp}_{run_conf.itr}") & ~ (df.index.str.contains("GPT"))]
    total_time = filtered_df['diff'].sum()
    stats.append({'tmp': run_conf.temp, 'itr': run_conf.itr, 'time': total_time, "gpt": False})

for run_conf in conf.eval_conf.get_run_confs():
    total_time = 0
    total_time += get_time_for_file(run_conf.temp, run_conf.itr, "sql.in")
    total_time += get_time_for_file(run_conf.temp, run_conf.itr, "sql.in.second")
    stats.append({'tmp': run_conf.temp, 'itr': run_conf.itr, 'time': total_time, "gpt": True})

stats_df = DataFrame(stats)
stats_df.to_csv("charts/dail_timing.csv")
