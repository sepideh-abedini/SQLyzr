from typing import List

from src.eval.dataset_config import DatasetConfig
from src.eval.exact_match import ExactMatchParser
from src.rel.base_matcher import Matcher
from src.rel.db_factory import DatabaseFactory
from src.rel.sql_data import SqlInputData
from src.rel.sql_processor import SqlMatchingProcessor
from src.util.meta_utils import powerset


class TransformerDetector:
    def __init__(self, dataset_config: DatasetConfig, processors: List[SqlMatchingProcessor]):
        self.processors = processors
        self.db_facade = DatabaseFactory.get_instance(dataset_config)
        self.parser = ExactMatchParser(dataset_config.get_tables_path())

    def run_with(self, pred: SqlInputData, gold: SqlInputData, procs: List[SqlMatchingProcessor]) \
            -> List[SqlMatchingProcessor]:
        matcher = Matcher(self.db_facade, self.parser, procs)
        res = matcher.match(pred, gold)
        if res:
            return procs
        else:
            return None

    def find_sub(self, pred: SqlInputData, gold: SqlInputData):
        pows = powerset(self.processors)
        for sub in pows:
            res = self.run_with(pred, gold, list(sub))
            if res is not None:
                return res
        return None

    def find_working_sub_sync(self, pred: SqlInputData, gold: SqlInputData):
        return self.find_sub(pred, gold)
