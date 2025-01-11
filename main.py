import asyncio
import json
import time

from tqdm import tqdm

from assets.print_logo import print_logo
from src.aug.augment_data import augment_data
from src.configs.dataset import BIRD_TRAIN, BIRD_DEV
from src.configs.sqlyzr import DIN_SPIDER_DEV, DIN_SPIDER_SMALL
from src.dataset.validate import validate_dataset
from src.eval.evaluator import calc_scores, post_process_scores
from src.eval.exact_match import ExactMatchParser
from src.eval.model_eval_config import ModelEvalConfig
from src.eval.run_model import run_din_async, run_din
from src.parse.parser import SqlParser
from src.rel.transformer_eval import find_transformers


def validate_preds(conf: ModelEvalConfig):
    parser = ExactMatchParser(conf.dataset_config.get_tables_path())
    for run_conf in conf.get_run_confs():
        errors = []
        with (open(run_conf.dataset_config.get_data_path()) as data_file,
              open(run_conf.get_pred_path()) as pred_file):
            data = json.load(data_file)
            pred_lines = pred_file.readlines()
            for i in range(len(data)):
                pred = pred_lines[i]
                try:
                    ast = parser.parse(pred_lines[i], data[i]["db_id"])
                except Exception:
                    ast = None
                if ast is None:
                    errors.append({"pred": pred, "gold": data[i]["query"], "question": data[i]["question"]})
            with open(f"{run_conf.get_pred_path()}.errors.json", "w") as errors_file:
                errors_file.write(json.dumps(errors, indent=4))
            print(f"{run_conf.get_pred_path()} errors: {len(errors)}/{len(data)}")


async def main():
    # print_logo()

    # sqlyzr_conf = DIN_SPIDER_SMALL
    sqlyzr_conf = DIN_SPIDER_DEV
    # sqlyzr_conf = DAIL_SPIDER_SMALL
    # sqlyzr_conf = DAIL_SPIDER_DEV
    eval_conf = sqlyzr_conf.eval_conf
    # eval_conf = DIN_SPIDER_DEV.eval_conf
    # eval_conf = DAIL_SPIDER_SMALL.eval_conf
    # eval_conf = DAIL_SPIDER_SMALL.eval_conf
    # eval_conf = DIN_BIRD_SMALL.eval_conf
    # dataset_conf = BIRD_DEV
    # dataset_conf = BIRD_TRAIN

    # validate_dataset(dataset_conf)

    # run_din(eval_conf)
    #
    # asyncio.run(run_din_async(eval_conf))
    #
    # validate_preds(eval_conf)

    # asyncio.run(run_dail_async(eval_conf))

    # calc_scores(eval_conf)

    post_process_scores(eval_conf)
    #
    # await find_transformers(eval_conf)
    #
    # augment_data(sqlyzr_conf)


if __name__ == '__main__':
    asyncio.run(main())
