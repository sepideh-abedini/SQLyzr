import asyncio
from typing import Optional, List, Set

import pandas as pd

from src.aug.auger import Auger
from src.cat.categories import CATS
from src.cat.sub_category import SubCategory
from src.configs.sqlyzr import SQLyzrConfig
from src.util.logger import log


class DatasetAugmentor:
    __config: SQLyzrConfig

    def __init__(self, config: SQLyzrConfig):
        self.__config = config

    async def augment_data(self):
        sub_cats = self.__find_cats_with_low_scores()
        if len(sub_cats) < 1:
            logger.debug(f"No category found with score below: {self.__config.error_threshold}, skipping augmentation")
            return
        logger.debug(f"Generating data for sub_categories: {sub_cats}")
        auger = Auger(self.__config, sub_cats)
        await auger.run()

    def __find_cats_with_low_scores(self) -> Set[SubCategory]:
        scores = pd.read_csv(self.__config.eval_conf.get_scores_path())
        scores = scores.sort_values('ea_mean')
        scores = scores[scores['sub_cat'] != "all"]
        scores = scores[scores['ea_mean'] < self.__config.error_threshold]
        if scores.shape[0] < 1:
            return set()
        return set(map(self.__find_cat, list(scores['sub_cat'])))

    @staticmethod
    def __find_cat(cat_name: str) -> Optional[SubCategory]:
        for c in CATS:
            for s in c.sub_cats:
                if s.name == cat_name:
                    return s
        return None
