import os
from dataclasses import dataclass, replace

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

    def get_pred_path(self):
        return os.path.join(self.pred_dir, f"{self.pred_file_name}_{self.temp}_{self.itr}.txt")

    def is_pred_file_valid(self):
        return os.path.exists(self.get_pred_path()) and get_num_lines(self.get_pred_path()) == get_num_lines(
            self.dataset_config.get_gold_path()) + 1

    def get_eval_data_path(self):
        return os.path.join(self.eval_dir, f"eval_{self.temp}_{self.itr}.json")

    def get_eval_gold_path_per_cat(self, cat: str):
        return os.path.join(self.eval_dir, f"gold_{self.temp}_{self.itr}_{cat}.txt")

    def get_eval_pred_path_per_cat(self, cat: str):
        return os.path.join(self.eval_dir, f"pred_{self.temp}_{self.itr}_{cat}.txt")

    def to_thread_conf(self, chunk_num: int):
        return replace(self,
                       dataset_config=self.dataset_config.to_thread_conf(chunk_num),
                       pred_file_name=f"{self.pred_file_name}_thread_{chunk_num}")
