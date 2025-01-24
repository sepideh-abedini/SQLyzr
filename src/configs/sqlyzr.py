import os.path
from dataclasses import dataclass
from typing import Literal

from src.eval.model_eval_config import ModelEvalConfig
from src.sqlyzr.pipeline_config import PipelineConfig


@dataclass
class SQLyzrConfig:
    eval_conf: ModelEvalConfig
    model: Literal["din", "dail"]
    aug_dir: str
    error_threshold: float
    aug_per_sub_cat: int = 2
    pipeline: PipelineConfig = PipelineConfig

    def get_aug_out(self):
        return os.path.join(self.aug_dir, "gen.jsonl")
