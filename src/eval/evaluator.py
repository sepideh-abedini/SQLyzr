import os
from itertools import product

import pandas as pd

from src.cat.categories import get_all_cats, CATS
from src.cat.categorizer import Categorizer
from src.cat.tag_extractor import TagExtractor
from src.eval.configs import SMALL_EVAL_CONF, DIN_SMALL_CONF
from src.eval.model_eval_config import ModelEvalConfig
from src.eval.runner_config import SingleRunConfig
from src.eval.metrics import ExactMatch
from src.eval.score_metrics import get_pred_gold_db_id
from src.parse.parser import SqlParser


def calc_score_data_row(config: SingleRunConfig, cat: str):
    score_data_row = {'temp': config.temp, 'itr': config.itr, 'cat': cat}
    score_metrics = [
        GoldCount(config),
        # TokenUsage(config),
        ExactMatch(config),
        SpiderExactMatch(config),
        ExecAcc(config),
        # RelaxedExecAcc(config),
        TotalExecTime(config),
        # TestSuitAcc(config)
    ]
    for metric in score_metrics:
        if os.path.exists(config.get_eval_gold_path_per_cat(cat)):
            score = metric.calc(cat)
        else:
            score = 0
        score_data_row[metric.name] = score
    return score_data_row


cats = get_all_cats(CATS)


# cats = get_all_sub_cats(CATS)


def evaluate(config: ModelEvalConfig):
    rows = []
    for conf, cat in product(config.get_run_confs(), cats):
        row = calc_score_data_row(conf, cat)
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(config.get_scores_path("0"))
    exit(0)

    cat_grouped = df.groupby(['temp', 'itr'], as_index=False).sum()
    cat_grouped['cat'] = 'all'
    cat_grouped.to_csv(config.get_scores_path("1"))

    result = pd.concat([cat_grouped, df], join='inner', ignore_index=True)
    result.to_csv(config.get_scores_path("2"))

    result = result[result['count'] > 0]
    result.to_csv(config.get_scores_path("3"))

    # score_names = [score for score in score_metrics.keys() if score != 'count']
    # score_names = ["exact_match", "spider_exact_match", "exec_acc", "test_suit_acc", "total_exec_time"]
    score_names = ["exec_acc", "rel_exec_acc"]

    score_mean_names = [score + "_mean" for score in score_names if
                        score != 'count' and score != 'token_score']

    result[score_names] = result[score_names].div(result['count'], axis=0)
    result.to_csv(config.get_scores_path("3"))

    # means = result.groupby(['temp', 'cat']).mean()
    # means = means.drop(columns=['itr'])
    # means.to_csv(config.get_scores_path("means"))
    # means.columns = [col + '_mean' for col in means.columns]

    # cis = result.groupby(['temp', 'cat']).agg(confidence_level_interval)
    # cis = cis.drop(columns=['itr'])
    # cis.to_csv(config.get_scores_path("cis"))
    # cis.columns = [col + '_ci' for col in cis.columns]

    # final = means.join(cis)
    # final = means
    # final[score_mean_names] = final[score_mean_names] * 100
    # final = final.round(2)
    # final[score_mean_names] = (final[score_mean_names]).astype(str) + '%'
    # final.to_csv(config.get_scores_path("final"))


def calc_scores(config: ModelEvalConfig):
    parser = SqlParser()
    tag_extractor = TagExtractor()
    categorizer = Categorizer()
    df = pd.DataFrame()
    metrics = [
        ExactMatch("em", config.get_run_confs()[0].dataset_config)
    ]
    for conf in config.get_run_confs():
        pred_path = conf.get_pred_path()
        gold_path = conf.dataset_config.get_gold_path()
        data = get_pred_gold_db_id(pred_path, gold_path)
        scores = []
        for gold, pred, db_id in data:
            ast = parser.parse(gold)
            tags = tag_extractor.extract_tags(ast)
            cat = categorizer.get_category(tags.tag_set)
            example_scores = {"tmp": conf.temp, "itr": conf.itr, "cat": cat.name}
            for metric in metrics:
                score = metric.calc(gold, pred, db_id)
                example_scores[metric.name] = score
            scores.append(example_scores)
        ti_df = pd.DataFrame(scores)
        df = pd.concat([df, ti_df])
    df.to_csv("scores.csv")

    print("salam")


if __name__ == "__main__":
    calc_scores(DIN_SMALL_CONF)
    # evaluate(DIN_SMALL_CONF)
