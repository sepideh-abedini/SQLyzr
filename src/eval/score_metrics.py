from abc import ABC, abstractmethod

from src.eval.exact_match import ExactMatchParser
from src.eval.lib import exec_sql
from src.eval import lib
from src.eval.runner_config import SingleRunConfig
from src.third_party.spider.evaluation import get_spider_exact_match


class EvalMetric(ABC):
    name: str
    run_conf: SingleRunConfig

    def __init__(self, name, conf):
        self.name = name
        self.run_conf = conf

    @abstractmethod
    def calc(self, cat: str):
        pass


class ExactMatch(EvalMetric):
    def __init__(self, conf):
        super().__init__("exact_match", conf)

    def calc(self, cat: str):
        pred_path = self.run_conf.get_eval_pred_path_per_cat(cat)
        gold_path = self.run_conf.get_eval_gold_path_per_cat(cat)
        data = get_pred_gold_db_id(pred_path, gold_path)
        parser = ExactMatchParser(self.run_conf.dataset_config.get_tables_path())
        score = 0
        parser_errors = []
        for pred, gold, db_id in data:
            try:
                gold_parser = parser.parse(gold, db_id)
                pred_parser = parser.parse(pred, db_id)
                if (gold_parser == pred_parser) or (pred_parser == gold_parser):
                    score += 1
            except Exception as e:
                print(e)
                parser_errors.append(pred)
        return score


# class SpiderExactMatch(EvalMetric):
#     def __init__(self, conf):
#         super().__init__("spider_exact_match", conf)
#
#     def calc(self, cat: str):
#         exact_match = eval_exact_match(
#             gold=self.run_conf.get_eval_gold_path_per_cat(cat),
#             pred=self.run_conf.get_eval_pred_path_per_cat(cat),
#             db_dir=self.run_conf.dataset_config.get_db_path(),
#             table=self.run_conf.dataset_config.get_tables_path()
#         )
#         return exact_match


class SpiderExactMatch(EvalMetric):
    def __init__(self, conf):
        super().__init__("spider_exact_match", conf)

    def calc(self, cat: str):
        score = 0
        pred_path = self.run_conf.get_eval_pred_path_per_cat(cat)
        gold_path = self.run_conf.get_eval_gold_path_per_cat(cat)
        data = get_pred_gold_db_id(pred_path, gold_path)
        for gold, pred, db_id in data:
            score += get_spider_exact_match(pred, f"{gold}\t{db_id}", self.run_conf.dataset_config.get_db_path(),
                                            self.run_conf.dataset_config.get_tables_path())
        return score


class ExecAcc(EvalMetric):
    def __init__(self, conf):
        super().__init__("exec_acc", conf)

    def calc(self, cat: str):
        score = 0
        pred_path = self.run_conf.get_eval_pred_path_per_cat(cat)
        gold_path = self.run_conf.get_eval_gold_path_per_cat(cat)
        data = get_pred_gold_db_id(pred_path, gold_path)
        for gold, pred, db_id in data:
            db_file_path = self.run_conf.dataset_config.get_db_file_path(db_id)
            gold_sql_exec_res = exec_sql(db_file_path, gold)
            pred_sql_exec_res = exec_sql(db_file_path, pred)
            result = (gold_sql_exec_res and pred_sql_exec_res) and (pred_sql_exec_res == gold_sql_exec_res)
            if result:
                score += 1
        return score


class GoldCount(EvalMetric):
    def __init__(self, conf):
        super().__init__("count", conf)

    def calc(self, cat: str):
        gold_path = self.run_conf.get_eval_gold_path_per_cat(cat)
        with open(gold_path) as gold_file:
            return len(gold_file.readlines())


class TotalExecTime(EvalMetric):
    def __init__(self, conf):
        super().__init__("total_exec_time", conf)

    def calc(self, cat: str):
        pred_path = self.run_conf.get_eval_pred_path_per_cat(cat)
        gold_path = self.run_conf.get_eval_gold_path_per_cat(cat)
        data = get_pred_gold_db_id(pred_path, gold_path)
        total_sql_exec_time = 0.0
        for gold, pred, db_id in data:
            db_file_path = self.run_conf.dataset_config.get_db_file_path(db_id)
            timer = lib.Timer()
            timer.start()
            exec_sql(db_file_path, pred)
            pred_sql_exec_time = timer.stop()
            total_sql_exec_time += pred_sql_exec_time.total_seconds()

        return total_sql_exec_time


def get_pred_gold_db_id(pred_path, gold_path):
    with open(pred_path) as pred_file, open(gold_path) as gold_file:
        pred_file_lines = pred_file.readlines()
        rows = []
        for i, gold_line in enumerate(gold_file):
            gold_sql, db_id = gold_line.strip().split("\t")
            pred_sql = pred_file_lines[i].strip()
            rows.append((pred_sql, gold_sql, db_id))
    return rows
