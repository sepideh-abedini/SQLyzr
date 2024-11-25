from itertools import product
from pathlib import Path
from random import randrange
from typing import List

import pandas as pd

from src.cat.categories import get_all_cats, CATS
from src.cat.categorizer import Categorizer
from src.cat.tag_extractor import TagExtractor
from src.evaluation.evaluator.model_eval_config import ModelEvalConfig
from src.evaluation.runner.dataset_config import SPIDER_SMALL
from src.evaluation.runner.runner_config import RunnerConfig
from src.sql_parser.parser import SqlParser

cats = get_all_cats(CATS)


def export_evaluation_data(config: RunnerConfig, eval_data_path: str):
    parser = SqlParser()
    tag_extractor = TagExtractor()
    categorizer = Categorizer()

    with open(config.output_path) as pred_file, open(config.dataset_config.get_gold_path()) as gold_file:
        pred_file_lines = pred_file.readlines()
        rows = []
        for i, gold_line in enumerate(gold_file):
            gold_sql, db_id = gold_line.strip().split("\t")
            ast = parser.parse(gold_sql)
            tags = tag_extractor.extract_tags(ast)
            cat = categorizer.get_category(tags.tag_set)
            pred_sql = pred_file_lines[i].strip()
            row = {'idx': i, 'gold': gold_sql, 'pred': pred_sql, 'db_id': db_id, 'cat': cat}
            rows.append(row)
    df = pd.DataFrame(rows)
    df.to_json(eval_data_path)
    df.to_csv(Path(eval_data_path).with_suffix(".csv"))


def export_to_file(df, out_path, row_to_line):
    with open(out_path, 'w') as out_file:
        for idx, row in df.iterrows():
            line = row_to_line(row)
            out_file.write(line)


def split_by_categories(config: ModelEvalConfig, temp: float, itr: int):
    df = pd.read_json(config.get_eval_data_path(temp, itr))
    dfs = {cat: sub_df for cat, sub_df in df.groupby('cat')}
    for cat, sub_df in dfs.items():
        export_to_file(sub_df, config.get_gold_path_per_cat(temp, itr, cat),
                       lambda row: f"{row['gold']}\t{row['db_id']}\n")
        export_to_file(sub_df, config.get_pred_path_per_cat(temp, itr, cat),
                       lambda row: f"{row['pred']}\n")
        with open(config.get_pred_path_per_cat(temp, itr, cat), 'a') as pred_file:
            pred_file.write(f"tokens:{randrange(15000, 30000)}\n")


if __name__ == "__main__":
    temps = [0.0, 0.2, 0.4, 0.7, 1.0]
    num_itrs = 4
    itrs = list(range(num_itrs))

    config = ModelEvalConfig(
        temps=temps,
        num_itrs=num_itrs,
        pred_dir="data/dum",
        eval_dir="data/eval",
        dataset_config=SPIDER_SMALL
    )

    for temp, itr in product(temps, itrs):
        export_evaluation_data(config.get_runner_conf(temp, itr),
                               config.get_eval_data_path(temp, itr))

    for temp, itr in product(temps, itrs):
        split_by_categories(config, temp, itr)
