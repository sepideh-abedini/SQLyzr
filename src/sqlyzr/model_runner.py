import asyncio
import os
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, Future

from src.configs.sqlyzr_config import SQLyzrConfig
from src.eval.model_eval_config import ModelEvalConfig
from src.eval.single_run_config import SingleRunConfig
from src.sqlyzr.dummy_predictor import DummyPredictor
from src.third_party.dail.dail_pred import DailPredictor
from loguru import logger

from src.third_party.din.din_bird_pred import DinBirdPredictor
from src.third_party.din.din_spider_pred import DinPredictor
from src.util.multi_thread_utils import get_thread_pool

RUNNER_THREADS = int(os.environ.get("RUNNER_THREADS", 1))


class ModelRunner(ABC):
    config: ModelEvalConfig

    def __init__(self, config: ModelEvalConfig):
        self.config = config

    async def run(self):
        for conf in self.config.get_run_confs():
            res = await self.run_single(conf)

    async def run_single(self, run_conf: SingleRunConfig):
        logger.info(f"Running for conf={run_conf}")
        result = await self.run_single_internal(run_conf)
        return result

    @abstractmethod
    async def run_single_internal(self, run_conf: SingleRunConfig):
        pass


class DailRunner(ModelRunner):

    async def run_single_internal(self, run_conf: SingleRunConfig):
        predictor = DailPredictor(run_conf)
        result = await predictor.run()
        return result


class DinRunner(ModelRunner):
    async def run_single_internal(self, run_conf: SingleRunConfig):
        if run_conf.dataset_config.dataset_type == "bird":
            predictor = DinBirdPredictor(run_conf)
        else:
            predictor = DinPredictor(run_conf)
        result = await predictor.run()
        return result


class DummyRunner(ModelRunner):
    async def run_single_internal(self, run_conf: SingleRunConfig):
        predictor = DummyPredictor(run_conf)
        result = await predictor.run()
        return result


MODELS = {
    "din": DinRunner,
    "dail": DailRunner,
    "dum": DummyRunner
}


async def run_model(config: SQLyzrConfig):
    model_type = MODELS[config.model]
    logger.info(f"Running model: {model_type}")
    runner = model_type(config.eval_conf)
    await runner.run()
