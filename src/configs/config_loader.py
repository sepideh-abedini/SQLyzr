import os.path
from typing import Literal, List, Tuple

from loguru import logger
from pydantic import BaseModel

from src.configs.datasets import DatasetName, DatasetSize, DATASETS
from src.configs.metrics import SPIDER_METRICS, BIRD_METRICS, METRICS
from src.configs.sqlyzr_config import SQLyzrConfig
from src.eval.model_eval_config import ModelEvalConfig
from src.eval.single_run_config import ModelName
from src.sqlyzr.chart_config import ChartName
from src.sqlyzr.pipeline_config import PipelineConfig


class ConfigData(BaseModel):
    data_dir: str = "data"
    aug_per_sub_cat: int = 2
    error_threshold: float = 101
    dataset: DatasetName = "spider"
    dataset_size: DatasetSize = "small"
    temps: List[float] = [0.0]
    itrs: int = 2
    models: List[ModelName]
    batch: bool = False
    force: bool = False
    pipeline: PipelineConfig = PipelineConfig()
    charts: List[ChartName] = []

    def get_model_dataset_dir(self):
        return os.path.join(self.data_dir, f"{'-'.join(self.models)}_{self.dataset}_{self.dataset_size}")

    def get_aug_dir(self):
        return os.path.join(self.get_model_dataset_dir(), "aug")

    def get_pred_dir(self):
        return os.path.join(self.get_model_dataset_dir(), "pred")

    def get_eval_dir(self):
        return os.path.join(self.get_model_dataset_dir(), "eval")

    def get_trs_dir(self):
        return os.path.join(self.get_model_dataset_dir(), "trs")

    def get_charts_dir(self):
        return os.path.join(self.get_model_dataset_dir(), "charts")

    @staticmethod
    def load(path: str):
        with open(path) as file:
            data = ConfigData.model_validate_json(file.read())
            return data

    def __str__(self):
        return f"""
############ SQLyzr Config ############
Dataset: {self.dataset}
Dataset Size: {self.dataset_size}
Models: {self.models}
Batch: {self.batch}
Temps: {self.temps}
Itrs: {self.itrs}
Pipeline: {self.pipeline}
#######################################
"""


def load_config(path) -> SQLyzrConfig:
    conf_data = ConfigData.load(path)
    logger.info(conf_data)
    dataset_confs = DATASETS[conf_data.dataset][conf_data.dataset_size]
    dirs = [conf_data.get_pred_dir(), conf_data.get_eval_dir(), conf_data.get_aug_dir(), conf_data.get_trs_dir(),
            conf_data.get_charts_dir()]
    for d in dirs:
        if conf_data.force:
            os.rmdir(d)
        os.makedirs(d, exist_ok=True)
    eval_conf = ModelEvalConfig(
        temps=conf_data.temps,
        num_itrs=conf_data.itrs,
        pred_dir=conf_data.get_pred_dir(),
        eval_dir=conf_data.get_eval_dir(),
        trs_dir=conf_data.get_trs_dir(),
        charts_dir=conf_data.get_charts_dir(),
        dataset_configs=dataset_confs,
        metrics=METRICS[conf_data.dataset],
        batch=conf_data.batch,
        included_charts=conf_data.charts,
        models=conf_data.models
    )
    conf = SQLyzrConfig(
        eval_conf=eval_conf,
        aug_dir=conf_data.get_aug_dir(),
        error_threshold=conf_data.error_threshold,
        aug_per_sub_cat=conf_data.aug_per_sub_cat,
        pipeline=conf_data.pipeline
    )

    return conf
