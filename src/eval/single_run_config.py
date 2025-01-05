import os
from dataclasses import dataclass

from src.eval.dataset_config import DatasetConfig
from src.util.file_utils import get_num_lines


@dataclass
class SingleRunConfig:
    dataset_config: DatasetConfig
    pred_dir: str
    eval_dir: str
    temp: float
    itr: int
    pred_file_name: str = "pred"
    token_file_name: str = "tokens"
    stats_file_name: str = "stats"
    batch: bool = False

    def get_pred_path(self):
        return os.path.join(self.pred_dir, f"{self.pred_file_name}_{self.temp}_{self.itr}.txt")

    def get_token_path(self):
        return os.path.join(self.pred_dir, f"{self.token_file_name}_{self.temp}_{self.itr}.txt")

    def get_stats_path(self):
        return os.path.join(self.pred_dir, f"{self.stats_file_name}_{self.temp}_{self.itr}.json")

    def is_pred_file_valid(self):
        return os.path.exists(self.get_pred_path()) and get_num_lines(self.get_pred_path()) == get_num_lines(
            self.dataset_config.get_gold_path())

    def __str__(self):
        return f"temp = {self.temp}, iter={self.itr}"
