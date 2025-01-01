import asyncio

from src.eval.model_eval_config import ModelEvalConfig
from src.third_party.dail.dail_conf import DailConfig
from src.third_party.dail.dail_pred import DailPredictor
from src.third_party.din.din_pred import DinPredictor


def run_din(config: ModelEvalConfig):
    for conf in config.get_run_confs():
        predictor = DinPredictor(conf)
        asyncio.run(predictor.run())


def run_dail(config: ModelEvalConfig):
    for conf in config.get_run_confs():
        dail_conf = DailConfig(conf)
        predictor = DailPredictor(dail_conf)
        asyncio.run(predictor.run())
