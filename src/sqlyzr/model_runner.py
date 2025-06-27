import os
from abc import ABC, abstractmethod
from collections import defaultdict

from loguru import logger

from src.configs.sqlyzr_config import SQLyzrConfig
from src.eval.single_run_config import SingleRunConfig
from src.sqlyzr.dummy_predictor import DummyPredictor
from src.third_party.dail.dail_pred import DailPredictor
from src.third_party.din.din_bird_pred import DinBirdPredictor
from src.third_party.din.din_spider_pred import DinPredictor
from src.util.log_util import alog


class ModelRunner(ABC):
    @alog("Model execution")
    async def run_single(self, run_conf: SingleRunConfig):
        logger.info(f"Running model for conf: {run_conf}")
        await self.run_single_internal(run_conf)
        logger.info(f"Finished prediction: {run_conf.get_pred_path()}")

    @abstractmethod
    async def run_single_internal(self, run_conf: SingleRunConfig):
        pass


class DailRunner(ModelRunner):

    async def run_single_internal(self, run_conf: SingleRunConfig):
        predictor = DailPredictor(run_conf)
        await predictor.run()


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

