import os.path
from dataclasses import dataclass
from typing import Literal

from src.configs.eval import DIN_SPIDER_DEV_EVAL, DIN_SPIDER_SMALL_EVAL, DAIL_SPIDER_SMALL_EVAL, DIN_BIRD_SMALL_EVAL, \
    DAIL_SPIDER_DEV_EVAL, DIN_BIRD_DEV_EVAL
from src.eval.model_eval_config import ModelEvalConfig


@dataclass
class SQLyzrConfig:
    eval_conf: ModelEvalConfig
    model: Literal["din", "dail"]
    aug_dir: str
    error_threshold: float
    rel_dir: str
    aug_per_sub_cat: int = 2

    def get_aug_out(self):
        return os.path.join(self.aug_dir, "gen.jsonl")


DIN_SPIDER_SMALL = SQLyzrConfig(
    eval_conf=DIN_SPIDER_SMALL_EVAL,
    aug_dir="data/aug",
    error_threshold=101,
    model="din",
    rel_dir="data/rel"
)

DIN_SPIDER_DEV = SQLyzrConfig(
    eval_conf=DIN_SPIDER_DEV_EVAL,
    aug_dir="data/aug",
    error_threshold=80,
    model="dail",
    rel_dir="data/rel"
)

DAIL_SPIDER_SMALL = SQLyzrConfig(
    eval_conf=DAIL_SPIDER_SMALL_EVAL,
    aug_dir="data/aug",
    error_threshold=80,
    model="dail",
    rel_dir="data/rel"
)

DAIL_SPIDER_DEV = SQLyzrConfig(
    eval_conf=DAIL_SPIDER_DEV_EVAL,
    aug_dir="data/aug",
    error_threshold=80,
    model="dail",
    rel_dir="data/rel"
)

DIN_BIRD_SMALL = SQLyzrConfig(
    eval_conf=DIN_BIRD_SMALL_EVAL,
    aug_dir="data/aug",
    error_threshold=80,
    model="din",
    rel_dir="data/rel"
)

DIN_BIRD_DEV = SQLyzrConfig(
    eval_conf=DIN_BIRD_DEV_EVAL,
    aug_dir="data/aug",
    error_threshold=80,
    model="din",
    rel_dir="data/rel"
)
