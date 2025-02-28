import os
import threading
from functools import partial

import pandas as pd
from tqdm import tqdm

from src.configs.sqlyzr_config import SQLyzrConfig
from src.eval.metrics import *
from src.eval.model_eval_config import ModelEvalConfig
from src.sqlyzr.pred_gold_reader import PredGoldReader
from src.util.multi_thread_utils import exec_multi_process

EVAL_PROCS = int(os.getenv("EVAL_PROCS", 1))


def calc_for_data(eval_conf, run_conf, data):
    catter = Catter()
    scores = []
    metrics = []
    for metric_name, metric_class in eval_conf.metrics.items():
        metrics.append(metric_class(metric_name, eval_conf.dataset_config))
    for i, (pred, gold, db_id) in tqdm(enumerate(data), total=len(data),
                                       desc=f"Calculating scores for {run_conf}-{threading.get_ident()} -{os.getpid()}"):
        cat, sub_cat = catter.categorize(gold)
        example_scores = {"tmp": run_conf.temp, "itr": run_conf.itr, "cat": str(cat), "sub_cat": sub_cat}
        for metric in metrics:
            try:
                score = metric.calc(gold, pred, db_id)
            except Exception as e:
                logger.debug(e)
                score = 0
            example_scores[metric.name] = score
        scores.append(example_scores)
    return scores


def calc_for_conf(config: ModelEvalConfig, conf: SingleRunConfig):
    scores_path = config.get_scores_path(f"_{conf.temp}_{conf.itr}")
    if os.path.exists(scores_path):
        logger.info(f"Scores for {conf} exists!")
        return pd.read_csv(scores_path)

    reader = PredGoldReader(conf)
    all_data = reader.get_pred_gold_db_id()
    logger.info(f"Calculating scores for {conf}")
    all_scores = exec_multi_process(partial(calc_for_data, config, conf), all_data, EVAL_PROCS)
    ti_df = pd.DataFrame(all_scores)
    ti_df.to_csv(scores_path)

    return ti_df


class ScoreCalculator:
    __config: SQLyzrConfig

    def __init__(self, config: SQLyzrConfig):
        self.__config = config

    def calc_scores(self):
        config = self.__config.eval_conf
        if os.path.exists(config.get_raw_scores_path()):
            logger.info(f"Raw scores exists: {config.get_raw_scores_path()}, skipping calculation.")
            return

        df = pd.DataFrame()

        for conf in config.get_run_confs():
            sub_df = calc_for_conf(config, conf)
            df = pd.concat([df, sub_df])
        df.to_csv(config.get_raw_scores_path())

        logger.info("Score calculation finished!")
