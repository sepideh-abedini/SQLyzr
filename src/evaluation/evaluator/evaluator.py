import os
from itertools import product

import pandas as pd

from src.cat.categories import get_all_cats, CATS
from src.evaluation.configs import EVAL_CONF
from src.evaluation.evaluator.lib import confidence_level_interval
from src.evaluation.evaluator.model_eval_config import ModelEvalConfig
from src.evaluation.evaluator.score_metrics import GoldCount, TokenUsage, ExactMatch, SpiderExactMatch, ExecAcc, \
    TotalExecTime, TestSuitAcc
from src.evaluation.runner.runner_config import SingleRunConfig


def calc_score_data_row(config: SingleRunConfig, cat: str):
    score_data_row = {'temp': config.temp, 'itr': config.itr, 'cat': cat}
    score_metrics = [
        GoldCount(config),
        TokenUsage(config),
        ExactMatch(config),
        SpiderExactMatch(config),
        ExecAcc(config),
        TotalExecTime(config),
        TestSuitAcc(config)
    ]
    for metric in score_metrics:
        if os.path.exists(config.get_eval_gold_path_per_cat(cat)):
            score = metric.calc(cat)
        else:
            score = 0
        score_data_row[metric.name] = score
    return score_data_row


cats = get_all_cats(CATS)


def evaluate(config: ModelEvalConfig):
    rows = []
    for conf, cat in product(config.get_run_confs(), cats):
        row = calc_score_data_row(conf, cat)
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

    # score_names = [score for score in score_metrics.keys() if score != 'count']
    score_names = ["exact_match", "spider_exact_match", "exec_acc", "test_suit_acc", "total_exec_time"]

    score_mean_names = [score + "_mean" for score in score_names if
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


if __name__ == "__main__":
    evaluate(EVAL_CONF)
