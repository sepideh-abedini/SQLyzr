import os

import pandas as pd
from tqdm import tqdm

from src.cat.catter import Catter
from src.configs.eval import DIN_SPIDER_SMALL_EVAL
from src.eval.lib import confidence_level_interval
from src.eval.metrics import *
from src.eval.model_eval_config import ModelEvalConfig
from src.parse.parser import SqlParser


def get_pred_gold_db_id(pred_path, gold_path):
    with open(pred_path) as pred_file, open(gold_path) as gold_file:
        pred_file_lines = pred_file.readlines()
        rows = []
        for i, gold_line in enumerate(gold_file):
            gold_sql, db_id = gold_line.strip().split("\t")
            pred_sql = pred_file_lines[i].strip()
            rows.append((pred_sql, gold_sql, db_id))
    return rows


def calc_scores(config: ModelEvalConfig):
    if not config.force and os.path.exists(config.get_raw_scores_path()):
        print(f"Raw scores exists: {config.get_raw_scores_path()}, skipping calculation.")
        return

    catter = Catter()
    parser = SqlParser()
    df = pd.DataFrame()
    metrics = []
    for metric_name, metric_class in config.metrics.items():
        metrics.append(metric_class(metric_name, config.dataset_config))

    for conf in config.get_run_confs():
        pred_path = conf.get_pred_path()
        gold_path = conf.dataset_config.get_gold_path()
        data = get_pred_gold_db_id(pred_path, gold_path)
        scores = []
        print(f"Calculating scores for {conf}")
        for i, (pred, gold, db_id) in tqdm(enumerate(data), total=len(data)):
            cat, sub_cat = catter.categorize(gold)
            past = parser.parse(pred)
            example_scores = {"tmp": conf.temp, "itr": conf.itr, "cat": str(cat), "sub_cat": sub_cat}
            for metric in metrics:
                # if past:
                try:
                    score = metric.calc(gold, pred, db_id)
                except Exception as e:
                    log(e)
                    score = 0
                example_scores[metric.name] = score
            scores.append(example_scores)
        ti_df = pd.DataFrame(scores)
        df = pd.concat([df, ti_df])
    df.to_csv(config.get_raw_scores_path())


def post_process_scores(config: ModelEvalConfig):
    df = pd.read_csv(config.get_raw_scores_path(), index_col=0)
    df['count'] = 1

    all_sub_cats = df.groupby(['tmp', 'itr', "cat"], as_index=False).sum()
    all_sub_cats['sub_cat'] = 'all'
    all_sub_cats.to_csv(config.get_scores_path("_all_sub_cats"))

    all_cats = df.groupby(['tmp', 'itr'], as_index=False).sum()
    all_cats['cat'] = 'all'
    all_cats['sub_cat'] = 'all'
    all_cats.to_csv(config.get_scores_path("_all_cats"))
    #
    combined = pd.concat([all_cats, all_sub_cats, df], join='inner', ignore_index=True)
    combined.to_csv(config.get_scores_path("_combined"))

    sums = combined.groupby(['tmp', 'itr', 'cat', "sub_cat"], as_index=False).sum()
    sums.to_csv(config.get_scores_path("_sum"))

    # stat_metrics = [
    #     TokenUsage("tokens")
    # ]
    # stats_rows = []
    # for run_conf in config.get_run_confs():
    #     row = {'tmp': run_conf.temp, 'itr': run_conf.itr}
    #     for metric in stat_metrics:
    #         row[metric.name] = metric.calc(run_conf)
    #     stats_rows.append(row)
    # stats = pd.DataFrame(stats_rows)
    # sums = pd.merge(sums, stats, on=["tmp", "itr"], how="inner")
    # sums.to_csv(config.get_scores_path("_stats"))

    metric_names = config.get_metric_names()
    means = sums.copy()
    means[metric_names] = sums[metric_names].div(sums['count'], axis=0)
    means.to_csv(config.get_scores_path("_means"), index_label="idx")

    means_per_temp = means.groupby(['tmp', 'cat', "sub_cat"]).mean()
    means_per_temp[metric_names] = means_per_temp[metric_names] * 100
    means_per_temp = means_per_temp.drop(columns=['itr'])
    means_per_temp.to_csv(config.get_scores_path("_means_per_temp"))

    # means_per_temp = means_per_temp.drop(columns=['itr'])
    #
    cis = means.groupby(['tmp', 'cat', "sub_cat"]).agg(confidence_level_interval)
    cis = cis.drop(columns=['itr'])
    cis.to_csv(config.get_scores_path("_cis"))

    final = means_per_temp.join(cis, lsuffix="_mean", rsuffix="_ci")
    final = final.round(2)
    final.to_csv(config.get_scores_path())


if __name__ == "__main__":
    calc_scores(DIN_SPIDER_SMALL_EVAL)
    # evaluate(DIN_SMALL_CONF)
