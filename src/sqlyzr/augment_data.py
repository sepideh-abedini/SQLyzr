from typing import Optional, Set, Any

import pandas as pd
from loguru import logger

from src.aug.auger import Auger
from src.aug.text_sql_pair import TextSqlPair, GeneratedTextSqlPair
from src.cat.categories import CATS
from src.cat.sub_category import SubCategory
from src.configs.sqlyzr_config import SQLyzrConfig
from src.dataset.models import SpiderExample
from src.util.file_utils import read_json, write_json
from src.util.log_util import alog
from src.util.model_utils import read_jsonl


class DatasetAugmentor:
    __config: SQLyzrConfig

    def __init__(self, config: SQLyzrConfig):
        self.__config = config

    @alog("Dataset augmentation")
    async def augment_data(self, expand: bool = False):
        logger.info(f"Score threshold for augmentation: {self.__config.error_threshold}")
        sub_cats = self.__find_cats_with_low_scores()
        logger.info(f"Found {len(sub_cats)} subs with with low scores: {sub_cats}")

        if len(sub_cats) < 1:
            logger.info(f"No category found with score below: {self.__config.error_threshold}, skipping augmentation")
            return

        for ds_conf in self.__config.eval_conf.dataset_configs:
            auger = Auger(self.__config, ds_conf, sub_cats)
            await auger.run()
        if expand:
            await self.expand_workload()

    def to_workload_entry(self, aug_entry: GeneratedTextSqlPair) -> dict[str, Any]:
        return SpiderExample(question=aug_entry.question, query=aug_entry.sql, db_id=aug_entry.db_id).dict()

    async def expand_workload(self):
        for ds_conf in self.__config.eval_conf.dataset_configs:
            logger.info(f"Expanding dataset: {ds_conf.get_test_path()}")
            aug_path = self.__config.get_aug_out(ds_conf.dataset_type)
            aug_data = read_jsonl(aug_path, GeneratedTextSqlPair)
            aug_data = list(map(self.to_workload_entry, aug_data))
            orig_data = read_json(ds_conf.get_test_path())
            new_data = orig_data + aug_data
            logger.info(f"Dataset expanded: {len(orig_data)} -> {len(new_data)}")
            write_json(ds_conf.get_test_path(), new_data)
            gold_path = ds_conf.get_test_path().replace(".json", ".gold.txt")
            with open(gold_path, "w") as f:
                for row in new_data:
                    f.write(f"{row['query']}\t{row['db_id']}\n")

    def __find_cats_with_low_scores(self) -> Set[SubCategory]:
        scores = pd.read_csv(self.__config.eval_conf.get_scores_path())
        scores = scores.sort_values('ea_mean')
        scores = scores[scores['sub'] != "all"]
        scores = scores[scores['ea_mean'] < self.__config.error_threshold]
        if scores.shape[0] < 1:
            return set()
        return set(map(self.__find_cat, list(scores['sub'])))

    @staticmethod
    def __find_cat(cat_name: str) -> Optional[SubCategory]:
        for c in CATS:
            for s in c.sub_cats:
                if s.name == cat_name:
                    return s
        return None
