import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple

from loguru import logger
from natsort import natsorted

from src.analyzer.letter_casing_transformer import LetterCasingTransformer
from src.analyzer.sql_data import SqlInputData, SqlParsedData
from src.db.db_facade import DatabaseFacade, DB_TIMEOUT
from src.db.db_factory import DatabaseFactory
from src.eval import lib
from src.eval.dataset_config import DatasetConfig
from src.eval.exact_match import ExactMatchParser
from src.eval.metrics import Metric
from src.third_party.dail.utils.utils import DB_LONG_TIMEOUT
from src.third_party.spider.evaluation import get_spider_exact_match


# Calculate REA + EA + exec times with a single execution
class NewRelaxedExecAccEfficient(Metric):

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
                gold_sql_exec_res = self.dbc.exec_query_uncached(db_id, gold_data.sql, scale=scale,
                                                                 timeout=DB_LONG_TIMEOUT)
                gold_sql_exec_time = timer.lap()
                gold_sql_exec_time *= 1_000_000
        return 0, 0, gold_sql_exec_time, pred_sql_exec_time
