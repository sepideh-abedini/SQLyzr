import os
from dataclasses import dataclass
from pathlib import Path

from src.eval.dataset_config import DatasetConfig
from src.util.file_utils import get_num_lines


@dataclass(frozen=True)
class SingleRunConfig:
    dataset_config: DatasetConfig
    pred_dir: str
    trs_dir: str
    temp: float
    itr: int
    pred_file_name: str = "pred"
    usage_file_name: str = "usage"
    trs_file_name: str = "trs"
    batch: bool = False

    def __post_init__(self):
        os.makedirs(Path(self.get_pred_path()).parent, exist_ok=True)
        os.makedirs(Path(self.get_trs_path()).parent, exist_ok=True)

    def get_pred_path(self):
        return os.path.join(self.pred_dir, self.dataset_config.dataset_type,
                            f"{self.pred_file_name}_{self.temp}_{self.itr}.txt")

    def get_usage_path(self):
        return f"{self.get_pred_path()}.usage.json"

    def get_trs_path(self):
        return os.path.join(self.trs_dir, self.dataset_config.dataset_type,
                            f"{self.trs_file_name}_{self.temp}_{self.itr}.csv")

    def is_pred_file_valid(self):
        return os.path.exists(self.get_pred_path()) and get_num_lines(self.get_pred_path()) == get_num_lines(
            self.dataset_config.get_gold_path())

    def __str__(self):
        return f"temp = {self.temp}, iter={self.itr}"

    def __repr__(self):
        return str(self)
