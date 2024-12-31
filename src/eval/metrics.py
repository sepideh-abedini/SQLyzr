from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.eval import lib
from src.eval.dataset_config import DatasetConfig
from src.eval.exact_match import ExactMatchParser
from src.eval.lib import exec_sql
from src.eval.runner_config import SingleRunConfig
from src.rel.base_matcher import SubsetMatcher
from src.rel.result_transformer import IgnoreListOrderTransformer, IgnoreColOrderTransformer
from src.rel.sql_data import SqlInputData
from src.rel.sql_transformer import LimitRemoverTransformer, LiteralCorrectorTransformer, ColCorrectorTransformer
from src.rel.transformer_detector import TransformerDetector
from src.third_party.spider.evaluation import get_spider_exact_match
from src.util.logger import log


@dataclass
class Metric(ABC):
    name: str
    conf: DatasetConfig

    @abstractmethod
    def calc(self, gold: str, pred: str, db_id: str) -> int:
        pass


@dataclass
class StatMetric(ABC):
    name: str

    @abstractmethod
    def calc(self, i: int, run_conf: SingleRunConfig) -> int:
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


class TokenUsage(StatMetric):

    def calc(self, i: int, run_conf: SingleRunConfig) -> int:
        file = open(run_conf.get_token_path())
        usage = file.readlines()
        return int(usage[i])


class SpiderExactMatch(Metric):
    def calc(self, gold: str, pred: str, db_id: str) -> int:
        score = get_spider_exact_match(pred, f"{gold}\t{db_id}", self.conf.get_db_path(),
                                       self.conf.get_tables_path())
        return score


class ExecAcc(Metric):
    def calc(self, gold: str, pred: str, db_id: str) -> int:
        db_file_path = self.conf.get_db_file_path(db_id)
        gold_sql_exec_res = exec_sql(db_file_path, gold)
        pred_sql_exec_res = exec_sql(db_file_path, pred)
        result = (gold_sql_exec_res and pred_sql_exec_res) and (pred_sql_exec_res == gold_sql_exec_res)
        if result:
            return 1
        else:
            return 0


class RelaxedExecAcc(Metric):

    def __init__(self, name: str, conf: DatasetConfig):
        super().__init__(name, conf)
        self.detector = TransformerDetector(conf, [
            LiteralCorrectorTransformer(),
            IgnoreListOrderTransformer(),
            IgnoreColOrderTransformer(),
            SubsetMatcher()
        ])

    def calc(self, gold: str, pred: str, db_id: str) -> int:
        pd = SqlInputData(db_id, pred)
        gd = SqlInputData(db_id, gold)
        working_sub = self.detector.find_working_sub(pd, gd)
        if working_sub:
            return 1
        else:
            return 0


class Count(Metric):

    def calc(self, gold: str, pred: str, db_id: str) -> int:
        return 1


class TotalExecTime(Metric):
    def calc(self, gold: str, pred: str, db_id: str) -> int:
        db_file_path = self.conf.get_db_file_path(db_id)
        timer = lib.Timer()
        timer.start()
        exec_sql(db_file_path, pred)
        pred_sql_exec_time = timer.stop()
        return pred_sql_exec_time.total_seconds() * 1_000_000
