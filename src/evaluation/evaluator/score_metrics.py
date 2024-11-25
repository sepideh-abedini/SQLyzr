from src.evaluation.evaluator.lib import exec_sql
from src.evaluation.evaluator.model_eval_config import ModelEvalConfig
from src.third_party.spider.evaluation import eval_exact_match
from src.third_party.test_suite_acc.evaluation import test_suite_exec_acc


def get_pred_gold_db_id(pred_path, gold_path):
    with open(pred_path) as pred_file, open(gold_path) as gold_file:
        pred_file_lines = pred_file.readlines()
        rows = []
        for i, gold_line in enumerate(gold_file):
            gold_sql, db_id = gold_line.strip().split("\t")
            pred_sql = pred_file_lines[i].strip()
            rows.append((pred_sql, gold_sql, db_id))
    return rows


def calc_token_usage_score(config: ModelEvalConfig, temp: float, itr: int, cat: str):
    total_toks = 0
    pred_path = config.get_pred_path_per_cat(temp, itr, cat)
    with open(pred_path) as f:
        lines = f.read().splitlines()
        total_tokens = lines[-1].split(":")[1]
        total_toks += int(total_tokens)
    return total_toks


def calc_exact_match(config: ModelEvalConfig, temp: float, itr: int, cat: str):
    pred_path = config.get_pred_path_per_cat(temp, itr, cat)
    gold_path = config.get_gold_path_per_cat(temp, itr, cat)
    data = get_pred_gold_db_id(pred_path, gold_path)
    parser = ExactMatchParser(config.get_tables_file_path())
    score = 0
    parser_errors = []
    for pred, gold, db_id in data:
        try:
            gold_parser = parser.parse(gold, db_id)
            pred_parser = parser.parse(pred, db_id)
            if (gold_parser == pred_parser) or (pred_parser == gold_parser):
                score += 1
        except Exception as e:
            parser_errors.append(pred)

    return score


def calc_spider_exact_match(config: ModelEvalConfig, temp: float, itr: int, cat: str):
    exact_match = eval_exact_match(
        gold=config.get_gold_path_per_cat(temp, itr, cat),
        pred=config.get_pred_path_per_cat(temp, itr, cat),
        db_dir=config.get_database_path(),
        table=config.get_tables_file_path()
    )
    return exact_match


def calc_exec_acc(config: ModelEvalConfig, temp: float, itr: int, cat: str):
    score = 0
    pred_path = config.get_pred_path_per_cat(temp, itr, cat)
    gold_path = config.get_gold_path_per_cat(temp, itr, cat)
    data = get_pred_gold_db_id(pred_path, gold_path)
    for gold, pred, db_id in data:
        db_file_path = config.get_database_file_path(db_id)
        gold_sql_exec_res = exec_sql(db_file_path, gold)
        pred_sql_exec_res = exec_sql(db_file_path, pred)
        result = (gold_sql_exec_res and pred_sql_exec_res) and (pred_sql_exec_res == gold_sql_exec_res)
        if result:
            score += 1
    return score


def calc_test_suit_acc(config: ModelEvalConfig, temp: float, itr: int, cat: str):
    test_suite_acc = test_suite_exec_acc(
        gold=config.get_gold_path_per_cat(temp, itr, cat),
        pred=config.get_pred_path_per_cat(temp, itr, cat),
        db_dir=config.get_database_path(),
        table=config.get_tables_file_path()
    )
    return test_suite_acc * calc_gold_queries_count(config, temp, itr, cat)


def calc_gold_queries_count(config: ModelEvalConfig, temp: float, itr: int, cat: str):
    gold_path = config.get_gold_path_per_cat(temp, itr, cat)
    with open(gold_path) as gold_file:
        return len(gold_file.readlines())
