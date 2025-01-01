import os.path
from dataclasses import dataclass
from typing import Literal

from src.eval.runner_config import SingleRunConfig


@dataclass
class DinConfig:
    out_path: str
    force: bool = False
    model: str = "gpt-3.5-turbo"

    def get_path(self, file_name: Literal['schema', 'classif', 'sql', 'sql_debug'], file_type: Literal['in', 'out']):
        return f"{self.out_path}.{file_name}.{file_type}.jsonl"
