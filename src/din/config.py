from dataclasses import dataclass

from src.eval.runner_config import SingleRunConfig


@dataclass
class DinConfig:
    schema_in: str
    schema_out: str
    classif_in: str
    classif_out: str
    sql_in: str
    sql_out: str
    sql_debug_in: str
    sql_debug_out: str
    force: bool


DEFAULT_CONF = DinConfig(
    schema_in="data/din/schema.in.jsonl",
    schema_out="data/din/schema.out.jsonl",
    classif_in="data/din/classif.in.jsonl",
    classif_out="data/din/classif.out.jsonl",
    sql_in="data/din/sql.in.jsonl",
    sql_out="data/din/sql.out.jsonl",
    sql_debug_in="data/din/sql_debug.in.jsonl",
    sql_debug_out="data/din/sql_debug.out.jsonl",
    force=False
)
