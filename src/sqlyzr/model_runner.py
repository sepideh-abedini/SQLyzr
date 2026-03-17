from abc import ABC, abstractmethod

from loguru import logger

from src.eval.lib import Timer
from src.eval.single_run_config import SingleRunConfig
from src.monitor.mem import track_memory_async
from src.pred.simple_predictor import SimplePredictor
from src.pred.simple_predictor_resd import SimplePredictorRESD
from src.pred.simple_predictor_v2 import SimplePredictorV2
from src.sqlyzr.dummy_predictor import DummyPredictor
from src.third_party.dail.dail_pred import DailPredictor
from src.third_party.din.din_bird_pred import DinBirdPredictor
from src.third_party.din.din_spider_pred import DinPredictor
from src.util.file_utils import write_json
from src.util.log_util import alog


class ModelRunner(ABC):
    @alog("Model execution")
    async def run_single(self, run_conf: SingleRunConfig):
        logger.info(f"Running model for conf: {run_conf}")
        timer = Timer.start()
        _, avg_mem, peak_mem = await track_memory_async(self.run_single_internal, run_conf)
        total_time = timer.lap()
        logger.info(f"TOTAL PRED TIME: {total_time}")
        logger.info(f"AVG MEM: {avg_mem}")
        logger.info(f"PEAK MEM: {peak_mem}")
        perf_stat = {"total_time": total_time, "avg_mem": avg_mem, "peak_mem": peak_mem}
        write_json(f"{run_conf.get_pred_path()}.stats.json", perf_stat)
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


class SimpleRunner(ModelRunner):
    async def run_single_internal(self, run_conf: SingleRunConfig):
        predictor = SimplePredictor(run_conf)
        result = await predictor.run()
        return result


class SimpleRunnerV2(ModelRunner):
    async def run_single_internal(self, run_conf: SingleRunConfig):
        predictor = SimplePredictorV2(run_conf)
        result = await predictor.run()
        return result
