from abc import ABC, abstractmethod
from typing import List

from src.eval.exact_match import ExactMatchParser
from src.rel.db_facade import DatabaseFacade
from src.rel.result_transformer import ResultTransformer
from src.rel.sql_data import SqlInputData, SqlParsedData, SqlExecResult
from src.rel.sql_processor import ResultMatcher, SqlMatchingProcessor
from src.rel.sql_transformer import SqlTransformer
from loguru import logger

from src.third_party.dail.utils.utils import DB_LONG_TIMEOUT

MAX_PERM = 1_000_000


class Matcher:
    db_facade: DatabaseFacade
    parser: ExactMatchParser
    pre_exec_transformers: List[SqlTransformer]
    post_exec_transformers: List[ResultTransformer]
    result_matchers: List[ResultMatcher]

    def __init__(self, db_facade: DatabaseFacade, parser: ExactMatchParser, processors: List[SqlMatchingProcessor]):
        self.db_facade = db_facade
        self.parser = parser
        self.pre_exec_transformers = []
        self.post_exec_transformers = []
        self.result_matchers = []

        self.result_matchers.append(ExactMatcher())

        for processor in processors:
            if isinstance(processor, SqlTransformer):
                self.pre_exec_transformers.append(processor)
            elif isinstance(processor, ResultTransformer):
                self.post_exec_transformers.append(processor)
            elif isinstance(processor, ResultMatcher):
                self.result_matchers.append(processor)

    def parse(self, data: SqlInputData) -> SqlParsedData:
        try:
            ast = self.parser.parse(data.sql, data.db_id)
            return data.to_parsed(ast)
        except Exception as e:
            logger.debug(e)
        return None

    def exec(self, data: SqlParsedData) -> SqlExecResult:
        # res = await self.db_facade.exec_query_async(data.db_id, data.sql)
        res = self.db_facade.exec_query_sync(data.db_id, data.sql)
        return data.to_result(res)

    def match(self, pred: SqlInputData, gold: SqlInputData):
        pred_parsed, gold_parsed = self.parse(pred), self.parse(gold)
        if pred_parsed is None or gold_parsed is None:
            return False
        old_pred_exec, old_gold_exec = self.exec(pred_parsed), self.exec(gold_parsed)

        for transformer in self.pre_exec_transformers:
            pred_parsed, gold_parsed = transformer.transform_sql(pred_parsed, gold_parsed)

        pred_exec, gold_exec = self.exec(pred_parsed), self.exec(gold_parsed)
        for transformer in sorted(self.post_exec_transformers):
            pred_exec = transformer.transform_result(pred_exec)
            gold_exec = transformer.transform_result(gold_exec)
        result = False
        for matcher in self.result_matchers:
            result = matcher.check_res(pred_exec, gold_exec)
            if result:
                break
        if old_pred_exec.res != old_gold_exec.res and result:
            logger.debug(f"new_pred: {pred_exec.sql}")
            logger.debug(f"new_gold: {gold_exec.sql}")
            logger.debug(f"old_pres: {pred_exec.res}")
            logger.debug(f"old_gres: {gold_exec.res}")
            logger.debug(f"pres: {old_pred_exec.res}")
            logger.debug(f"gres: {old_gold_exec.res}")
        return result

    def get_result(self, data: SqlInputData):
        parsed = self.parse(data)
        return self.exec(parsed)


class ExactMatcher(ResultMatcher):
    def check_res(self, pred: SqlExecResult, gold: SqlExecResult) -> bool:
        return pred.res == gold.res


class ExtraTupleRemoverMatcher(ResultMatcher):
    def check_res(self, pred: SqlExecResult, gold: SqlExecResult) -> bool:
        matched = set()
        if pred.res is None or gold.res is None:
            return False
        for g in gold.res:
            g = frozenset(g)
            if g in pred.res:
                matched.add(g)
        if matched == gold.res:
            return True
        else:
            return False


class ExtraColumnRemoverMatcher(ResultMatcher):
    def check_res(self, pred: SqlExecResult, gold: SqlExecResult) -> bool:
        matched = set()
        if pred.res is None or gold.res is None:
            return False
        if len(list(gold.res)) * len(list(pred.res)) > MAX_PERM:
            return False
        for g in gold.res:
            g = frozenset(g)
            for p in pred.res:
                p = frozenset(p)
                if g.issubset(p):
                    matched.add(g)
        if matched == gold.res and len(gold.res) == len(pred.res):
            return True
        else:
            return False


class SubsetMatcher(ResultMatcher):
    def check_res(self, pred: SqlExecResult, gold: SqlExecResult) -> bool:
        matched = set()
        if pred.res is None or gold.res is None:
            return False
        for g in gold.res:
            g = frozenset(g)
            for p in pred.res:
                p = frozenset(p)
                if g.issubset(p):
                    matched.add(g)
        if len(matched) == len(gold.res):
            return True
        else:
            return False
