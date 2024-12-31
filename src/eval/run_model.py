import asyncio

from src.eval.model_eval_config import ModelEvalConfig
from src.third_party.din.din_pred import DinPredictor


def run_din(config: ModelEvalConfig):
    for conf in config.get_run_confs():
        predictor = DinPredictor(conf)
        asyncio.run(predictor.run())
