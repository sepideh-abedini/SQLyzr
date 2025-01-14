from src.configs.sqlyzr import SQLyzrConfig
from src.sqlyzr.augment_data import augment_data
from src.sqlyzr.config_loader import load_config
from src.sqlyzr.evaluator import calc_scores, post_process_scores
from src.sqlyzr.model_runner import run_model
from src.sqlyzr.transformer_eval import find_transformers
from src.sqlyzr.validate import validate_dataset


class Sqlyzr:
    conf: SQLyzrConfig

    def __init__(self):
        self.conf = load_config()

    async def run(self):
        validate_dataset(self.conf)

        await run_model(self.conf)

        calc_scores(self.conf)

        post_process_scores(self.conf)

        await find_transformers(self.conf)

        await augment_data(self.conf)
