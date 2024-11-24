from dataclasses import dataclass
from threading import Thread

from src.evaluation.runner.runner_config import RunnerConfig


class ModelRunner(Thread):
    config: RunnerConfig

    def __init__(self, config: RunnerConfig):
        super().__init__()
        self.config = config

    def preprocess(self):
        pass

    def run_model(self):
        pass

    def run(self):
        self.preprocess()
        self.run_model()
