import asyncio
from asyncio import FIRST_COMPLETED
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

    async def run_with(self, pred: SqlInputData, gold: SqlInputData, procs: List[SqlMatchingProcessor]) \
            -> List[SqlMatchingProcessor]:
        matcher = Matcher(self.db_facade, self.parser, procs)
        res = await matcher.match(pred, gold)
        if res:
            return procs
        else:
            return None

    async def find_sub(self, pred: SqlInputData, gold: SqlInputData):
        pows = powerset(self.processors)
        tasks = []
        for sub in pows:
            tasks.append(self.run_with(pred, gold, list(sub)))
        results = await asyncio.gather(*tasks)
        for res in results:
            if res is not None:
                return res
        return None

    async def find_working_sub_sync(self, pred: SqlInputData, gold: SqlInputData):
        return await self.find_sub(pred, gold)

    async def find_sub_async(self, pred: SqlInputData, gold: SqlInputData):
        pows = powerset(self.processors)
        print(len(pows))
        tasks = []
        for sub in pows:
            task = asyncio.create_task(self.run_with(pred, gold, list(sub)))
            tasks.append(task)

        # results = await asyncio.gather(*tasks)
        # return results
        while tasks:
            done, pending = await asyncio.wait(tasks, return_when=FIRST_COMPLETED)
            for d in done:
                result = d.result()
                if d.result() is not None:
                    for p in pending:
                        p.cancel()
                    return result
            print(len(tasks))
            tasks = pending
        return None
    #     # for sub in pows:
    #     # print(f"Checking with: {sub}")
    #     # res = pool.apply_async(func=self.run_with, args=(pred, gold, sub))
    #     # procs.append(res)
    #     # p = Thread(target=self.run_with, args=(pred, gold, sub))
    #     # res = self.run_with(pred, gold, list(sub))
    #     # continue
    #     # if res is not None:
    #     #     return res
    #     #     working_sub = sub
    #     #     break
    #     # pool.close()
    #     # count = 1 * (1 / 0.01)
    #     # while count > 0:
    #     #     for p in procs:
    #     #         if p.ready():
    #     #             x = p.get(1)
    #     #             if x is not None:
    #     #                 pool.terminate()
    #     #                 return x
    #     # count -= 1
    #     # sleep(0.001)
    #     # pool.terminate()
    #     return None
