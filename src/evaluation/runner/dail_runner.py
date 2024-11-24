import json
import math
import os.path

from src.evaluation.runner.dataset_config import DatasetConfig, SPIDER_SMALL
from src.evaluation.runner.model_runner import ModelRunner
from src.evaluation.runner.runner_config import RunnerConfig
from src.third_party.dail.ask_llm import run_dail
from src.third_party.dail.data_preprocess import preprocess_data
from src.third_party.dail.generate_question import generate_questions


class DailRunner(ModelRunner):
    schema_links_path = "data/dail/preprocess/schema_links.json"
    questions_path = "data/dail/preprocess/questions.json"

    def generate_schema_links(self):
        print("Starting: schema links generation")
        preprocess_data(
            input_path=self.config.dataset_config.get_data_path(),
            output_path=self.schema_links_path,
            db_path=self.config.dataset_config.get_db_path(),
            tables_path=self.config.dataset_config.get_tables_path()
        )
        print("Finished: schema links generation")

    def generate_questions(self):
        print("Starting question generation")
        generate_questions(
            tables_path=self.config.dataset_config.get_tables_path(),
            output_path=self.questions_path,
            db_dir=self.config.dataset_config.get_db_path(),
            input_path=self.config.dataset_config.get_data_path(),
            schema_links_path=self.schema_links_path
        )
        print("Finished question generation")

    def preprocess(self):
        self.generate_schema_links()
        self.generate_questions()

    def run_model(self):
        run_dail(input_path=self.questions_path,
                 output_path=self.config.output_path,
                 db_dir=self.config.dataset_config.get_db_path(),
                 temp=self.config.temp)


if __name__ == "__main__":
    runner_config = RunnerConfig(dataset_config=SPIDER_SMALL, output_path="data/dail/pred.txt", temp=1.0)
    runner = DailRunner(runner_config)
    runner.run()
