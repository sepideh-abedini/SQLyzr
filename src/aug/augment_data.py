import asyncio

from src.aug.auger import Auger
from src.eval.model_eval_config import ModelEvalConfig


def augment_data(config: ModelEvalConfig):
    auger = Auger("data/aug/gen.jsonl", CAT_2, "concert_singer", config.dataset_config)
    asyncio.run(auger.run())
