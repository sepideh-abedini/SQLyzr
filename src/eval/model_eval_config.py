import os
from dataclasses import dataclass
from itertools import product
from typing import List, Dict, Type

from src.eval.dataset_config import DatasetConfig
from src.eval.metrics import Metric
from src.eval.single_run_config import SingleRunConfig


@dataclass
class ModelEvalConfig:
    run_confs: Dict[float, List[SingleRunConfig]]
    eval_dir: str
    pred_dir: str
    dataset_config: DatasetConfig
    metrics: Dict[str, Type[Metric]]
    force: bool = False

    def __init__(self, temps: List[float], num_itrs: int, pred_dir: str, eval_dir: str, dataset_config: DatasetConfig,
                 metrics: Dict[str, Type[Metric]]):
        self.pred_dir = pred_dir
        self.eval_dir = eval_dir
        self.run_confs = {}
        self.dataset_config = dataset_config
        for temp, itr in product(temps, range(num_itrs)):
            conf = SingleRunConfig(dataset_config=dataset_config,
                                   pred_dir=pred_dir,
                                   eval_dir=eval_dir,
                                   temp=temp,
                                   itr=itr)
            self.run_confs.setdefault(temp, []).append(conf)
        self.metrics = metrics

    def get_run_confs(self):
        return list([conf for ll in self.run_confs.values() for conf in ll])

    def get_runner_conf(self, temp: float, itr: int):
        return self.run_confs[temp][itr]

    def get_raw_scores_path(self):
        return os.path.join(self.eval_dir, f"scores_raw.csv")

    def get_scores_path(self, sub: str = ""):
        return os.path.join(self.eval_dir, f"scores{sub}.csv")

    def get_metric_names(self):
        return list(self.metrics.keys())
