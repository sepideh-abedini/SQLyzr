from src.configs.sqlyzr import SQLyzrConfig
from src.sqlyzr.augment_data import augment_data
from src.sqlyzr.config_loader import load_config
from src.sqlyzr.evaluator import post_process_scores, calc_scores
from src.sqlyzr.model_runner import run_model
from src.sqlyzr.transformer_eval import find_transformers, post_process_transformers
from src.sqlyzr.validate import validate_dataset


class Sqlyzr:
    conf: SQLyzrConfig

    def __init__(self):
        self.conf = load_config()

    async def run(self):
        if self.conf.pipeline.verify:
            validate_dataset(self.conf)

        if self.conf.pipeline.predict:
            await run_model(self.conf)

        if self.conf.pipeline.eval:
            await calc_scores(self.conf)
            post_process_scores(self.conf)

        if self.conf.pipeline.transformers:
            await find_transformers(self.conf)
            post_process_transformers(self.conf)

        if self.conf.pipeline.augment:
            await augment_data(self.conf)
