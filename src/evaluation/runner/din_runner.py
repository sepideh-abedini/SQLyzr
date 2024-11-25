from src.evaluation.runner.configs import SPIDER_SMALL
from src.evaluation.runner.model_runner import ModelRunner
from src.evaluation.runner.runner_config import SingleRunConfig
from src.third_party.din.din import run_din


class DinRunner(ModelRunner):
    def run_model(self):
        run_din(input_path=self.config.dataset_config.get_data_path(),
                output_path=self.config.output_path,
                tables_path=self.config.dataset_config.get_tables_path(),
                temp=self.config.temp)


if __name__ == "__main__":
    runner_config = SingleRunConfig(dataset_config=SPIDER_SMALL, output_path="data/din/pred.txt", temp=1.0)
    runner = DinRunner(runner_config)
    runner.run()
