import sys

import tqdm
from openai.types.chat import ChatCompletion

from src.configs.config_loader import load_config
from src.util.model_utils import read_jsonl

conf_path = sys.argv[1]
conf = load_config(conf_path)

suffs = ["classif.out.jsonl", "schema.out.jsonl", "sql.out.jsonl", "sql_debug.out.jsonl"]
for run_conf in tqdm.tqdm(conf.eval_conf.get_run_confs()):
    all_toks = []
    for suff in suffs:
        p = f"{run_conf.get_pred_path()}.{suff}"
        data = read_jsonl(p, ChatCompletion)
        toks = list(map(lambda r: r.usage.total_tokens, data))
        all_toks.append(toks)
    sum_toks = list(map(lambda s: sum(s), zip(*all_toks)))
    with open(f"{run_conf.get_pred_path()}.tokens.txt", "w") as tok_file:
        tok_file.write("\n".join(map(str, sum_toks)))
