from dataclasses import dataclass

from src.evaluation.runner.dataset_config import DatasetConfig


@dataclass
class RunnerConfig:
    dataset_config: DatasetConfig
    output_path: str
    temp: float
