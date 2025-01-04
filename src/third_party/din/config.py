from dataclasses import dataclass
from typing import Literal

from src.eval.single_run_config import SingleRunConfig


@dataclass
class DinConfig:
    run_conf: SingleRunConfig
    force: bool = False
    model: str = "gpt-4o-mini"
    # model: str = "gpt-3.5-turbo"

    def get_path(self, file_name: Literal['schema', 'classif', 'sql', 'sql_debug'], file_type: Literal['in', 'out']):
        return f"{self.run_conf.get_pred_path()}.{file_name}.{file_type}.jsonl"
