from pathlib import Path
from random import randrange

import pandas as pd

from src.cat.categories import get_all_cats, CATS
from src.cat.categorizer import Categorizer
from src.cat.tag_extractor import TagExtractor
from src.eval.configs import SMALL_EVAL_CONF
from src.eval.runner_config import SingleRunConfig
from src.parse.parser import SqlParser

cats = get_all_cats(CATS)


def export_evaluation_data(config: SingleRunConfig):
    parser = SqlParser()
    tag_extractor = TagExtractor()
    categorizer = Categorizer()

    with open(config.get_pred_path()) as pred_file, open(config.dataset_config.get_gold_path()) as gold_file:
        pred_file_lines = pred_file.readlines()
        rows = []
        for i, gold_line in enumerate(gold_file):
            gold_sql, db_id = gold_line.strip().split("\t")
            ast = parser.parse(gold_sql)
            tags = tag_extractor.extract_tags(ast)
            cat = categorizer.get_category(tags.tag_set)
            pred_sql = pred_file_lines[i].strip()
            row = {'idx': i, 'gold': str(gold_sql), 'pred': str(pred_sql), 'db_id': str(db_id), 'cat': str(cat)}
            rows.append(row)
    df = pd.DataFrame(rows)
    df.to_json(config.get_eval_data_path())
    df.to_csv(Path(config.get_eval_data_path()).with_suffix(".csv"))


def export_to_file(df, out_path, row_to_line):
    with open(out_path, 'w') as out_file:
        for idx, row in df.iterrows():
            line = row_to_line(row)
            out_file.write(line)


def split_by_categories(config: SingleRunConfig):
    df = pd.read_json(config.get_eval_data_path())
    dfs = {cat: sub_df for cat, sub_df in df.groupby('cat')}
    for cat, sub_df in dfs.items():
        export_to_file(sub_df, config.get_eval_gold_path_per_cat(cat),
                       lambda row: f"{row['gold']}\t{row['db_id']}\n")
        export_to_file(sub_df, config.get_eval_pred_path_per_cat(cat),
                       lambda row: f"{row['pred']}\n")
        with open(config.get_eval_pred_path_per_cat(cat), 'a') as pred_file:
            pred_file.write(f"tokens:{randrange(15000, 30000)}\n")


if __name__ == "__main__":
    for conf in SMALL_EVAL_CONF.get_run_confs():
        export_evaluation_data(conf)
        split_by_categories(conf)
