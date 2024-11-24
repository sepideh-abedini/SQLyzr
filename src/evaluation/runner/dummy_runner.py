import json

from src.evaluation.runner.dataset_config import SPIDER_SMALL
from src.evaluation.runner.model_runner import ModelRunner
from src.evaluation.runner.runner_config import RunnerConfig


class DummyRunner(ModelRunner):
    def run_model(self):
        with open(self.config.dataset_config.get_data_path()) as data_file:
            data = json.load(data_file)

        with open(self.config.output_path, "w") as out_file:
            for entry in data:
                out_file.write(f"{entry["query"]}\n")
            out_file.write(f"tokens:{19000}")


if __name__ == "__main__":
    runner_config = RunnerConfig(dataset_config=SPIDER_SMALL, output_path="data/dum/pred.txt", temp=1.0)
    runner = DummyRunner(runner_config)
    runner.run()
