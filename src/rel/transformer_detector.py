from multiprocessing.pool import ThreadPool
from time import sleep
from typing import List

from src.eval.dataset_config import DatasetConfig
from src.eval.exact_match import ExactMatchParser
from src.rel.base_matcher import Matcher
from src.rel.db_facade import DatabaseFacade
from src.rel.sql_data import SqlInputData
from src.rel.sql_processor import SqlMatchingProcessor
from src.util.meta_utils import powerset


class TransformerDetector:
    def __init__(self, dataset_config: DatasetConfig, processors: List[SqlMatchingProcessor]):
        self.processors = processors
        self.db_facade = DatabaseFacade(dataset_config.get_db_path())
        self.parser = ExactMatchParser(dataset_config.get_tables_path())

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
        pool = ThreadPool(processes=4)
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
