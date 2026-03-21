import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple

from loguru import logger
from natsort import natsorted

from src.cat.catter import Catter
from src.eval import lib
from src.eval.dataset_config import DatasetConfig
from src.eval.exact_match import ExactMatchParser
from src.eval.single_run_config import SingleRunConfig
from src.rel.db_facade import DatabaseFacade, DB_TIMEOUT
from src.rel.db_factory import DatabaseFactory
from src.rel.result_matcher import ExtraColumnsMatcher, IgnoreListOrderMatcher, IgnoreColOrderMatcher
from src.rel.sql_data import SqlInputData, SqlParsedData
from src.rel.sql_transformer import LetterCasingTransformer
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
    def calc(self, gold: str, pred: str, db_id: str, scale=1) -> int:
        pass


class ExactMatch(Metric):
    def __init__(self, name: str, conf: DatasetConfig):
        super().__init__(name, conf)
        self.parser = ExactMatchParser(self.conf.get_tables_path())

    def calc(self, gold: str, pred: str, db_id: str, scale=1) -> int:
        parser = self.parser
        try:
            gold_ast = parser.parse(gold, db_id)
            pred_ast = parser.parse(pred, db_id)
            if (gold_ast == pred_ast) or (pred_ast == gold_ast):
                return 1
        except Exception as e:
            logger.debug(e)
        return 0


class SpiderExactMatch(Metric):
    def calc(self, gold: str, pred: str, db_id: str, scale=1) -> int:
        try:
            score = get_spider_exact_match(pred, f"{gold}\t{db_id}", self.conf)
            return score
        except Exception as e:
            logger.debug(e)
            return 0


class ExecAcc(Metric):
    def calc(self, gold: str, pred: str, db_id: str, scale=1) -> int:
        try:
            gold_sql_exec_res = self.dbc.exec_query_sync(db_id, gold, scale=scale, timeout=DB_LONG_TIMEOUT)
            pred_sql_exec_res = self.dbc.exec_query_sync(db_id, pred, scale=scale, timeout=DB_LONG_TIMEOUT)
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


class GoldNotEmpty(Metric):
    def calc(self, gold: str, pred: str, db_id: str, scale: int = 1) -> int:
        try:
            gold_sql_exec_res = self.dbc.exec_query_sync(db_id, gold, scale=scale, timeout=DB_LONG_TIMEOUT)
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
            LetterCasingTransformer(),
            IgnoreListOrderMatcher(),
            IgnoreColOrderMatcher(),
            # IgnoreListOrderMatcher(),
            ExtraColumnsMatcher()
        ])

    def calc(self, gold: str, pred: str, db_id: str, scale: int = 1) -> int:
        try:
            pd = SqlInputData(db_id, pred)
            gd = SqlInputData(db_id, gold)
            # working_sub = self.detector.find_working_sub_sync(pd, gd)
            working_sub = self.detector.apply_all(pd, gd)
            if working_sub is not None:
                return 1
            else:
                return 0
        except Exception as e:
            logger.debug(e)
        return 0


class NewRelaxedExecAcc(Metric):

    def __init__(self, name: str, conf: DatasetConfig):
        super().__init__(name, conf)
        self.parser = ExactMatchParser(self.conf.get_tables_path())

    def sorted_rs_str(self, rs: List[Tuple]):
        row_strs = []
        for r in rs:
            vals = list(map(str, r))
            sorted_vals = natsorted(vals)
            row_str = "-".join(sorted_vals)
            row_strs.append(row_str)

        row_strs_sorted = natsorted(row_strs)
        rs_str = "#".join(row_strs_sorted)
        return rs_str

    def check_equi(self, rs1: List[Tuple], rs2: List[Tuple]):
        rs1_str = self.sorted_rs_str(rs1)
        rs2_str = self.sorted_rs_str(rs2)
        return rs1_str == rs2_str

    def parse(self, data: SqlInputData) -> SqlParsedData:
        try:
            ast = self.parser.parse(data.sql, data.db_id)
            return data.to_parsed(ast)
        except Exception as e:
            logger.debug(e)
        return None

    def calc(self, gold: str, pred: str, db_id: str, scale: int = 1) -> Tuple[int, int, int, int]:
        transformer = LetterCasingTransformer()

        gold_sql_exec_time = 0
        pred_sql_exec_time = 0
        try:
            pred_data = SqlInputData(db_id, pred)
            gold_data = SqlInputData(db_id, gold)
            pred_parsed, gold_parsed = self.parse(pred_data), self.parse(gold_data)
            pred_data, gold_data = transformer.transform_sql(pred_parsed, gold_parsed)

            timer = lib.Timer.start()
            pred_sql_exec_res = self.dbc.exec_query_uncached(db_id, pred_data.sql, scale=scale, timeout=DB_LONG_TIMEOUT)
            pred_sql_exec_time = timer.lap()
            pred_sql_exec_time *= 1_000_000

            timer = lib.Timer.start()
            gold_sql_exec_res = self.dbc.exec_query_uncached(db_id, gold_data.sql, scale=scale, timeout=DB_LONG_TIMEOUT)
            gold_sql_exec_time = timer.lap()
            gold_sql_exec_time *= 1_000_000

            if gold_sql_exec_res is None:
                raise RuntimeError("Gold result is None!")
            if pred_sql_exec_res is None:
                return 0, 0, gold_sql_exec_time, pred_sql_exec_time
            if self.check_equi(gold_sql_exec_res, pred_sql_exec_res):
                ea = int(pred_sql_exec_res == gold_sql_exec_res)
                return 1, ea, gold_sql_exec_time, pred_sql_exec_time
            else:
                return 0, 0, gold_sql_exec_time, pred_sql_exec_time
        except Exception as e:
            logger.error(e)
            if gold_sql_exec_time == 0:
                gold_data = SqlInputData(db_id, gold)
                timer = lib.Timer.start()
                gold_sql_exec_res = self.dbc.exec_query_uncached(db_id, gold_data.sql, scale=scale, timeout=DB_LONG_TIMEOUT)
                gold_sql_exec_time = timer.lap()
                gold_sql_exec_time *= 1_000_000
        return 0, 0, gold_sql_exec_time, pred_sql_exec_time


class Count(Metric):

    def calc(self, gold: str, pred: str, db_id: str, scale: int = 1) -> int:
        return 1


class ExecTime(Metric):
    def calc(self, gold: str, pred: str, db_id: str, scale: int = 1) -> int:
        try:
            timer = lib.Timer.start()
            self.dbc.exec_query_uncached(db_id, pred, scale=scale)
            pred_sql_exec_time = timer.lap()
            return pred_sql_exec_time * 1_000_000
        except Exception as e:
            logger.debug(e)
            return 0


class GoldExecTime(Metric):
    def calc(self, gold: str, pred: str, db_id: str, scale: int = 1) -> int:
        try:
            timer = lib.Timer.start()
            res = self.dbc.exec_query_uncached(db_id, gold, scale=scale, timeout=DB_TIMEOUT)
            pred_sql_exec_time = timer.lap()
            return pred_sql_exec_time * 1_000_000
        except Exception as e:
            logger.error(e)
            return 0
