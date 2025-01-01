import asyncio

from src.eval.model_eval_config import ModelEvalConfig
from src.third_party.dail.dail_conf import DailConfig
from src.third_party.dail.dail_pred import DailPredictor
from src.third_party.din.config import DinConfig
from src.third_party.din.din_pred import DinPredictor


def run_din(config: ModelEvalConfig):
    for run_conf in config.get_run_confs():
        din_conf = DinConfig(run_conf)
        predictor = DinPredictor(din_conf)
        asyncio.run(predictor.run())


def run_dail(config: ModelEvalConfig):
    for run_conf in config.get_run_confs():
        dail_conf = DailConfig(run_conf)
        predictor = DailPredictor(dail_conf)
        asyncio.run(predictor.run())
