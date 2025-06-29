import asyncio
import os
from dataclasses import replace

import pandas as pd

from read_eval_data import read_eval_data
from src.configs.datasets import SPIDER_ALL
from src.eval.metrics import ExactMatch, ExecAcc, RelaxedExecAcc, ExecTime, GoldExecTime, NewRelaxedExecAcc
from src.rel.sqlite_facade import SqliteFacade
from src.util.async_utils import apply_async
from src.util.log_util import configure_logging
from src.util.multi_thread_utils import exec_multi_process

configure_logging()

metrics = [
    ExactMatch("em", SPIDER_ALL),
    ExecAcc("ea", SPIDER_ALL),
    # RelaxedExecAcc("rea", SPIDER_ALL),
    NewRelaxedExecAcc("rea", SPIDER_ALL),
    ExecTime("et", SPIDER_ALL),
    GoldExecTime("get", SPIDER_ALL)
]


class ScaledCalculator:
    def __init__(self, scale):
        self.eval_data = read_eval_data()
        self.metrics = metrics
        self.scale = scale
        self.set_scale()

    def set_scale(self):
        conf = SPIDER_ALL
        conf = replace(conf, db_dir=os.path.join(f"database_s{self.scale}"))
        for metric in self.metrics:
            metric.dbc = SqliteFacade(conf)

    def calc_row(self, row):
        scores = row
        for metric in metrics:
            db_id = row['db_id']
            pred = row['pred']
            gold = row['gold']
            score = metric.calc(gold, pred, db_id)
            scores[metric.name] = score
        scores['plt'] = ((row['et'] / row['get']) < 1.46) * scores['rea']
        del scores['gold']
        del scores['pred']
        del scores['db_id']
        return scores

    async def calc(self):
        results = exec_multi_process(self.calc_row, self.eval_data, desc=f"Score calculation for {self.scale}")
        df = pd.DataFrame(results)
        df.to_csv(f"thesis_v2/scale/scores_s{self.scale}.csv")
        return results


async def main():
    calculator = ScaledCalculator(1)
    await calculator.calc()


if __name__ == '__main__':
    asyncio.run(main())
