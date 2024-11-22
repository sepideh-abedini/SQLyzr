import os
from itertools import product
from random import randrange

import pandas as pd

from src.cat.categories import get_all_sub_cats, CATS, get_all_cats
from src.evaluation.src.evaluator import lib
from src.evaluation.src.evaluator.data_generator import generate_evaluation_data
from src.evaluation.src.evaluator.model_eval_config import ModelEvalConfig
from src.evaluation.src.evaluator.score_metrics import calc_token_usage_score, calc_exact_match, \
    calc_spider_exact_match, calc_exec_acc, calc_test_suit_acc, calc_gold_queries_count

# cats = get_all_sub_cats(CATS)
cats = get_all_cats(CATS)


def export_to_file(df, out_path, row_to_line):
    with open(out_path, 'w') as out_file:
        for idx, row in df.iterrows():
            line = row_to_line(row)
            out_file.write(line)


def split_by_categories(config: ModelEvalConfig, temp: float, itr: int):
    df = pd.read_json(config.get_eval_data_path(temp, itr))
    dfs = {cat: sub_df for cat, sub_df in df.groupby('cat')}
    for cat, sub_df in dfs.items():
        export_to_file(sub_df, config.get_gold_path_per_cat(temp, itr, cat),
                       lambda row: f"{row['gold']}\t{row['db_id']}\n")
        export_to_file(sub_df, config.get_pred_path_per_cat(temp, itr, cat),
                       lambda row: f"{row['pred']}\n")
        with open(config.get_pred_path_per_cat(temp, itr, cat), 'a') as pred_file:
            pred_file.write(f"tokens:{randrange(15000, 30000)}\n")


def generate_pred_data(config: ModelEvalConfig, temps, itrs):
    for temp, itr in product(temps, itrs):
        generate_evaluation_data(config.get_pred_path(temp, itr),
                                 config.get_gold_file_path(),
                                 config.get_eval_data_path(temp, itr),
                                 1000)


score_metrics = {
    'count': calc_gold_queries_count,
    'token_score': calc_token_usage_score,
    'exact_match': calc_exact_match,
    'spider_exact_match': calc_spider_exact_match,
    'exec_score': calc_exec_acc,
    'test_suit_score': calc_test_suit_acc,
}


def calc_score_data_row(config: ModelEvalConfig, temp: float, itr: int, cat: str):
    score_data_row = {'temp': temp, 'itr': itr, 'cat': cat}
    pred_path = config.get_pred_path_per_cat(temp, itr, cat)
    gold_path = config.get_gold_path_per_cat(temp, itr, cat)
    db_path = config.get_database_path()
    tables_path = config.get_tables_file_path()
    for metric_name in score_metrics:
        if os.path.exists(config.get_gold_path_per_cat(temp, itr, cat)):
            metric_fun = score_metrics[metric_name]
            score = metric_fun(config, temp, itr, cat)
        else:
            score = 0
        score_data_row[metric_name] = score
    return score_data_row


def main():
    # config = ModelEvalConfig(dataset_path="data/spider",
    #                          pred_dir="data/out/din_gen",
    #                          eval_dir="data/out/din_eval",
    #                          query_file="dev.json",
    #                          gold_file="dev_gold.sql",
    #                          database_dir="database",
    #                          tables_file="tables.json",
    #                          scores_file="scores.csv"
    #                          )

    config = ModelEvalConfig(dataset_path="data/spider",
                             pred_dir="data/out/din",
                             eval_dir="data/out/din_eval",
                             query_file="dev.json",
                             gold_file="gold_500.txt",
                             database_dir="database",
                             tables_file="tables.json",
                             scores_file="scores.csv"
                             )
    temps = [0.0, 0.2, 0.4, 0.7, 1.0]
    # temps = [0.0]
    itrs = range(1, 4)
    # itrs = range(1, 2)

    generate_pred_data(config, temps, itrs)
    #
    for temp, itr in product(temps, itrs):
        split_by_categories(config, temp, itr)
    # return

    rows = []
    for temp, itr, cat in product(temps, itrs, cats):
        row = calc_score_data_row(config, temp, itr, cat)
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(config.get_scores_path("0"))

    cat_grouped = df.groupby(['temp', 'itr'], as_index=False).sum()
    cat_grouped['cat'] = 'all'
    cat_grouped.to_csv(config.get_scores_path("1"))

    result = pd.concat([cat_grouped, df], join='inner', ignore_index=True)
    result.to_csv(config.get_scores_path("2"))

    result = result[result['count'] > 0]
    result.to_csv(config.get_scores_path("3"))

    score_names = [score for score in score_metrics.keys() if score != 'count']
    score_mean_names = [score + "_mean" for score in score_metrics.keys() if
                        score != 'count' and score != 'token_score']

    result[score_names] = result[score_names].div(result['count'], axis=0)
    result.to_csv(config.get_scores_path("3"))

    means = result.groupby(['temp', 'cat']).mean()
    means = means.drop(columns=['itr'])
    means.to_csv(config.get_scores_path("means"))
    means.columns = [col + '_mean' for col in means.columns]

    cis = result.groupby(['temp', 'cat']).agg(lib.confidence_level_interval)
    cis = cis.drop(columns=['itr'])
    cis.to_csv(config.get_scores_path("cis"))
    cis.columns = [col + '_ci' for col in cis.columns]

    final = means.join(cis)
    final[score_mean_names] = final[score_mean_names] * 100
    final = final.round(2)
    final[score_mean_names] = (final[score_mean_names]).astype(str) + '%'
    final.to_csv(config.get_scores_path("final"))


if __name__ == "__main__":
    main()
