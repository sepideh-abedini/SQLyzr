import asyncio
from abc import ABC, abstractmethod

from src.eval.model_eval_config import ModelEvalConfig
from src.eval.single_run_config import SingleRunConfig
from src.third_party.dail.dail_conf import DailConfig
from src.third_party.dail.dail_pred import DailPredictor
from src.third_party.din.config import DinConfig
from src.third_party.din.din_pred import DinPredictor
from src.util.system_utils import ProcessUsage


class ModelRunner(ABC):
    config: ModelEvalConfig

    def __init__(self, config: ModelEvalConfig):
        self.config = config

    async def run(self):
        futures = []
        for run_conf in self.config.get_run_confs():
            future = self.run_single(run_conf)
            futures.append(future)
            print(f"Running for conf = {run_conf}")
        await asyncio.gather(*futures)

    async def run_single(self, run_conf: SingleRunConfig):
        result = await self.run_single_internal(run_conf)
        ProcessUsage.dump_proc_usage(run_conf.get_util_path())
        return result

    @abstractmethod
    async def run_single_internal(self, run_conf: SingleRunConfig):
        pass


class DailRunner(ModelRunner):

    async def run_single_internal(self, run_conf: SingleRunConfig):
        dail_conf = DailConfig(run_conf)
        predictor = DailPredictor(dail_conf)
        result = await predictor.run()
        return result


class DinRunner(ModelRunner):
    async def run_single_internal(self, run_conf: SingleRunConfig):
        din_conf = DinConfig(run_conf)
        predictor = DinPredictor(din_conf)
        result = await predictor.run()
        return result


def run_din(config: ModelEvalConfig):
    for run_conf in config.get_run_confs():
        din_conf = DinConfig(run_conf)
        predictor = DinPredictor(din_conf)
        asyncio.run(predictor.run())
        print(f"Run started for conf = {run_conf}")


def run_dail(config: ModelEvalConfig):
    for run_conf in config.get_run_confs():
        dail_conf = DailConfig(run_conf)
        predictor = DailPredictor(dail_conf)
        asyncio.run(predictor.run())
