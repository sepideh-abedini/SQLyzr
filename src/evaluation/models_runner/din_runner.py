import shutil

from src.evaluation.src.evaluator.lib import execute_command
from src.evaluation.src.models_runner.run_config import ModelEvalConfig
from src.evaluation.src.models_runner.runner import ModelRunner

DIN_FILE = 'src/third_party/din_gen/DIN-SQL.py'


class DinRunner(ModelRunner):

    def run_model_single_time(self, k):
        k_dataset_dir = f"{self.config.dataset_path}_{k}/"
        k_output_path = f"{self.output_dir}_{k}"
        DIN_command = f"python3 {DIN_FILE} --dataset {k_dataset_dir} --output {k_output_path} --temp {self.temp}"
        execute_command(DIN_command)

    def convert_dataset(self):
        shutil.copyfile(self.config.get_query_file_path(), self.config.get_sub_path("dev.json"))


def main():
    config = ModelEvalConfig(dataset_path="data/dataset/uniform",
                             query_file="test.json",
                             gold_file="test.gold.txt",
                             database_dir="database",
                             tables_file="tables.json")
    runner = DinRunner(config=config, output_dir="data/out/din_gen/pred.sql", thread_count=2, temp=1)
    runner.convert_dataset()
    runner.run()
    runner.merge_results()


# if __name__ == '__main__':
#     main()
