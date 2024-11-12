# from turtle import pd
import argparse
import json
import math
import os.path
import sqlite3

import pandas as pd

import lib
from src.batch.batch_sql_parser import BatchSqlParser
from src.batch.category_exporter import BatchCategoryExporter
from src.batch.spider_pre_processor import SpiderPreProcessor
from src.evaluation.my_exe_eval import exec_sql
from exact_match import ExactMatchParser
from src.evaluation.lib import Timer
from src.evaluation.src.models_runner.run_config import ModelRunConfig
from src.evaluation.src.models_runner.din_runner import DinRunner
from src.third_party.spider.evaluation import eval_exact_match
from src.third_party.test_suite_acc.evaluation import test_suite_exec_acc


class DinModelEvaluator:
    config: ModelRunConfig

    def __init__(self, config, pred_dir, temps, itrs, threads):
        self.df = pd.DataFrame()
        self.config = config
        self.temps = temps
        self.itrs = itrs
        self.pred_dir = pred_dir
        self.thread_count = threads
        self.score_metrics = {
            'token_score': self.calc_token_usage_score,
            'exact_match': self.calc_exact_match,
            'spider_exact_match': self.calc_spider_exact_match,
            'exec_score': self.calc_exec_acc,
            'test_suit_score': self.calc_test_suit_acc,
            'sql_exec_time': self.total_sql_exec_time,
            'count': self.get_gold_queries_count
        }

    def get_pred_file_path(self, temp, itr):
        return os.path.join(self.pred_dir, f"{temp}_{itr + 1}_out")

    def evaluate(self, skip: bool = False):
        model_exec_times = {}
        if skip == False:
            for temp in self.temps:
                for itr in range(self.itrs):
                    exec_time = self.run_model(temp, itr)
                    if temp not in model_exec_times:
                        model_exec_times[temp] = {}
                    model_exec_times[temp][itr] = exec_time

        for temp in self.temps:
            for itr in range(self.itrs):
                exec_time = 0
                if not skip:
                    exec_time = model_exec_times[temp][itr]
                self.calc_single_run_metrics(temp, itr, exec_time)

        # print("_______created dataframe_______\n", self.df[['temp','exact_score','test_suit_acc',
        #                                                     'spider_exact_score','exec_score', 'total_sql_exec_time']])
        means = self.df.groupby('temp').mean()
        means.columns = [col + '_mean' for col in means.columns]

        cis = self.df.groupby('temp').agg(lib.confidence_level_interval)
        cis.columns = [col + '_ci' for col in cis.columns]

        result = means.join(cis)
        result = result.round(3)

        result.to_csv("scores.csv")

    def get_gold_pred_db(self, temp, iter):
        result = []

        with open(self.config.get_query_file_path()) as f_gold:
            gold_file = json.load(f_gold)
            with open(self.get_pred_file_path(temp, iter), 'r') as f_pred:
                f_pred_lines = f_pred.read().splitlines()[:-1]
                for idx, pred in enumerate(f_pred_lines):
                    gold = gold_file[idx]
                    db_id = gold['db_id']
                    gold_query = gold['query']

                    result.append([gold_query, pred, db_id])
        return result

    def calc_token_usage_score(self, temp: float, itr: int):
        total_toks = 0
        with open(self.get_pred_file_path(temp, itr), 'r') as f:
            lines = f.read().splitlines()
            total_tokens = lines[-1].split(":")[1]
            total_toks += int(total_tokens)
        return total_toks

    def calc_single_run_metrics(self, temp: float, itr: int, model_exec_time):
        scores = {'temp': temp, 'iter': itr, 'model_exec_time': model_exec_time}
        for metric_name in self.score_metrics:
            metric_fun = self.score_metrics[metric_name]
            score = metric_fun(temp, itr)
            scores[metric_name] = score

        result = pd.DataFrame([scores])
        self.df = pd.concat([self.df, result], ignore_index=True)

    # iter | tmp | token_score | exact_match | exec_acc

    def run_model(self, temp: float, itr: int):
        timer = Timer()
        timer.start()
        din_runner = DinRunner(self.config, self.get_pred_file_path(temp, itr), self.thread_count, temp)
        din_runner.run()
        din_runner.merge_results()
        return timer.stop().total_seconds() * 1000000

    def calc_exec_acc(self, temp, itr):
        score = 0
        total_sql_exec_time = 0
        res = self.get_gold_pred_db(temp, itr)
        for gold, pred, db_id in res:

            db_path = os.path.join(self.config.get_database_path(), db_id, f'{db_id}.sqlite')

            gold_sql_exec_res = exec_sql(db_path, gold)
            pred_sql_exec_res = exec_sql(db_path, pred)
            result = pred_sql_exec_res == gold_sql_exec_res

            if result:
                score += 1

        final_score = score / len(res) * 100
        return final_score

    def total_sql_exec_time(self, temp, itr):
        res = self.get_gold_pred_db(temp, itr)
        total_sql_exec_time = 0.0
        for gold, pred, db_id in res:
            db_path = os.path.join(self.config.get_database_path(), db_id, f'{db_id}.sqlite')

            timer = lib.Timer()
            timer.start()
            pred_sql_exec_res = exec_sql(db_path, pred)
            pred_sql_exec_time = timer.stop()
            total_sql_exec_time += pred_sql_exec_time.total_seconds() * 1000000

        return total_sql_exec_time

    def calc_exact_match(self, temp, itr):
        parser = ExactMatchParser(self.config.get_tables_file_path())
        res = self.get_gold_pred_db(temp, itr)
        score = 0
        parser_errors = []

        for gold, pred, db_id in res:
            try:
                gold_parser = parser.parse(gold, db_id)
                pred_parser = parser.parse(pred, db_id)
                if (gold_parser == pred_parser) or (pred_parser == gold_parser):
                    score += 1
            except Exception as e:
                parser_errors.append(pred)

        with open(os.path.join(self.pred_dir, "parser_errors.txt"), 'w') as f:
            for error in parser_errors:
                f.write(f"{error}")

        return score

    def calc_test_suit_acc(self, temp, itr):
        test_suite_acc = test_suite_exec_acc(
            gold=self.config.get_gold_file_path(),
            pred=self.get_pred_file_path(temp, itr),
            db_dir=self.config.get_database_path(),
            table=self.config.get_tables_file_path()
        )
        return test_suite_acc * 100

    def calc_spider_exact_match(self, temp, itr):
        exact_match = eval_exact_match(
            gold=self.config.get_gold_file_path(),
            pred=self.get_pred_file_path(temp, itr),
            db_dir=self.config.get_database_path(),
            table=self.config.get_tables_file_path()
        )
        return exact_match

    def get_gold_queries_count(self, temp, itr):
        res = self.get_gold_pred_db(temp, itr)
        return len(res)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--temps", nargs='+', type=float, help='different GPT"s temperature')
    parser.add_argument("--itrs", type=int, help='number of iterations')
    parser.add_argument("--thread_count", type=int, default=4, help='number of threads')

    config = ModelRunConfig(dataset_path="data/dataset/uniform",
                            query_file="all.json",
                            gold_file="all.gold.txt",
                            database_dir="database",
                            tables_file="tables.json")
    args = parser.parse_args()

    preprocessor = SpiderPreProcessor(config.get_query_file_path(), "out/spider.csv" )
    preprocessor.process()

    parser = BatchSqlParser("out/spider.csv")
    ASTlist = parser.process()

    categorizer = BatchCategoryExporter("out/spider_categories.csv")
    df = categorizer.process(ASTlist)
    evaluator = DinModelEvaluator(config, "data/out/din", args.temps, args.itrs, args.thread_count)
    evaluator.evaluate(skip=True)


    # evaluator.evaluate(skip=False)


if __name__ == "__main__":
    main()
