import os

import pandas as pd
from tqdm import tqdm

from src.configs.sqlyzr import SQLyzrConfig
from src.eval.metrics import *
from src.parse.parser import SqlParser
from src.sqlyzr.pred_gold_reader import PredGoldReader

from loguru import logger


class ScoreCalculator:
    __config: SQLyzrConfig

    def __init__(self, config: SQLyzrConfig):
        self.__config = config

    def calc_scores(self):
        config = self.__config.eval_conf
        if os.path.exists(config.get_raw_scores_path()):
            logger.debug(f"Raw scores exists: {config.get_raw_scores_path()}, skipping calculation.")
            return

        catter = Catter()
        parser = SqlParser()
        df = pd.DataFrame()
        metrics = []
        for metric_name, metric_class in config.metrics.items():
            metrics.append(metric_class(metric_name, config.dataset_config))

        for conf in config.get_run_confs():
            reader = PredGoldReader(conf)
            data = reader.get_pred_gold_db_id()
            scores = []
            print(f"Calculating scores for {conf}")
            for i, (pred, gold, db_id) in tqdm(enumerate(data), total=len(data)):
                cat, sub_cat = catter.categorize(gold)
                example_scores = {"tmp": conf.temp, "itr": conf.itr, "cat": str(cat), "sub_cat": sub_cat}
                for metric in metrics:
                    # if past:
                    try:
                        score = metric.calc(gold, pred, db_id)
                    except Exception as e:
                        logger.debug(e)
                        score = 0
                    example_scores[metric.name] = score
                scores.append(example_scores)
            ti_df = pd.DataFrame(scores)
            df = pd.concat([df, ti_df])
        df.to_csv(config.get_raw_scores_path())

        logger.debug("Score calculation finished!")
