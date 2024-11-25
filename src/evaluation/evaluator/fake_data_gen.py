import os.path
import shutil
import re
from itertools import product
from typing import List

from src.evaluation.evaluator.model_eval_config import ModelEvalConfig
from src.evaluation.runner.configs import SPIDER_SMALL


def generate_fake_preds(config: ModelEvalConfig, pred_file: str, temps: List[float], itrs: List[int]):
    pred_path = os.path.join(config.pred_dir, pred_file)
    for temp, itr in product(temps, itrs):
        conf = config.get_runner_conf(temp, itr)
        print(f"Generating: {conf.output_path}")
        shutil.copy(pred_path, conf.output_path)


if __name__ == '__main__':
    temps = [0.0, 0.2, 0.4, 0.7, 1.0]
    num_itrs = 4
    itrs = list(range(num_itrs))

    eval_config = ModelEvalConfig(
        temps=temps,
        num_itrs=num_itrs,
        pred_dir="data/dum",
        eval_dir="data/eval",
        dataset_config=SPIDER_SMALL
    )
    generate_fake_preds(eval_config, "pred.txt", temps, itrs)
