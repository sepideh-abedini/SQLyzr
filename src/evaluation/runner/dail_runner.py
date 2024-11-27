import json
import math
import os.path

from src.evaluation.configs import EVAL_CONF
from src.evaluation.runner.dataset_config import DatasetConfig
from src.evaluation.runner.model_runner import ModelRunner
from src.evaluation.runner.runner_config import SingleRunConfig
from src.third_party.dail.ask_llm import run_dail
from src.third_party.dail.data_preprocess import preprocess_data
from src.third_party.dail.generate_question import generate_questions


class DailRunner(ModelRunner):
    schema_links_path = "data/dail/preprocess/schema_links.json"
    questions_path = "data/dail/preprocess/questions.json"

    def generate_schema_links(self):
        preprocess_data(
            input_path=self.config.dataset_config.get_data_path(),
            output_path=self.schema_links_path,
            db_path=self.config.dataset_config.get_db_path(),
            tables_path=self.config.dataset_config.get_tables_path()
        )
        print("Preprocessing Done")

    def generate_questions(self):
        generate_questions(
            tables_path=self.config.dataset_config.get_tables_path(),
            output_path=self.questions_path,
            db_dir=self.config.dataset_config.get_db_path(),
            input_path=self.config.dataset_config.get_data_path(),
            schema_links_path=self.schema_links_path
        )
        print("Question generation done")

    def preprocess(self):
        self.generate_schema_links()
        self.generate_questions()
        print("Preprocessing done")

    def run_model(self):
        run_dail(input_path=self.questions_path,
                 output_path=self.config.get_pred_path(),
                 db_dir=self.config.dataset_config.get_db_path(),
                 temp=self.config.temp)


if __name__ == "__main__":
    runner = DailRunner(EVAL_CONF.get_runner_conf(0.0, 0))
    runner.run()
