from dataclasses import dataclass
from threading import Thread

from src.evaluation.runner.runner_config import SingleRunConfig


class ModelRunner(Thread):
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
