import os.path
from dataclasses import dataclass
from typing import Literal

from src.eval.model_eval_config import ModelEvalConfig
from src.sqlyzr.pipeline_config import PipelineConfig


@dataclass(frozen=True)
class SQLyzrConfig:
    eval_conf: ModelEvalConfig
    aug_dir: str
    error_threshold: float
    etc_ratio: float = 1.1
    aug_per_sub_cat: int = 2
    pipeline: PipelineConfig = PipelineConfig

    def get_aug_out(self):
        return os.path.join(self.aug_dir, "gen.jsonl")

    def __str__(self):
        return f"""
######## SQLyzr Config ########
Eval Config:
  Pred Directory: {self.eval_conf.pred_dir}
  Eval Directory: {self.eval_conf.eval_dir}
  TRS Directory: {self.eval_conf.trs_dir}
  Metrics: {', '.join(self.eval_conf.get_metric_names())}
  Dataset Configs: {len(self.eval_conf.dataset_configs)}
  Run Configurations: {len(self.eval_conf.get_run_confs())}
"""
