from src.configs.sqlyzr_config import SQLyzrConfig
from src.eval.dataset_config import DatasetConfig
from src.util.file_utils import read_json


class WorkloadExpander:
    def __init__(self, conf: SQLyzrConfig):
        self.conf = conf

    def expand_workload(self):
        data = read_json(self.conf.eval_conf.datasets)

