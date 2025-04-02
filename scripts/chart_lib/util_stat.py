import numpy as np
import pandas as pd

from src.util.model_utils import read_jsonl


def find_starts(d):
    starts = [0]
    for i in range(1, len(d) - 1):
        prev = d.iloc[i - 1]
        cur = d.iloc[i]
        nxt = d.iloc[i + 1]
        if prev['ct'] > cur['ct']:
            starts.append(cur['ts'])
    return starts


def proc_df(path: str):
    data = read_jsonl(path)
    rows = []
    for row in data:
        ts = row['record']['time']['timestamp']
        ts = int(ts)
        util = row['record']['extra']['util']
        rows.append({"ts": ts, 'ct': util['cpu_time'], 'cp': util['cpu'], 'mem': util['mem']})
    df = pd.DataFrame(rows)
    df['ts'] = df['ts'] - df['ts'].min()
    df['cc'] = df['cp'] / 100
    df['ct'] = df['ct'].apply(np.ceil)
    df['ctd'] = df['ct'].diff()
    df['ctd'] = df['ctd'].clip(lower=0)
    return df


def get_util_stats(model):
    df = proc_df(f"data/{model}_bird_logs/util.jsonl")
    timing_df = pd.read_csv(f"charts/{model}_timing.csv")
    starts = find_starts(df)
    stats = dict()
    pre = timing_df.groupby(["tmp", "itr"]).sum()
    cts = df[df['ts'].isin(starts)]['ct']
    stats['Total CPU Time'] = cts.sum() / 9
    stats['Max Mem'] = df['mem'].max()
    stats['Max cores'] = df['cc'].max()
    stats['Max cpu percentage'] = df['cp'].max()
    stats['Total Time'] = pre['time'].mean()
    stats['Model'] = model
    return stats


din_stats = get_util_stats("din")
dail_stats = get_util_stats("dail")

df = pd.DataFrame([din_stats, dail_stats])
df.to_csv("charts/util_stats.csv")
