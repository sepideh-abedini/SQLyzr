from dataclasses import dataclass


@dataclass
class AugerConf:
    gen_in: str
    gen_out: str
    num_examples: int
    gen_num: int


DEFAULT_CONF = AugerConf(
    gen_in="data/aug/gen.in.jsonl",
    gen_out="data/aug/gen.out.jsonl",
    num_examples=1,
    gen_num=5
)
