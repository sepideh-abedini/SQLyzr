import argparse
import sys
import os
from typing import List
import my_exe_eval
import lib
import csv
import datetime
import pandas as pd
import math
import statistics as stat
from src.third_party.spider.evaluation import eval_exact_match
from exact_match_prep import add_db_name_to_gold_sql
from src.third_party.test_suite_acc.evaluation import test_suite_exec_acc


# class DataStats():
#     def __init__(self, args):
#         self.args = args

#     def dev_json(self):
#         return "{}dev.json".format(self.args.dataset)


def run_model(args, temp):
    timer = lib.Timer()
    timer.start()
    dataset_dir = f"models/{args.dataset}"

    DIN_command = "python3 models/din_gen/{din_file} --dataset {dataset_dir} --output {output} --temp {temp}".format(
        model_file=args.model,
        dataset_dir=dataset_dir,
        output=args.output,
        temp=temp,
        din_file="models/din_gen/DIN-SQL.py"
    )

    token = "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"
    group_id = "org-uepjYjYK5sZA3J2gTh6bBlRU"
    question_file = "./models/dail/dataset/process/SPIDER-TEST_SQL_9-SHOT_EUCDISMASKPRESKLSIMTHR_QA-EXAMPLE_CTX-200_ANS-4096/"
    DAIL_command = f"python3.11 models/dail/ask_llm.py --db_dir {args.dataset + 'database'}  --question {question_file} --output {args.output} --temperature {temp} --openai_api_key {token} --openai_group_id {group_id} --model gpt-4 --end_index 20"

    # DAIL_command = f"./models/dail/run_dail_sql_mini.sh {token} {}"

    # if(args.model == "dail"):
    #     os.system(DAIL_command)
    # elif(args.model == "din_gen"):
    # os.system(DIN_command)
    res = os.system(DAIL_command)

    # Time that takes model generate all queries
    model_exec_time = timer.stop()
    return model_exec_time


def run_eval(args, temp):
    dev_json_path = "{}dev.json".format(args.dataset)
    gold_db, gold_sql_strs = my_exe_eval.read_gold_data(dev_json_path)

    pred_sql_strs = my_exe_eval.read_pred_sql(args.output)

    exec_acc_score = 0
    total_sql_exec_time = 0
    for db_name, g, p in zip(gold_db, gold_sql_strs, pred_sql_strs):
        # exec_acc_score: execution accuracy score
        # total_sql_exec_time: total execution time
        db_path = "{dataset_path}database/{db_name}/{db_name}.sqlite".format(dataset_path=args.dataset, db_name=db_name)
        valid_sql, sql_exec_time = my_exe_eval.eval_exec_acc(db_path, g, p, temp)
        if valid_sql:
            exec_acc_score += 1
            total_sql_exec_time += sql_exec_time.total_seconds()

    return exec_acc_score, total_sql_exec_time, len(gold_sql_strs)


def read_total_tokens(args):
    with open(args.output) as file:
        lines = file.read().splitlines()
        total_tokens = lines[-1].split(":")[1]
    return total_tokens


# def get_mean(score_list, score_name):
#     return sum(list(map(lambda x: int(x[score_name]), score_list))) / len(score_list)

