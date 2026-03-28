import os
from functools import partial

import pandas as pd
from tqdm import tqdm

from src.cat.categories import find_cat
from src.cat.catter import Catter
from src.configs.sqlyzr_config import SQLyzrConfig
from src.eval.metrics import *
from src.eval.single_run_config import SingleRunConfig
from src.sqlyzr.pred_gold_reader import PredGoldReader
from src.util.file_utils import file_exists_not_forced
from src.util.log_util import log
from src.util.multi_thread_utils import exec_multi_process

catter = Catter()


def calc_for_entry(conf: SQLyzrConfig, run_conf: SingleRunConfig, scale, entry):
    pred, gold, db_id = entry
    cat, sub_cat = catter.categorize(gold)
    pred_cat, pred_sub_cat = catter.categorize(pred)
    example_scores = {"model": run_conf.model, "tmp": run_conf.temp, "itr": run_conf.itr, "cat": str(cat),
                      "sub": sub_cat,
                      "dst": run_conf.dataset_config.dataset_type,
                      "dst_ver": run_conf.dataset_config.ver,
                      "pcat": pred_cat.name,
                      "psub": pred_sub_cat.name}
    metrics = []
    for metric_name, metric_class in conf.eval_conf.metrics.items():
        metrics.append(metric_class(metric_name, run_conf.dataset_config))

    for metric in metrics:
        try:
            score = metric.calc(gold, pred, db_id, scale)
        except Exception as e:
            logger.debug(e)
            score = 0
        example_scores[metric.name] = score
    return example_scores


@log("Score calculation for single conf")
def calc_for_conf_scale(conf: SQLyzrConfig, run_conf: SingleRunConfig, scale: int):
    if not conf.eval_force and file_exists_not_forced(run_conf.get_scores_path()):
        logger.info(f"Scores for {run_conf} exists at {run_conf.get_scores_path()}!")
        return pd.read_csv(run_conf.get_scores_path())

    reader = PredGoldReader(run_conf)
    all_data = reader.get_pred_gold_db_id()
    all_scores = exec_multi_process(partial(calc_for_entry, conf, run_conf, scale), all_data,
                                    desc=f"Score calculation for {run_conf} x{scale}")
    df = pd.DataFrame(all_scores)
    with open(run_conf.get_tokens_path(), "r") as f:
        tokens = [int(line.strip()) for line in f if line.strip()]

    with open(run_conf.get_time_path(), "r") as f:
        times = [int(line.strip()) for line in f if line.strip()]
    df["tokens"] = tokens
    df["time_seconds"] = times
    df['count'] = 1
    df['gold_cat_idx'] = df['cat'].str.replace('c', '', regex=False).astype(int)
    df['pred_cat_idx'] = df['pcat'].str.replace('c', '', regex=False).astype(int)
    df['pred_cat_lt_gold'] = (df['pred_cat_idx'] <= df['gold_cat_idx']).astype(int)
    df['plc'] = df['pred_cat_lt_gold'] * df['ea']
    df['pred_et_lt_gold'] = df.apply(lambda e: int((e['et'] / e['get']) < conf.etc_ratio), axis=1)
    df["plt"] = df['pred_et_lt_gold'] * df['ea']
    # df['plc'] = df.apply(lambda e: int(find_cat(e['pcat']) <= find_cat(e['cat'])), axis=1)
    # df['plt'] = df.apply(lambda e: int((df['get'] != 0) & (e['et'] / e['get']) > conf.etc_ratio), axis=1)
    # df['plt'] = ((df['get'] != 0) & ((df['et'] / df['get']) > conf.etc_ratio)).astype(int)
    df['scale'] = scale

    return df


@log("Score calculation for single conf")
def calc_for_conf(conf: SQLyzrConfig, run_conf: SingleRunConfig):
    df = pd.DataFrame()
    for scale in run_conf.scales:
        scale_df = calc_for_conf_scale(conf, run_conf, scale)
        df = pd.concat([df, scale_df])

    df.to_csv(run_conf.get_scores_path())
    return df


class ScoreCalculator:
    __config: SQLyzrConfig

    def __init__(self, config: SQLyzrConfig):
        self.__config = config

    @log("Score calculation")
    def calc_scores(self):
        config = self.__config.eval_conf
        if not self.__config.eval_force and file_exists_not_forced(config.get_raw_scores_path()):
            logger.info(f"Raw scores exists: {config.get_raw_scores_path()}, skipping calculation.")
            return

        df = pd.DataFrame()

        for conf in config.get_run_confs():
            sub_df = calc_for_conf(self.__config, conf)
            df = pd.concat([df, sub_df])
        df.to_csv(config.get_raw_scores_path())
