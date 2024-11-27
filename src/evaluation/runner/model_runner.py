from threading import Thread

from src.evaluation.runner.runner_config import SingleRunConfig
from src.evaluation.runner.utils import wait_for_file


class ModelRunner:
    config: SingleRunConfig

    def __init__(self, config: SingleRunConfig):
        super().__init__()
        self.config = config

    def preprocess(self):
        pass

    def run_model(self):
        pass

    def run(self):
        self.preprocess()
        self.run_model()
        wait_for_file(self.config.get_pred_path())
        print(f"File created: {self.config.get_pred_path()}")
