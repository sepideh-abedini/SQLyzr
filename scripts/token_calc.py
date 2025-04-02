import sys

import pandas as pd

from src.configs.config_loader import load_config

conf_path = sys.argv[1]
conf = load_config(conf_path)

rows = []
for run_conf in conf.eval_conf.get_run_confs():
    with open(f"{run_conf.get_pred_path()}.tokens.txt") as tfile:
        tokens = tfile.readlines()
    for tok in tokens:
        rows.append({"tmp": run_conf.temp, "itr": run_conf.itr, "tokens": tok})

df = pd.DataFrame(rows)
df.to_csv(conf.eval_conf.get_scores_path("_toks"))
