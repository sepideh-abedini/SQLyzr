import pandas as pd

from src.cat.catter import Catter
from src.configs.eval import DIN_SPIDER_SMALL_EVAL
from src.eval.lib import confidence_level_interval
from src.eval.metrics import *
from src.eval.model_eval_config import ModelEvalConfig


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
    catter = Catter()
    df = pd.DataFrame()
    metrics = [
        ExactMatch("em", config.dataset_config),
        ExecAcc("ea", config.dataset_config),
        TotalExecTime("et", config.dataset_config),
        SpiderExactMatch("sem", config.dataset_config),
        RelaxedExecAcc("rea", config.dataset_config),
        Count("count", config.dataset_config),
    ]
    stat_metrics = [
        TokenUsage("tokens")
    ]
    for conf in config.get_run_confs():
        pred_path = conf.get_pred_path()
        gold_path = conf.dataset_config.get_gold_path()
        data = get_pred_gold_db_id(pred_path, gold_path)
        scores = []
        print(f"Calculating scores for {conf}")
        for i, (pred, gold, db_id) in enumerate(data):
            cat = catter.get_category(gold)
            example_scores = {"tmp": conf.temp, "itr": conf.itr, "cat": str(cat)}
            for metric in metrics:
                score = metric.calc(gold, pred, db_id)
                example_scores[metric.name] = score
            for metric in stat_metrics:
                score = metric.calc(i, conf)
                example_scores[metric.name] = score
            scores.append(example_scores)
        ti_df = pd.DataFrame(scores)
        df = pd.concat([df, ti_df])
    df.to_csv(config.get_raw_scores_path())


def post_process_scores(config: ModelEvalConfig):
    df = pd.read_csv(config.get_raw_scores_path(), index_col=0)

    cat_grouped = df.groupby(['tmp', 'itr'], as_index=False).sum()
    cat_grouped['cat'] = 'all'
    cat_grouped.to_csv(config.get_scores_path("_1"))
    #
    df = pd.concat([cat_grouped, df], join='inner', ignore_index=True)
    df.to_csv(config.get_scores_path("_2"))
    #
    df = df.groupby(['tmp', 'itr', 'cat'], as_index=False).sum()
    df.to_csv(config.get_scores_path("_3"))

    scores = ["em", "ea", "sem", "rea"]
    df[scores] = df[scores].div(df['count'], axis=0)
    df.to_csv(config.get_scores_path("_4"), index_label="idx")

    means = df.groupby(['tmp', 'cat']).mean()
    means[scores] = means[scores] * 100
    means = means.drop(columns=['itr'])
    means.to_csv(config.get_scores_path("_means"))
    means.columns = [col + '_mean' for col in means.columns]

    cis = df.groupby(['tmp', 'cat']).agg(confidence_level_interval)
    cis = cis.drop(columns=['itr'])
    cis.to_csv(config.get_scores_path("cis"))
    cis.columns = [col + '_ci' for col in cis.columns]

    final = means.join(cis)
    final = final.round(2)
    final.to_csv(config.get_scores_path())


if __name__ == "__main__":
    calc_scores(DIN_SPIDER_SMALL_EVAL)
    # evaluate(DIN_SMALL_CONF)
