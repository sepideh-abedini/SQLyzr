from dataclasses import dataclass

from src.eval.configs import DIN_SMALL_CONF, DAIL_SMALL_CONF
from src.eval.model_eval_config import ModelEvalConfig


@dataclass
class SQLyzrConfig:
    eval_conf: ModelEvalConfig
    aug_out: str
    aug_db_id: str


DIN_SPIDER_SMALL = SQLyzrConfig(
    eval_conf=DIN_SMALL_CONF,
    aug_out="data/aug/gen.jsonl",
    aug_db_id="concert_singer"
)

DAIL_SPIDER_SMALL = SQLyzrConfig(
    eval_conf=DAIL_SMALL_CONF,
    aug_out="data/aug/gen.jsonl",
    aug_db_id="concert_singer"
)
