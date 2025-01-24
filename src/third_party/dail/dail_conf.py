from dataclasses import dataclass
from typing import Literal

from src.eval.single_run_config import SingleRunConfig


@dataclass
class DailConfig:
    pred_path: str
    force: bool = False
    compute_cv_link: bool = True
    params = {
        'model': "gpt-4o-mini",
        'n': 5
    }

    def schema_path(self):
        return f"{self.pred_path}.schema.jsonl"

    def questions_path(self):
        return f"{self.pred_path}.questions.json"

    def get_path(self, file_type: Literal["in", "out"]):
        return f"{self.pred_path}.sql.{file_type}.jsonl"
