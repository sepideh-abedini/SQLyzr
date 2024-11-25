import os
from itertools import product

import pandas as pd

from src.cat.categories import get_all_cats, CATS
from src.evaluation.evaluator.lib import confidence_level_interval
from src.evaluation.evaluator.model_eval_config import ModelEvalConfig
from src.evaluation.evaluator.score_metrics import calc_gold_queries_count, calc_token_usage_score, calc_exact_match, \
    calc_spider_exact_match, calc_exec_acc, calc_test_suit_acc, calc_total_sql_exec_time
from src.evaluation.runner.dataset_config import SPIDER_SMALL

score_metrics = {
    'count': calc_gold_queries_count,
    'token_score': calc_token_usage_score,
    'exact_match': calc_exact_match,
    'spider_exact_match': calc_spider_exact_match,
    'exec_score': calc_exec_acc,
    'total_exec_time': calc_total_sql_exec_time,
    'test_suit_score': calc_test_suit_acc,
}


def calc_score_data_row(config: ModelEvalConfig, temp: float, itr: int, cat: str):
    score_data_row = {'temp': temp, 'itr': itr, 'cat': cat}
    pred_path = config.get_pred_path_per_cat(temp, itr, cat)
    gold_path = config.get_gold_path_per_cat(temp, itr, cat)
    runner_conf = config.get_runner_conf(temp, itr)
    db_path = runner_conf.dataset_config.get_db_path()
    tables_path = runner_conf.dataset_config.get_db_path()
    for metric_name in score_metrics:
        if os.path.exists(config.get_gold_path_per_cat(temp, itr, cat)):
            metric_fun = score_metrics[metric_name]
            score = metric_fun(config, temp, itr, cat)
        else:
            score = 0
        score_data_row[metric_name] = score
    return score_data_row


cats = get_all_cats(CATS)

if __name__ == "__main__":
    temps = [0.0, 0.2, 0.4, 0.7, 1.0]
    num_itrs = 4
    itrs = list(range(num_itrs))

    config = ModelEvalConfig(
        temps=temps,
        num_itrs=num_itrs,
        pred_dir="data/dum",
        eval_dir="data/eval",
        dataset_config=SPIDER_SMALL
    )

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

    cis = result.groupby(['temp', 'cat']).agg(confidence_level_interval)
    cis = cis.drop(columns=['itr'])
    cis.to_csv(config.get_scores_path("cis"))
    cis.columns = [col + '_ci' for col in cis.columns]

    final = means.join(cis)
    final[score_mean_names] = final[score_mean_names] * 100
    final = final.round(2)
    final[score_mean_names] = (final[score_mean_names]).astype(str) + '%'
    final.to_csv(config.get_scores_path("final"))
