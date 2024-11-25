import os
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import List, Dict

from src.evaluation.runner.dataset_config import DatasetConfig
from src.evaluation.runner.runner_config import SingleRunConfig


@dataclass
class ModelEvalConfig:
    run_confs: Dict[float, List[SingleRunConfig]]
    eval_dir: str
    pred_dir: str

    def __init__(self, temps: List[float], num_itrs: int, pred_dir: str, eval_dir: str, dataset_config: DatasetConfig):
        self.pred_dir = pred_dir
        self.eval_dir = eval_dir
        self.run_confs = {}
        for temp, itr in product(temps, range(num_itrs)):
            conf = SingleRunConfig(dataset_config=dataset_config,
                                   pred_dir=pred_dir,
                                   eval_dir=eval_dir,
                                   temp=temp,
                                   itr=itr)
            self.run_confs.setdefault(temp, []).append(conf)

    def get_run_confs(self):
        return list([conf for ll in self.run_confs.values() for conf in ll])

    def get_runner_conf(self, temp: float, itr: int):
        return self.runner_configs[temp][itr]

    def get_scores_path(self, sub: str = ""):
        return os.path.join(self.eval_dir, f"scores_{sub}.csv")
