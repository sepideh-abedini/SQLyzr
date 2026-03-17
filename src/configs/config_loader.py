import os.path
import shutil
from typing import List, Optional

from loguru import logger
from natsort import natsorted
from pydantic import BaseModel

from src.configs.datasets import DatasetName, DatasetSize, DATASETS
from src.configs.metrics import METRICS
from src.configs.sqlyzr_config import SQLyzrConfig
from src.eval.model_eval_config import ModelEvalConfig
from src.eval.single_run_config import ModelName
from src.sqlyzr.chart_config import ChartName
from src.sqlyzr.pipeline_config import PipelineConfig


class ConfigData(BaseModel):
    data_dir: str = "data"
    out_dir: str = "out"
    aug_per_sub_cat: int = 2
    error_threshold: float = 101
    dataset: DatasetName = "spider"
    dataset_size: DatasetSize = "small"
    dataset_versions: List[str] = []
    temps: List[float] = [0.0]
    itrs: int = 2
    models: List[ModelName]
    batch: bool = False
    force: bool = False
    pipeline: PipelineConfig = PipelineConfig()
    charts: List[ChartName] = []
    etcr: float = 1.1

    @property
    def last_version(self):
        last_version = max(self.dataset_versions, key=lambda x: int(x[1:]))
        return last_version

    @property
    def idx(self):
        return f"{'_'.join(self.models)}_{self.dataset}_{self.dataset_size}"

    @property
    def dataset_id(self):
        # if self.dataset_version:
        #     return f"{self.dataset}/{self.dataset_version}"
        # else:
        return self.dataset

    def get_model_dataset_dir(self):
        return os.path.join(self.out_dir, f"{'-'.join(natsorted(self.models))}_{self.dataset_size}_{self.dataset_id}")

    def get_aug_dir(self):
        return os.path.join(self.get_model_dataset_dir(), "aug", self.last_version)

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

    def save(self, path):
        with open(path, 'w') as file:
            file.write(self.model_dump_json(indent=4))

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
Charts: {self.charts}
#######################################
"""


def load_config(path) -> SQLyzrConfig:
    conf_data = ConfigData.load(path)
    logger.debug(conf_data)
    dataset_confs = DATASETS[conf_data.dataset]
    dataset_confs = dataset_confs[conf_data.dataset_size]
    versioned_dataset_confs = []
    for conf in dataset_confs:
        for version in conf_data.dataset_versions:
            versioned_dataset_confs.append(conf.to_ver(version))
    dirs = [conf_data.get_pred_dir(), conf_data.get_eval_dir(), conf_data.get_aug_dir(), conf_data.get_trs_dir(),
            conf_data.get_charts_dir()]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    eval_conf = ModelEvalConfig.create(
        temps=conf_data.temps,
        num_itrs=conf_data.itrs,
        base_dir=conf_data.get_model_dataset_dir(),
        pred_dir=conf_data.get_pred_dir(),
        eval_dir=conf_data.get_eval_dir(),
        trs_dir=conf_data.get_trs_dir(),
        charts_dir=conf_data.get_charts_dir(),
        dataset_configs=versioned_dataset_confs,
        metrics=METRICS[conf_data.dataset],
        batch=conf_data.batch,
        included_charts=conf_data.charts,
        models=conf_data.models
    )
    conf = SQLyzrConfig(
        idx=conf_data.idx,
        eval_conf=eval_conf,
        aug_dir=conf_data.get_aug_dir(),
        error_threshold=conf_data.error_threshold,
        aug_per_sub_cat=conf_data.aug_per_sub_cat,
        pipeline=conf_data.pipeline,
        etc_ratio=conf_data.etcr,
    )

    return conf
