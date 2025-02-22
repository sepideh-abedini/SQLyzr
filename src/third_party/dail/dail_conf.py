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
        'max_tokens': 600,
        'n': 5
    }

    def test_schema_path(self):
        return f"{self.pred_path}.test.schema.jsonl"

    def train_schema_path(self):
        return f"{self.pred_path}.train.schema.jsonl"

    def pre_test_result_path(self):
        return f"{self.pred_path}.pre_test_result.txt"

    def questions_path(self):
        return f"{self.pred_path}.questions.json"

    def second_questions_path(self):
        return f"{self.pred_path}.second.questions.json"

    def get_path(self, file_type: Literal["in", "out","in.second","out.second"]):
        return f"{self.pred_path}.sql.{file_type}.jsonl"
