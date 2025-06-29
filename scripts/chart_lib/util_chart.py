import os.path

import numpy as np
import pandas as pd
import seaborn as sns
from dataclasses_json.stringcase import snakecase
from matplotlib import pyplot as plt

from src.util.model_utils import read_jsonl


def get_range(d, start, end):
    return d[(d['ts'] >= start) & (d['ts'] <= end)].copy()


def draw_line(d, metric, label, title, sub_dir):
    plt.figure(figsize=(30, 6))
    sns.lineplot(data=d, x="ts", y=metric)
    plt.title(title)
    plt.locator_params(axis='x', nbins=30)
    plt.ylabel(label)
    plt.xlabel("Time (Seconds)")
    plt.savefig(os.path.join(sub_dir, snakecase(title)), dpi=600)
    plt.show()


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


METRIC_LABELS = {
    "ct": {
        "title": "{} CPU Time {}",
        "label": "CPU Time (Seconds)"
    },
    "cp": {
        "title": "{} CPU Usage Percentage {}",
        "label": "CPU Usage Percentage"
    },
    "ctd": {
        "title": "{} CPU Time Diff {}",
        "label": "CPU Time Diff (Seconds)"
    },
    "cc": {
        "title": "{} Number of Cores {}",
        "label": "Number of Cores"
    },
    "mem": {
        "title": "{} Memory Usage {}",
        "label": "Memory Usage (MB)"
    }
}


def draw_model_util_charts(model: str):
    df = proc_df(f"data/{model}_bird_logs/util.jsonl")
    model_dir = os.path.join("out/dec31/charts", "util", model)
    os.makedirs(model_dir, exist_ok=True)
    starts = find_starts(df)
    for metric in ["ct", "cp", "ctd", "cc", "mem"]:
        metric_dir = os.path.join(model_dir, metric)
        os.makedirs(metric_dir, exist_ok=True)
        draw_line(df, metric, METRIC_LABELS[metric]["label"], METRIC_LABELS[metric]["title"].format(model, ""),
                  model_dir)
        for i in range(1, len(starts)):
            start = starts[i - 1]
            end = starts[i]
            sub_df = get_range(df, start, end - 1)
            sub_df['ts'] -= sub_df['ts'].min()
            draw_line(sub_df, metric, METRIC_LABELS[metric]["label"], METRIC_LABELS[metric]["title"].format(model, i),
                      metric_dir)


draw_model_util_charts("din")
draw_model_util_charts("dail")
