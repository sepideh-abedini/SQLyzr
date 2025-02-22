from dataclasses import dataclass, field
from typing import Literal

from src.eval.single_run_config import SingleRunConfig


@dataclass
class DailParams:
    max_seq_len: int = 4096
    max_ans_len: int = 200
    tokenizer: str = 'gpt-3.5-turbo'
    prompt_repr: str = 'SQL'
    k_shot: int = 9
    example_type: str = 'QA'
    selector_type: str = 'EUCDISQUESTIONMASK'
    second_selector_type: str = 'EUCDISMASKPRESKLSIMTHR'
    scope_factor: int = 100
    split: str = "test"


@dataclass
class DailConfig:
    pred_path: str
    force: bool = False
    compute_cv_link: bool = True
    params: DailParams = field(default_factory=DailParams)
    gpt_params = {
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

    def get_path(self, file_type: Literal["in", "out", "in.second", "out.second"]):
        return f"{self.pred_path}.sql.{file_type}.jsonl"
