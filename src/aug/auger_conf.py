import os.path
from dataclasses import dataclass


@dataclass
class AugerConf:
    aug_dir: str
    num_examples: int = 1
    gen_in: str = "gen.in.jsonl"
    gen_out: str = "gen.out.jsonl"
    gpt_params = {
        'model': "gpt-4o-mini",
        'max_tokens': 600
    }

    def get_aug_in(self):
        return os.path.join(self.aug_dir, self.gen_in)

    def get_aug_out(self):
        return os.path.join(self.aug_dir, self.gen_out)


DEFAULT_CONF = AugerConf(
    aug_dir="data/aug",
    gen_in="gen.in.jsonl",
    gen_out="gen.out.jsonl",
    num_examples=1
)
