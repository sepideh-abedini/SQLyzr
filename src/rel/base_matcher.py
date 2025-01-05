from abc import ABC, abstractmethod
from typing import List

from src.eval.exact_match import ExactMatchParser
from src.rel.db_facade import DatabaseFacade
from src.rel.result_transformer import ResultTransformer
from src.rel.sql_data import SqlInputData, SqlParsedData, SqlExecResult
from src.rel.sql_processor import ResultMatcher, SqlMatchingProcessor
from src.rel.sql_transformer import SqlTransformer
from src.util.logger import log


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
        if len(self.result_matchers) > 4:
            print("salam")

    def parse(self, data: SqlInputData) -> SqlParsedData:
        try:
            ast = self.parser.parse(data.sql, data.db_id)
            return data.to_parsed(ast)
        except Exception as e:
            log(e)
        return None

    async def exec(self, data: SqlParsedData) -> SqlExecResult:
        res = await self.db_facade.exec_query_async(data.db_id, data.sql)
        return data.to_result(res)

    async def match(self, pred: SqlInputData, gold: SqlInputData):
        pred_parsed, gold_parsed = self.parse(pred), self.parse(gold)
        if pred_parsed is None or gold_parsed is None:
            return False

        for transformer in self.pre_exec_transformers:
            pred_parsed, gold_parsed = transformer.transform_sql(pred_parsed, gold_parsed)

        pred_exec, gold_exec = await self.exec(pred_parsed), await self.exec(gold_parsed)
        for transformer in sorted(self.post_exec_transformers):
            pred_exec = transformer.transform_result(pred_exec)
            gold_exec = transformer.transform_result(gold_exec)

        result = False
        for matcher in self.result_matchers:
            result = matcher.check_res(pred_exec, gold_exec)
            if result:
                break
        if result:
            pass
            # print(f"new_pred: {pred_exec.sql}")
            # print(f"new_gold: {gold_exec.sql}")
            # print(f"pred_res: {pred_exec.res}")
            # print(f"gold_res: {gold_exec.res}")
        return result

    def get_result(self, data: SqlInputData):
        parsed = self.parse(data)
        return self.exec(parsed)


class ExactMatcher(ResultMatcher):
    def check_res(self, pred: SqlExecResult, gold: SqlExecResult) -> bool:
        return pred.res == gold.res


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
        if matched == gold.res:
            return True
        else:
            return False
