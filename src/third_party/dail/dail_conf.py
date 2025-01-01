from dataclasses import dataclass
from typing import Literal

from src.eval.runner_config import SingleRunConfig


@dataclass
class DailConfig:
    run_conf: SingleRunConfig
    force: bool = False
    compute_cv_link: bool = True
    model: str = "gpt-4o-mini"

    def schema_path(self):
        return f"{self.run_conf.get_pred_path()}.schema.jsonl"

    def questions_path(self):
        return f"{self.run_conf.get_pred_path()}.questions.json"
