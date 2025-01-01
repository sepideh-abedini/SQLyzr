from dataclasses import dataclass
from typing import Literal

from src.eval.single_run_config import SingleRunConfig


@dataclass
class DailConfig:
    run_conf: SingleRunConfig
    batch: bool = False
    force: bool = False
    compute_cv_link: bool = True
    model: str = "gpt-3.5-turbo"
    self_consistent_set_size: int = 5

    def schema_path(self):
        return f"{self.run_conf.get_pred_path()}.schema.jsonl"

    def questions_path(self):
        return f"{self.run_conf.get_pred_path()}.questions.json"

    def get_batch_path(self, file_type: Literal["in", "out"]):
        return f"{self.run_conf.get_pred_path()}.sql.{file_type}.jsonl"
