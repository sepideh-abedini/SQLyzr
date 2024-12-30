import pandas as pd

from src.cat.categorizer import Categorizer
from src.cat.catter import Catter
from src.cat.tag_extractor import TagExtractor
from src.eval.configs import DIN_SMALL_CONF
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
    catter = Catter()
    df = pd.DataFrame()
    metrics = [
        ExactMatch("em", config.dataset_config),
        ExecAcc("ea", config.dataset_config),
        TotalExecTime("et", config.dataset_config),
        SpiderExactMatch("sem", config.dataset_config),
        Count("count", config.dataset_config)
    ]
    for conf in config.get_run_confs():
        pred_path = conf.get_pred_path()
        gold_path = conf.dataset_config.get_gold_path()
        data = get_pred_gold_db_id(pred_path, gold_path)
        scores = []
        for gold, pred, db_id in data:
            cat = catter.get_category(gold)
            example_scores = {"tmp": conf.temp, "itr": conf.itr, "cat": cat.name}
            for metric in metrics:
                score = metric.calc(gold, pred, db_id)
                example_scores[metric.name] = score
            scores.append(example_scores)
        ti_df = pd.DataFrame(scores)
        df = pd.concat([df, ti_df])
    df.to_csv("scores.csv")


if __name__ == "__main__":
    calc_scores(DIN_SMALL_CONF)
    # evaluate(DIN_SMALL_CONF)
