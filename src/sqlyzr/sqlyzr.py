from src.configs.config_loader import load_config
from src.configs.sqlyzr_config import SQLyzrConfig
from src.sqlyzr.augment_data import DatasetAugmentor
from src.sqlyzr.model_runner import run_model
from src.sqlyzr.score_calculator import ScoreCalculator
from src.sqlyzr.scores_post_processor import ScoresPostProcessor
from src.sqlyzr.transformer_eval import TransformerFinder
from src.sqlyzr.validate import validate_dataset


class Sqlyzr:
    conf: SQLyzrConfig

    def __init__(self):
        self.conf = load_config()

    async def run(self):
        if self.conf.pipeline.verify:
            await validate_dataset(self.conf)

        if self.conf.pipeline.predict:
            await run_model(self.conf)

        if self.conf.pipeline.eval:
            calc = ScoreCalculator(self.conf)
            calc.calc_scores()
            post_processor = ScoresPostProcessor(self.conf)
            post_processor.run()

        if self.conf.pipeline.transformers:
            trs_finder = TransformerFinder(self.conf)
            await trs_finder.run()
            trs_finder.post_process()

        if self.conf.pipeline.augment:
            augmentor = DatasetAugmentor(self.conf)
            await augmentor.augment_data()
