from typing import List, Tuple

from src.eval.dataset_config import DatasetConfig
from src.eval.model_eval_config import ModelEvalConfig
from src.eval.single_run_config import SingleRunConfig


class PredGoldReader:
    __config: SingleRunConfig

    def __init__(self, config: SingleRunConfig):
        self.__config = config

    def get_pred_gold_db_id(self) -> List[Tuple[str, str, str]]:
        pred_path = self.__config.get_pred_path()
        gold_path = self.__config.dataset_config.get_gold_path()
        with open(pred_path) as pred_file, open(gold_path) as gold_file:
            pred_file_lines = pred_file.readlines()
            rows = []
            for i, gold_line in enumerate(gold_file):
                gold_sql, db_id = gold_line.strip().split("\t")
                pred_sql = pred_file_lines[i].strip()
                rows.append((pred_sql, gold_sql, db_id))
        return rows
