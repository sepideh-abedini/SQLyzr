import os.path
import shutil
import re
from itertools import product
from typing import List

from src.evaluation.configs import SPIDER_SMALL, EVAL_CONF, SMALL_EVAL_CONF
from src.evaluation.evaluator.model_eval_config import ModelEvalConfig


def generate_fake_preds(config: ModelEvalConfig, pred_file: str):
    for conf in config.get_run_confs():
        print(f"Generating: {conf.get_pred_path()}")
        shutil.copy(pred_file, conf.get_pred_path())


if __name__ == '__main__':
    generate_fake_preds(SMALL_EVAL_CONF, "data/dum/pred.txt")
