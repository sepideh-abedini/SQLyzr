# from turtle import pd
import json
import os.path

import pandas as pd
import math
from exact_match import ExactMatchParser
from src.spider.evaluation import eval_exact_match
from src.evaluation.src.models_runner.din_runner import DinRunner


def confidence_level_interval(column: pd.Series) -> float:
    CONFIDENCE = 0.95
    Z = 1.65
    SE = column.std() / math.sqrt(column.size)
    err_margin = Z * SE
    mean = column.mean()
    interval_start = mean - err_margin
    interval_end = mean + err_margin
    return (interval_start, interval_end)


class DinModelEvaluator:

    def __init__(self):
        self.df = pd.DataFrame()
        self.temps = [0.0, 0.2, 0.4, 0.7, 1.0]
        self.itrs = 3
        self.pred_results_dir = "data/out/pred_results/din"
        self.dataset_dir = "data/dataset/data"

    def get_pred_file_path(self, temp, itr):
        return os.path.join(self.pred_results_dir, f"{temp}_{itr+1}_out")

    def evaluate(self, skip: bool = False):
        # print("first")
        if skip == False:
            for temp in self.temps:
                self.run_model_k_times(temp, self.itrs)

        for temp in self.temps:
            for itr in range(self.itrs):
                self.calc_single_run_metrics(temp, itr)

        print("_______created dataframe_______\n", self.df)

    def calc_token_usage_score(self, temp: float, itr: int):
        total_toks = 0
        with open(self.get_pred_file_path(temp, itr), 'r') as f:
            lines = f.read().splitlines()
            total_tokens = lines[-1].split(":")[1]
            total_toks += int(total_tokens)
        return total_toks

    def calc_single_run_metrics(self, temp: float, itr: int):
        token_score = self.calc_token_usage_score(temp, itr)
        exact_score = self.calc_exact_match(temp, itr)
        spider_exact_score = self.calc_spider_exact_match(temp, itr)
        exec_score = self.calc_exec_acc(temp, itr)
        test_suit_score = self.calc_test_suit_acc(temp, itr)

        result = pd.DataFrame([{"temp": temp, "iter": itr + 1, \
                                "token_score": token_score, "exec_score": exec_score, \
                                "spider_exact_score": spider_exact_score, \
                                "exact_score": exact_score, "test_suit_acc": test_suit_score}])

        self.df = pd.concat([self.df, result], ignore_index=True)

    def run_model_k_times(self, temp: float, itr: int):
        # print("second")
        for i in range(itr):
            self.run_model(temp, i)
            # print("i", i)

    # iter | tmp | token_score | exact_match | exec_acc

    def run_model(self, temp: float, itr: int):
        din_runner = DinRunner()
        din_runner.run(self.dataset_dir, self.get_pred_file_path(temp, itr), temp)

    def calc_exec_acc(self, temp, itr):
        return 0

    def calc_exact_match(self, temp, itr):
        parser = ExactMatchParser(os.path.join(self.dataset_dir, "tables.json"))
        with open(os.path.join(self.dataset_dir, "dev.json"), "r") as f_gold:
            gold_file = json.load(f_gold)
            score = 0
            with open(self.get_pred_file_path(temp, itr), 'r') as f_pred:
                f_pred_lines = f_pred.read().splitlines()[:-1]
                for idx, pred in enumerate(f_pred_lines):
                    gold = gold_file[idx]
                    db_id = gold['db_id']
                    gold_query = gold['query']
                    gold_parser = parser.parse(gold_query, db_id)
                    pred_parser = parser.parse(pred, db_id)
                    if (gold_parser == pred_parser) or (pred_parser == gold_parser):
                        score += 1
        return score

    def calc_test_suit_acc(self, temp, itr):
        return 0

    def calc_spider_exact_match(self, temp, itr):
        exact_match = eval_exact_match(
            gold=os.path.join(self.dataset_dir, "gold.txt"),
            pred=self.get_pred_file_path(temp, itr),
            db_dir=os.path.join(self.dataset_dir, "database"),
            table=os.path.join(self.dataset_dir, "tables.json")
        )
        return exact_match


def main():
    evaluator = DinModelEvaluator()
    evaluator.evaluate(skip=True)


if __name__ == "__main__":
    main()
