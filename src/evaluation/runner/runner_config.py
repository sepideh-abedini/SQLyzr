import os
from dataclasses import dataclass

from src.evaluation.runner.dataset_config import DatasetConfig


@dataclass
class SingleRunConfig:
    dataset_config: DatasetConfig
    pred_dir: str
    eval_dir: str
    temp: float
    itr: int

    def get_pred_path(self):
        return os.path.join(self.pred_dir, f"pred_{self.temp}_{self.itr}.txt")

    def get_eval_data_path(self):
        return os.path.join(self.eval_dir, f"eval_{self.temp}_{self.itr}.json")

    def get_eval_gold_path_per_cat(self, cat: str):
        return os.path.join(self.eval_dir, f"gold_{self.temp}_{self.itr}_{cat}.txt")

    def get_eval_pred_path_per_cat(self, cat: str):
        return os.path.join(self.eval_dir, f"pred_{self.temp}_{self.itr}_{cat}.txt")
