from typing import Type

from src.evaluation.configs import SMALL_EVAL_CONF
from src.evaluation.evaluator.data_generator import export_evaluation_data, split_by_categories
from src.evaluation.evaluator.evaluator import evaluate
from src.evaluation.evaluator.model_eval_config import ModelEvalConfig
from src.evaluation.runner.din_runner import DinRunner
from src.evaluation.runner.model_runner import ModelRunner
from src.evaluation.runner.multi_iter_runner import run_multiple_iters


def run_and_evaluate_model(config: ModelEvalConfig, runner: Type[ModelRunner]):
    run_multiple_iters(config, runner, resume=False)
    for conf in config.get_run_confs():
        export_evaluation_data(conf)
        split_by_categories(conf)
    evaluate(config)


if __name__ == "__main__":
    run_and_evaluate_model(SMALL_EVAL_CONF, DinRunner)
