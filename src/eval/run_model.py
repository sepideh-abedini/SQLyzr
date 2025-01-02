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
        print(f"Running for conf = {run_conf}")


async def run_din_async(config: ModelEvalConfig):
    futures = []
    for run_conf in config.get_run_confs():
        din_conf = DinConfig(run_conf)
        predictor = DinPredictor(din_conf)
        futures.append(predictor.run())
        print(f"Running for conf = {run_conf}")
    await asyncio.gather(*futures)


def run_dail(config: ModelEvalConfig):
    for run_conf in config.get_run_confs():
        dail_conf = DailConfig(run_conf)
        predictor = DailPredictor(dail_conf)
        asyncio.run(predictor.run())


async def run_dail_async(config: ModelEvalConfig):
    futures = []
    for run_conf in config.get_run_confs():
        dail_conf = DailConfig(run_conf)
        predictor = DailPredictor(dail_conf)
        futures.append(predictor.run())
        print(f"Running for conf = {run_conf}")
    await asyncio.gather(*futures)