def iter_on_run_data(args, temp):
    ITER_NUM = 3
    res = pd.DataFrame()

    for i in range(ITER_NUM):
        res = pd.concat([res, one_time_run_data(args, temp)], ignore_index=True)

    exec_acc_score_series = res.loc[:, 'exec_acc_score']
    exec_acc_score_mean = exec_acc_score_series.mean()
    exec_acc_score_ci = confidence_level_interval(exec_acc_score_series)

    total_sql_exec_time_series = res.loc[:, 'total_sql_exec_time']
    total_sql_exec_time_mean = total_sql_exec_time_series.mean()
    total_sql_exec_time_ci = confidence_level_interval(total_sql_exec_time_series)

    model_exec_time_series = res.loc[:, 'model_exec_time']
    model_exec_time_mean = model_exec_time_series.mean()
    model_exec_time_ci = confidence_level_interval(model_exec_time_series)

    total_tokens_series = res.loc[:, 'total_tokens']
    total_tokens_mean = total_tokens_series.mean()
    total_tokens_ci = confidence_level_interval(total_tokens_series)

    exact_match_score_series = res.loc[:, 'exact_match_score']
    exact_match_score_mean = exact_match_score_series.mean()
    exact_match_score_ci = confidence_level_interval(exact_match_score_series)

    test_suite_acc_score_series = res.loc[:, 'test_suite_acc']
    test_suite_acc_score_mean = test_suite_acc_score_series.mean()
    test_suite_acc_score_ci = confidence_level_interval(test_suite_acc_score_series)

    pd_result = pd.DataFrame([{'temperature': temp,
                               'exec_acc_score_mean': "%.5f" % exec_acc_score_mean,
                               'total_sql_exec_time_mean': "%.5f" % total_sql_exec_time_mean,
                               'model_exec_time_mean': "%.5f" % model_exec_time_mean,
                               'total_tokens_mean': "%.5f" % total_tokens_mean,
                               'exact_match_score_mean': "%.5f" % exact_match_score_mean,
                               'test_suite_acc_mean': "%.5f" % test_suite_acc_score_mean,
                               'exec_acc_score_ci': "[{0:.5f},{1:.5f}]".format(exec_acc_score_ci[0],
                                                                               exec_acc_score_ci[1]),
                               'total_sql_exec_time_ci': "[{0:.5f},{1:.5f}]".format(total_sql_exec_time_ci[0],
                                                                                    total_sql_exec_time_ci[1]),
                               'model_exec_time_ci': "[{0:.5f},{1:.5f}]".format(model_exec_time_ci[0],
                                                                                model_exec_time_ci[1]),
                               'total_tokens_ci': "[{0:.5f},{1:.5f}]".format(total_tokens_ci[0], total_tokens_ci[1]),
                               'exact_match_score_ci': "[{0:.5f},{1:.5f}]".format(exact_match_score_ci[0],
                                                                                  exact_match_score_ci[1]),
                               'test_suite_acc_score_ci': "[{0:.5f},{1:.5f}]".format(test_suite_acc_score_ci[0],
                                                                                     test_suite_acc_score_ci[1])
                               }])
    return pd_result


def one_time_run_data(args, temp):
    model_exec_time = datetime.timedelta(seconds=0)
    if not args.skip_run:
        model_exec_time = run_model(args, temp)

    exec_acc_score, total_sql_exec_time, total_sql_number = run_eval(args, temp)
    exec_acc_score = (exec_acc_score / total_sql_number) * 100

    total_tokens = read_total_tokens(args)

    dev_json_path = '{}/dev.json'.format(args.dataset)  # args.dataset = models/din_gen/sample_data
    add_db_name_to_gold_sql(dev_json_path)

    exact_match = eval_exact_match(
        gold='{}.final'.format(dev_json_path),
        pred=args.output,  # args.output = din_gen.pred.out
        db_dir='{}/database'.format(args.dataset),  # args.dataset = models/din_gen/sample_data
        table='{}/tables.json'.format(args.dataset)
    )
    #
    test_suite_acc = test_suite_exec_acc(
        gold='{}.final'.format(dev_json_path),
        pred=args.output,  # args.output = din_gen.pred.out
        db_dir='{}/database'.format(args.dataset),  # args.dataset = models/din_gen/sample_data
        table='{}/tables.json'.format(args.dataset)
    )

    results = {
        "exec_acc_score": exec_acc_score,
        "total_sql_exec_time": total_sql_exec_time,
        "model_exec_time": model_exec_time.total_seconds(),
        "total_tokens": int(total_tokens),
        "exact_match_score": exact_match,
        "test_suite_acc": test_suite_acc
    }

    pd_result = pd.DataFrame([results])

    return pd_result


def confidence_level_interval(column: pd.Series) -> float:
    CONFIDENCE = 0.95
    Z = 1.65
    SE = column.std() / math.sqrt(column.size)
    err_margin = Z * SE
    mean = column.mean()
    interavl_start = mean - err_margin
    interval_end = mean + err_margin
    return (interavl_start, interval_end)


def main():
    # print(sys.argv[0])
    # print(sys.argv[1], sys.argv[2])

    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str)
    parser.add_argument('--dataset', type=str)
    parser.add_argument('--output', type=str)
    parser.add_argument('--skip-run', action='store_true')
    args = parser.parse_args()

    columns = ['temp', 'gold', 'pred']
    with open("errors.csv", "w") as errors_file:
        dw = csv.DictWriter(errors_file, delimiter="\t", fieldnames=columns)
        dw.writeheader()
    res = pd.DataFrame()
    temps = [0.0, 0.2, 0.4, 0.7, 1.0]
    # temps = [0.0]
    for temp in temps:
        res = pd.concat([res, iter_on_run_data(args, temp)], ignore_index=True)

    res.to_csv("scores_mean.csv", sep='\t')


if __name__ == "__main__":
    main()
