import asyncio
from typing import Optional

import pandas as pd

from src.aug.auger import Auger
from src.cat.categories import CATS
from src.cat.statement_category import StatementCategory
from src.eval.model_eval_config import ModelEvalConfig
from src.sqlyzr_conf import SQLyzrConfig


def find_worst_cat(config: ModelEvalConfig):
    scores = pd.read_csv(config.get_scores_path())
    scores = scores.sort_values('rea_mean')
    scores = scores[scores['cat'] != "all"]
    scores = scores.head(1)
    return scores['cat'].item()


def find_cat(cat_name: str) -> Optional[StatementCategory]:
    for c in CATS:
        if c.name == cat_name:
            return c
    return None


def augment_data(config: SQLyzrConfig):
    worst_cat = find_worst_cat(config.eval_conf)
    print(f"Worst category is: {worst_cat}")
    cat = find_cat(worst_cat)
    auger = Auger(config.aug_out, cat, config.aug_db_id, config.eval_conf.dataset_config)
    asyncio.run(auger.run())
