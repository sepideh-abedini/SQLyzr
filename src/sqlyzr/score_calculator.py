import os
import threading

import pandas as pd
from loguru import logger
from tqdm import tqdm

from src.configs.sqlyzr import SQLyzrConfig
from src.eval.metrics import *
from src.eval.model_eval_config import ModelEvalConfig
from src.sqlyzr.pred_gold_reader import PredGoldReader
from src.third_party.dail.dail_pred import DAIL_THREADS
from src.util.multi_thread_utils import exec_multi_thread


def calc_for_conf(config: ModelEvalConfig, conf: SingleRunConfig):
    scores_path = config.get_scores_path(f"_{conf.temp}_{conf.itr}")
    if os.path.exists(scores_path):
        logger.info(f"Scores for {conf} exists!")
        return pd.read_csv(scores_path)

    def calc_for_data(data):
        catter = Catter()
        metrics = []
        for metric_name, metric_class in config.metrics.items():
            metrics.append(metric_class(metric_name, config.dataset_config))
        for i, (pred, gold, db_id) in tqdm(enumerate(data), total=len(data),
                                           desc=f"Calculating scores for {conf}-{threading.get_ident()}"):
            cat, sub_cat = catter.categorize(gold)
            example_scores = {"tmp": conf.temp, "itr": conf.itr, "cat": str(cat), "sub_cat": sub_cat}
            for metric in metrics:
                try:
                    score = metric.calc(gold, pred, db_id)
                except Exception as e:
                    logger.debug(e)
                    score = 0
                example_scores[metric.name] = score
            scores.append(example_scores)
        return scores

    reader = PredGoldReader(conf)
    data = reader.get_pred_gold_db_id()
    scores = []
    logger.info(f"Calculating scores for {conf}")
    scores = exec_multi_thread(calc_for_data, data, DAIL_THREADS)
    ti_df = pd.DataFrame(scores)
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
