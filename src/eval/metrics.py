import json
from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.cat.catter import Catter
from src.eval import lib
from src.eval.dataset_config import DatasetConfig
from src.eval.exact_match import ExactMatchParser
from src.eval.lib import DatabaseClient
from src.eval.single_run_config import SingleRunConfig
from src.rel.base_matcher import ExtraColumnRemoverMatcher
from src.rel.result_transformer import IgnoreListOrderTransformer, IgnoreColOrderTransformer
from src.rel.sql_data import SqlInputData
from src.rel.sql_transformer import LiteralCorrectorTransformer
from src.rel.transformer_detector import TransformerDetector
from src.third_party.spider.evaluation import get_spider_exact_match
from src.util.logger import log


@dataclass
class Metric(ABC):
    name: str
    conf: DatasetConfig
    dbc: DatabaseClient

    def __init__(self, name: str, conf: DatasetConfig):
        self.name = name
        self.conf = conf
        self.dbc = DatabaseClient(conf)

    @abstractmethod
    async def calc(self, gold: str, pred: str, db_id: str) -> int:
        pass


@dataclass
class StatMetric(ABC):
    name: str

    @abstractmethod
    async def calc(self, run_conf: SingleRunConfig) -> int:
        pass


class ExactMatch(Metric):
    async def calc(self, gold: str, pred: str, db_id: str) -> int:
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

    async def calc(self, run_conf: SingleRunConfig) -> int:
        with open(run_conf.get_stats_path()) as file:
            data = json.load(file)
            return int(data["total_tokens"])


class SpiderExactMatch(Metric):
    async def calc(self, gold: str, pred: str, db_id: str) -> int:
        score = get_spider_exact_match(pred, f"{gold}\t{db_id}", self.conf.get_db_path(),
                                       self.conf.get_tables_path())
        return score


class ExecAcc(Metric):
    async def calc(self, gold: str, pred: str, db_id: str) -> int:
        db_file_path = self.conf.get_db_file_path(db_id)
        gold_sql_exec_res = self.dbc.exec_sql(db_id, gold)
        pred_sql_exec_res = self.dbc.exec_sql(db_id, pred)
        if gold_sql_exec_res is None:
            raise RuntimeError("Gold result is None!")
        if pred_sql_exec_res is None:
            return 0
        if pred_sql_exec_res == gold_sql_exec_res:
            return 1
        else:
            return 0


class ComplexityConsistency(Metric):
    async def calc(self, gold: str, pred: str, db_id: str) -> int:
        catter = Catter()
        c_gold = catter.get_category(gold)
        c_pred = catter.get_category(pred)
        if c_pred is None:
            return 0
        if c_pred <= c_gold:
            return 1
        else:
            return 0


class GoldNotEmpty(Metric):
    async def calc(self, gold: str, pred: str, db_id: str) -> int:
        gold_sql_exec_res = self.dbc.exec_sql(db_id, gold)
        if gold_sql_exec_res is not None and len(gold_sql_exec_res) > 0:
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
            ExtraColumnRemoverMatcher()
        ])

    async def calc(self, gold: str, pred: str, db_id: str) -> int:
        pd = SqlInputData(db_id, pred)
        gd = SqlInputData(db_id, gold)
        working_sub = await self.detector.find_working_sub_sync(pd, gd)
        if working_sub is not None:
            return 1
        else:
            return 0


class Count(Metric):

    async def calc(self, gold: str, pred: str, db_id: str) -> int:
        return 1


class TotalExecTime(Metric):
    async def calc(self, gold: str, pred: str, db_id: str) -> int:
        timer = lib.Timer.start()
        self.dbc.exec_sql(db_id, pred)
        pred_sql_exec_time = timer.lap()
        return pred_sql_exec_time.total_seconds() * 1_000_000
