from dataclasses import dataclass

from src.configs.eval import DIN_SPIDER_DEV_EVAL, DIN_SPIDER_SMALL_EVAL, DAIL_SPIDER_SMALL_EVAL, DIN_BIRD_SMALL_EVAL, \
    DAIL_SPIDER_DEV_EVAL, DIN_BIRD_DEV_EVAL
from src.eval.model_eval_config import ModelEvalConfig


@dataclass
class SQLyzrConfig:
    eval_conf: ModelEvalConfig
    aug_out: str
    error_threshold: float
    aug_per_sub_cat: int = 2


DIN_SPIDER_SMALL = SQLyzrConfig(
    eval_conf=DIN_SPIDER_SMALL_EVAL,
    aug_out="data/aug/gen.jsonl",
    error_threshold=80,
)

DIN_SPIDER_DEV = SQLyzrConfig(
    eval_conf=DIN_SPIDER_DEV_EVAL,
    aug_out="data/aug/gen.jsonl",
    error_threshold=80,
)

DAIL_SPIDER_SMALL = SQLyzrConfig(
    eval_conf=DAIL_SPIDER_SMALL_EVAL,
    aug_out="data/aug/gen.jsonl",
    error_threshold=80,
)

DAIL_SPIDER_DEV = SQLyzrConfig(
    eval_conf=DAIL_SPIDER_DEV_EVAL,
    aug_out="data/aug/gen.jsonl",
    error_threshold=80,
)

DIN_BIRD_SMALL = SQLyzrConfig(
    eval_conf=DIN_BIRD_SMALL_EVAL,
    aug_out="data/aug/gen.jsonl",
    error_threshold=80,
)

DIN_BIRD_DEV = SQLyzrConfig(
    eval_conf=DIN_BIRD_DEV_EVAL,
    aug_out="data/aug/gen.jsonl",
    error_threshold=80,
)
