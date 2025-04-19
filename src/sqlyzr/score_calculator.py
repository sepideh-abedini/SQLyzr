import os
from functools import partial

import pandas as pd
from tqdm import tqdm

from src.cat.categories import find_cat
from src.configs.sqlyzr_config import SQLyzrConfig
from src.eval.metrics import *
from src.eval.model_eval_config import ModelEvalConfig
from src.sqlyzr.pred_gold_reader import PredGoldReader
from src.util.file_utils import file_exists_not_forced
from src.util.log_util import log
from src.util.multi_thread_utils import exec_multi_process

catter = Catter()


def calc_for_entry(conf: SQLyzrConfig, run_conf: SingleRunConfig, entry):
    pred, gold, db_id = entry
    cat, sub_cat = catter.categorize(gold)
    pred_cat, pred_sub_cat = catter.categorize(pred)
    example_scores = {"model": conf.model, "tmp": run_conf.temp, "itr": run_conf.itr, "cat": str(cat), "sub": sub_cat,
                      "dst": run_conf.dataset_config.dataset_type,
                      "pcat": pred_cat.name,
                      "psub": pred_sub_cat.name}
    metrics = []
    for metric_name, metric_class in conf.eval_conf.metrics.items():
        metrics.append(metric_class(metric_name, run_conf.dataset_config))

    for metric in metrics:
        try:
            score = metric.calc(gold, pred, db_id)
        except Exception as e:
            logger.debug(e)
            score = 0
        example_scores[metric.name] = score
    return example_scores


def calc_for_data(eval_conf, run_conf, data):
    scores = []
    for i, (pred, gold, db_id) in tqdm(enumerate(data), total=len(data),
                                       desc=f"Calculating scores for {run_conf}-{os.getpid()}"):
        example_scores = calc_for_entry(eval_conf, run_conf, (pred, gold, db_id))
        scores.append(example_scores)

    return scores


@log("Score calculation for single conf")
def calc_for_conf(conf: SQLyzrConfig, run_conf: SingleRunConfig):
    scores_path = conf.eval_conf.get_scores_path(
        f"_{run_conf.temp}_{run_conf.itr}_{run_conf.dataset_config.dataset_type}")
    if file_exists_not_forced(scores_path):
        logger.info(f"Scores for {run_conf} exists!")
        return pd.read_csv(scores_path)

    reader = PredGoldReader(run_conf)
    all_data = reader.get_pred_gold_db_id()
    all_scores = exec_multi_process(partial(calc_for_entry, conf, run_conf), all_data,
                                    desc=f"Score calculation for {run_conf}")
    df = pd.DataFrame(all_scores)
    with open(run_conf.get_tokens_path(), "r") as f:
        tokens = [int(line.strip()) for line in f if line.strip()]
    df["tokens"] = tokens
    df['count'] = 1
    df['plc'] = df.apply(lambda e: int(find_cat(e['pcat']) <= find_cat(e['cat'])), axis=1)
    df['plt'] = df.apply(lambda e: int((e['et'] / e['get']) > conf.etc_ratio), axis=1)
    df.to_csv(scores_path)

    return df


class ScoreCalculator:
    __config: SQLyzrConfig

    def __init__(self, config: SQLyzrConfig):
        self.__config = config

    @log("Score calculation")
    def calc_scores(self):
        config = self.__config.eval_conf
        if file_exists_not_forced(config.get_raw_scores_path()):
            logger.info(f"Raw scores exists: {config.get_raw_scores_path()}, skipping calculation.")
            return

        df = pd.DataFrame()

        for conf in config.get_run_confs():
            sub_df = calc_for_conf(self.__config, conf)
            df = pd.concat([df, sub_df])
        df.to_csv(config.get_raw_scores_path())
