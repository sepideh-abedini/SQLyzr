from loguru import logger

from src.chart.charter import draw_all_charts
from src.configs.config_loader import load_config
from src.configs.sqlyzr_config import SQLyzrConfig
from src.sqlyzr.augment_data import DatasetAugmentor
from src.sqlyzr.model_runner import run_model
from src.sqlyzr.pipeline_config import PipelineConfig
from src.sqlyzr.score_calculator import ScoreCalculator
from src.sqlyzr.scores_post_processor import ScoresPostProcessor
from src.sqlyzr.transformer_eval import TransformerFinder
from src.sqlyzr.validate import validate_dataset


class Sqlyzr:
    conf: SQLyzrConfig

    def __init__(self, conf_path: str):
        self.conf = load_config(conf_path)

    async def run(self):
        run_status = PipelineConfig.init()

        if self.conf.pipeline.verify:
            await validate_dataset(self.conf.eval_conf.dataset_configs)
            run_status.verify = True

        if self.conf.pipeline.predict:
            await run_model(self.conf)
            run_status.predict = True

        if self.conf.pipeline.eval:
            calc = ScoreCalculator(self.conf)
            calc.calc_scores()
            post_processor = ScoresPostProcessor(self.conf)
            post_processor.run()
            run_status.eval = True

        if self.conf.pipeline.charts:
            draw_all_charts(self.conf.eval_conf.get_raw_scores_path(),
                            out_dir=self.conf.eval_conf.charts_dir,
                            included_charts=self.conf.eval_conf.included_charts)
            run_status.charts = True

        if self.conf.pipeline.transformers:
            trs_finder = TransformerFinder(self.conf)
            trs_finder.run()
            trs_finder.post_process()
            run_status.transformers = True

        if self.conf.pipeline.augment:
            augmentor = DatasetAugmentor(self.conf)
            await augmentor.augment_data()
            run_status.augment = True
