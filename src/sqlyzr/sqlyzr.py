import os
import shutil

from src.chart.charter import draw_all_charts
from src.configs.config_loader import load_config, ConfigData
from src.configs.sqlyzr_config import SQLyzrConfig
from src.ipc.messanger import Messanger
from src.model.models import run_model
from src.sqlyzr.augment_data import DatasetAugmentor
from src.sqlyzr.pipeline_config import PipelineConfig
from src.sqlyzr.run_scale_cli import scale_dbs
from src.sqlyzr.score_calculator import ScoreCalculator
from src.sqlyzr.scores_post_processor import ScoresPostProcessor
from src.sqlyzr.transformer_eval import TransformerFinder
from src.sqlyzr.validate import validate_dataset


class Sqlyzr:
    conf: SQLyzrConfig
    conf_path: str

    def __init__(self, conf_path: str):
        self.conf = load_config(conf_path)
        self.conf_path = conf_path
        self.messanger = Messanger()

    async def run(self):
        run_status = PipelineConfig.init()

        if self.conf.pipeline.verify:
            await validate_dataset(self.conf.eval_conf.dataset_configs)
            run_status.verify = True
            self.messanger.write(f"Verify DONE!!")

        if self.conf.pipeline.scale:
            scales = scale_dbs(self.conf_path)
            self.messanger.write(f"Scaling for factors {scales} completed")

        if self.conf.pipeline.predict:
            await run_model(self.conf)
            run_status.predict = True

        if self.conf.pipeline.eval:
            calc = ScoreCalculator(self.conf)
            calc.calc_scores()
            post_processor = ScoresPostProcessor(self.conf)
            post_processor.run()
            run_status.eval = True
            self.messanger.write(f"Evaluation completed!")

        if self.conf.pipeline.plots:
            shutil.rmtree(self.conf.eval_conf.charts_dir)
            os.makedirs(self.conf.eval_conf.charts_dir, exist_ok=True)
            for hue in ["Model", "Workload Version"]:
                draw_all_charts(self.conf.eval_conf.get_raw_scores_path(),
                                out_dir=self.conf.eval_conf.charts_dir,
                                included_charts=self.conf.eval_conf.included_charts,
                                hue=hue,
                                scaled_plots=len(self.conf.eval_conf.scales) > 1)
            run_status.plots = True

        if self.conf.pipeline.analysis:
            trs_finder = TransformerFinder(self.conf)
            trs_finder.run()
            trs_finder.post_process()
            run_status.analysis = True

        if self.conf.pipeline.augment:
            augmentor = DatasetAugmentor(self.conf)
            new_ver = await augmentor.augment_data(expand=True)
            run_status.augment = True
            conf_data = ConfigData.load(self.conf_path)
            cur_ver = conf_data.dataset_versions[-1]
            conf_data.dataset_versions.append(new_ver)
            shutil.copy(self.conf_path, f"{self.conf_path}.bak")
            conf_data.save(self.conf_path)
            self.messanger.write(f"Data augmentation done: {cur_ver} -> {new_ver}")
