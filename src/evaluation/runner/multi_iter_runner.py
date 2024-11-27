import os
from typing import Type

from src.evaluation.evaluator.model_eval_config import ModelEvalConfig
from src.evaluation.runner.configs import SPIDER_SMALL, EVAL_CONF, SMALL_EVAL_CONF
# from src.evaluation.runner.dail_runner import DailRunner
from src.evaluation.runner.din_runner import DinRunner
from src.evaluation.runner.model_runner import ModelRunner
from src.evaluation.runner.multi_thread_runner import MultiThreadRunner


def run_multiple_iters(config: ModelEvalConfig, runner_type: Type[ModelRunner], resume: bool = True):
    for conf in config.get_run_confs():
        if resume and conf.is_pred_file_valid():
            print(f"Pred file exists {conf.get_pred_path()}, skipping run.")
            continue
        print(f"Running for temp={conf.temp},itr={conf.itr}")
        runner = MultiThreadRunner(conf, runner_type, 4)
        runner.run()


if __name__ == "__main__":
    run_multiple_iters(SMALL_EVAL_CONF, DinRunner)
