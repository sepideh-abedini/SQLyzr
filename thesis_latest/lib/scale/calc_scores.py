import argparse
import asyncio
import os
from dataclasses import replace

import pandas as pd

from read_eval_data import read_eval_data
from src.configs.datasets import SPIDER_ALL
from src.eval.metrics import ExactMatch, ExecAcc, ExecTime, GoldExecTime, NewRelaxedExecAcc
from src.rel.sqlite_facade import SqliteFacade
from src.util.log_util import configure_logging
from src.util.multi_thread_utils import exec_multi_process
from thesis_latest.lib.params import R_VALUE, SCALES

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
    def __init__(self, scale, input_file, pred_dir, output_dir):
        self.eval_data = read_eval_data(input_file, pred_dir)
        self.output_dir = output_dir
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
        scores['plt'] = ((row['et'] / row['get']) < R_VALUE) * scores['rea']
        del scores['gold']
        del scores['pred']
        del scores['db_id']
        return scores

    async def calc(self):
        results = exec_multi_process(self.calc_row, self.eval_data, desc=f"Score calculation for {self.scale}")
        df = pd.DataFrame(results)
        out_file = os.path.join(self.output_dir, f'scores_s{self.scale}.csv')
        df.to_csv(out_file)
        return results


async def main(input_file, pred_dir, output_dir):
    for scale in SCALES:
        calculator = ScaledCalculator(scale, input_file, pred_dir, output_dir)
        await calculator.calc()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True)
    parser.add_argument("-p", required=True)
    parser.add_argument("-o", required=True)
    args = parser.parse_args()
    asyncio.run(main(args.i, args.p, args.o))
