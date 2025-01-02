import asyncio
from enum import Enum

from assets.print_logo import print_logo
from src.aug.augment_data import augment_data
from src.configs.sqlyzr import DIN_SPIDER_SMALL, DIN_SPIDER_DEV
from src.dataset.validate import validate_dataset
from src.eval.evaluator import calc_scores, post_process_scores
from src.eval.run_model import run_din, run_din_async
from src.rel.transformer_eval import find_transformers


def main():
    print_logo()

    sqlyzr_conf = DIN_SPIDER_SMALL
    eval_conf = sqlyzr_conf.eval_conf
    # eval_conf = DIN_SPIDER_DEV.eval_conf
    # eval_conf = DAIL_SPIDER_SMALL.eval_conf
    # eval_conf = DAIL_SPIDER_SMALL.eval_conf
    # eval_conf = DIN_BIRD_SMALL.eval_conf

    # validate_dataset(eval_conf.dataset_config)

    # run_din(eval_conf)

    # calc_scores(eval_conf)

    # post_process_scores(eval_conf)

    # find_transformers(eval_conf)

    augment_data(sqlyzr_conf)


if __name__ == '__main__':
    main()
