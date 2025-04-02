import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from loguru import logger

from src.cat.catter import Catter
from src.eval import lib
from src.eval.dataset_config import DatasetConfig
from src.eval.exact_match import ExactMatchParser
from src.eval.single_run_config import SingleRunConfig
from src.rel.base_matcher import ExtraColumnRemoverMatcher
from src.rel.db_facade import DatabaseFacade
from src.rel.db_factory import DatabaseFactory
from src.rel.result_transformer import IgnoreListOrderTransformer, IgnoreColOrderTransformer
from src.rel.sql_data import SqlInputData
from src.rel.sql_transformer import LiteralCorrectorTransformer
from src.rel.transformer_detector import TransformerDetector
from src.third_party.dail.utils.utils import DB_LONG_TIMEOUT
from src.third_party.spider.evaluation import get_spider_exact_match


@dataclass
class Metric(ABC):
    name: str
    conf: DatasetConfig
    dbc: DatabaseFacade

    def __init__(self, name: str, conf: DatasetConfig):
        self.name = name
        self.conf = conf
        self.dbc = DatabaseFactory.get_instance(conf)

    @abstractmethod
    def calc(self, gold: str, pred: str, db_id: str) -> int:
        pass


@dataclass
class StatMetric(ABC):
    name: str

    @abstractmethod
    def calc(self, run_conf: SingleRunConfig) -> int:
        pass


class ExactMatch(Metric):
    def __init__(self, name: str, conf: DatasetConfig):
        super().__init__(name, conf)
        self.parser = ExactMatchParser(self.conf.get_tables_path())

    def calc(self, gold: str, pred: str, db_id: str) -> int:
        parser = self.parser
        try:
            gold_parser = parser.parse(gold, db_id)
            pred_parser = parser.parse(pred, db_id)
            if (gold_parser == pred_parser) or (pred_parser == gold_parser):
                return 1
        except Exception as e:
            logger.debug(e)
        return 0


class SpiderExactMatch(Metric):
    def calc(self, gold: str, pred: str, db_id: str) -> int:
        try:
            score = get_spider_exact_match(pred, f"{gold}\t{db_id}", self.conf)
            return score
        except Exception as e:
            logger.debug(e)
            return 0


class ExecAcc(Metric):
    def calc(self, gold: str, pred: str, db_id: str) -> int:
        try:
            gold_sql_exec_res = self.dbc.exec_query_sync(db_id, gold, timeout=DB_LONG_TIMEOUT)
            pred_sql_exec_res = self.dbc.exec_query_sync(db_id, pred, timeout=DB_LONG_TIMEOUT)
            if gold_sql_exec_res is None:
                raise RuntimeError("Gold result is None!")
            if pred_sql_exec_res is None:
                return 0
            if pred_sql_exec_res == gold_sql_exec_res:
                return 1
            else:
                return 0
        except Exception as e:
            logger.debug(e)
            return 0


class ComplexityConsistency(Metric):
    def __init__(self, name: str, conf: DatasetConfig):
        super().__init__(name, conf)
        self.catter = Catter()

    def calc(self, gold: str, pred: str, db_id: str) -> int:
        catter = self.catter
        try:
            c_gold = catter.get_category(gold)
            c_pred = catter.get_category(pred)
            if c_pred is None:
                return 0
            if c_pred <= c_gold:
                return 1
            else:
                return 0
        except Exception as e:
            logger.debug(e)
            return 0


class GoldNotEmpty(Metric):
    def calc(self, gold: str, pred: str, db_id: str) -> int:
        try:
            gold_sql_exec_res = self.dbc.exec_query_sync(db_id, gold, timeout=DB_LONG_TIMEOUT)
            if gold_sql_exec_res is not None and len(gold_sql_exec_res) > 0:
                return 1
            else:
                return 0
        except Exception as e:
            logger.debug(e)
            return 0


class RelaxedExecAcc(Metric):

    def __init__(self, name: str, conf: DatasetConfig):
        super().__init__(name, conf)
        self.detector = TransformerDetector(conf, [
            LiteralCorrectorTransformer(),
            IgnoreListOrderTransformer(),
            IgnoreColOrderTransformer(),
            ExtraColumnRemoverMatcher()
        ])

    def calc(self, gold: str, pred: str, db_id: str) -> int:
        try:
            pd = SqlInputData(db_id, pred)
            gd = SqlInputData(db_id, gold)
            working_sub = self.detector.find_working_sub_sync(pd, gd)
            if working_sub is not None:
                return 1
            else:
                return 0
        except Exception as e:
            logger.debug(e)
        return 0


class Count(Metric):

    def calc(self, gold: str, pred: str, db_id: str) -> int:
        return 1


class ExecTime(Metric):
    def calc(self, gold: str, pred: str, db_id: str) -> int:
        try:
            timer = lib.Timer.start()
            self.dbc.exec_query_uncached(db_id, pred)
            pred_sql_exec_time = timer.lap()
            return pred_sql_exec_time * 1_000_000
        except Exception as e:
            logger.debug(e)
            return 0


class TokenUsage(Metric):
    tokens: List[int]

    def __init__(self, name: str, conf: DatasetConfig):
        super().__init__(name, conf)

    def calc(self, gold: str, pred: str, db_id: str) -> int:
        try:
            timer = lib.Timer.start()
            self.dbc.exec_query_uncached(db_id, pred)
            pred_sql_exec_time = timer.lap()
            return pred_sql_exec_time * 1_000_000
        except Exception as e:
            logger.debug(e)
            return 0


class GoldExecTime(Metric):
    def calc(self, gold: str, pred: str, db_id: str) -> int:
        try:
            timer = lib.Timer.start()
            self.dbc.exec_query_uncached(db_id, gold)
            pred_sql_exec_time = timer.lap()
            return pred_sql_exec_time * 1_000_000
        except Exception as e:
            logger.debug(e)
            return 0
