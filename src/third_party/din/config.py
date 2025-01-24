from dataclasses import dataclass
from typing import Literal


@dataclass
class DinConfig:
    pred_path: str
    default_params = {
        'model': "gpt-4o-mini",
        'max_completion_tokens': 600,
        'stop': ["Q:"]
    }
    debug_params = {
        'model': "gpt-3.5-turbo",
        "max_completion_tokens": 350,
        "stop": ["#", ";", "\n\n"]
    }

    # model: str = "gpt-3.5-turbo"

    def get_path(self, file_name: Literal['schema', 'classif', 'sql', 'sql_debug'], file_type: Literal['in', 'out']):
        return f"{self.pred_path}.{file_name}.{file_type}.jsonl"
