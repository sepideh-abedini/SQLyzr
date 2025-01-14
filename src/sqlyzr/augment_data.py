import asyncio
from typing import Optional, List

import pandas as pd

from src.aug.auger import Auger
from src.cat.categories import CATS
from src.cat.statement_category import StatementCategory
from src.cat.sub_category import SubCategory
from src.configs.sqlyzr import SQLyzrConfig
from src.eval.model_eval_config import ModelEvalConfig
from src.sqlyzr.sqlyzr_processor import SqlyzrProcessor


class DatasetAugmentor(SqlyzrProcessor):
    async def run(self):
        await augment_data(self.conf)


def find_cats_with_low_scores(config: SQLyzrConfig) -> List[SubCategory]:
    scores = pd.read_csv(config.eval_conf.get_scores_path())
    scores = scores.sort_values('ea_mean')
    scores = scores[scores['sub_cat'] != "all"]
    scores = scores[scores['ea_mean'] < config.error_threshold]
    if scores.shape[0] < 1:
        raise RuntimeError(f"No category found with score below: {config.error_threshold}")
    return set(list(map(find_cat, list(scores['sub_cat']))))


def find_cat(cat_name: str) -> Optional[SubCategory]:
    for c in CATS:
        for s in c.sub_cats:
            if s.name == cat_name:
                return s
    return None


async def augment_data(config: SQLyzrConfig):
    sub_cats = find_cats_with_low_scores(config)
    print(f"Generating data for sub_categories: {sub_cats}")
    auger = Auger(config, sub_cats)
    await auger.run()
