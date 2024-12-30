from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.eval.dataset_config import DatasetConfig
from src.eval.exact_match import ExactMatchParser
from src.util.logger import log


@dataclass
class Metric(ABC):
    name: str
    conf: DatasetConfig

    @abstractmethod
    def calc(self, gold: str, pred: str, db_id: str) -> int:
        pass


class ExactMatch(Metric):
    def calc(self, gold: str, pred: str, db_id: str) -> int:
        parser = ExactMatchParser(self.conf.get_tables_path())
        try:
            gold_parser = parser.parse(gold, db_id)
            pred_parser = parser.parse(pred, db_id)
            if (gold_parser == pred_parser) or (pred_parser == gold_parser):
                return 1
        except Exception as e:
            log(e)
        return 0
