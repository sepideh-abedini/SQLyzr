from typing import List

import tqdm

from src.eval.model_eval_config import ModelEvalConfig
from src.util.model_utils import read_jsonl




def din_token_calc(conf: ModelEvalConfig):
    files = ["classif.out.jsonl", "schema.out.jsonl", "sql.out.jsonl", "sql_debug.out.jsonl"]
    export_tokens_file(conf, files)


def dail_token_calc(conf: ModelEvalConfig):
    files = ["sql.out.jsonl", "sql.out.second.jsonl"]
    export_tokens_file(conf, files)
