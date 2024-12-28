from multiprocessing.pool import ThreadPool
from time import sleep
from typing import List
from threading import Thread

from src.evaluation.evaluator.exact_match import ExactMatchParser
from src.exprimental.db_facade import DatabaseFacade
from src.exprimental.matcher.base_matcher import Matcher, SubsetMatcher
from src.exprimental.matcher.lib import powerset
from src.exprimental.matcher.result_transformer import IgnoreListOrderTransformer, IgnoreColOrderTransformer
from src.exprimental.matcher.sql_data import SqlInputData
from src.exprimental.matcher.sql_processor import SqlMatchingProcessor
from src.exprimental.matcher.sql_transformer import LimitRemoverTransformer, LiteralCorrectorTransformer, \
    ColCorrectorTransformer
import multiprocessing as mp


class TransformerDetector:
    def __init__(self):
        self.processors = [
            LimitRemoverTransformer(),
            LiteralCorrectorTransformer(),
            ColCorrectorTransformer(),
            IgnoreListOrderTransformer(),
            IgnoreColOrderTransformer(),
            SubsetMatcher()
        ]
        self.db_facade = DatabaseFacade("data/spider/database")
        self.parser = ExactMatchParser("data/spider/tables.json")

    def run_with(self, pred: SqlInputData, gold: SqlInputData, procs: List[SqlMatchingProcessor]):
        matcher = Matcher(self.db_facade, self.parser, procs)
        res = matcher.match(pred, gold)
        if res:
            return procs
        else:
            return None

    def find_working_sub(self, pred: SqlInputData, gold: SqlInputData):
        working_sub = None
        procs = []
        pool = ThreadPool(processes=1)
        for sub in powerset(self.processors):
            # print(f"Checking with: {sub}")
            res = pool.apply_async(func=self.run_with, args=(pred, gold, sub))
            procs.append(res)
            # p = Thread(target=self.run_with, args=(pred, gold, sub))
            # res = self.run_with(pred, gold, list(sub))
            # continue
            # if res is not None:
            #     return res
            #     working_sub = sub
            #     break
        pool.close()
        count = 1 * (1 / 0.01)
        while count > 0:
            for p in procs:
                if p.ready():
                    x = p.get(1)
                    if x:
                        pool.terminate()
                        return x
            count -= 1
            sleep(0.01)
        pool.terminate()
        return None
