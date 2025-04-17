from typing import Literal

from src.eval.dataset_config import DatasetConfig

SPIDER_SMALL = DatasetConfig(
    dataset_dir="data/spider",
    test_file="data.test.small.json",
    gold_file="data.test.small.gold.txt",
    train_file="data.train.small.json",
    tables_file="tables.json",
    db_dir="database"
)

SPIDER_500 = DatasetConfig(
    dataset_dir="data/spider",
    test_file="data.500.json",
    gold_file="data.500.gold.txt",
    train_file="data.500.json",
    tables_file="tables.json",
    db_dir="database"
)

SPIDER_ALL = DatasetConfig(
    dataset_dir="data/spider",
    test_file="data.test.json",
    gold_file="data.test.gold.txt",
    train_file="data.train.json",
    tables_file="tables.json",
    db_dir="database"
)

BIRD_SMALL = DatasetConfig(
    dataset_dir="data/bird",
    test_file="data.test.small.json",
    gold_file="data.test.small.gold.txt",
    train_file="data.train.small.json",
    tables_file="tables.json",
    db_dir="database",
    dataset_type="bird"
)

BIRD_ALL = DatasetConfig(
    dataset_dir="data/bird",
    test_file="data.test.json",
    gold_file="data.test.gold.txt",
    train_file="data.train.json",
    tables_file="tables.json",
    db_dir="database",
    dataset_type="bird"
)

BEAVER_ALL = DatasetConfig(
    dataset_dir="data/beaver",
    test_file="data.test.json",
    gold_file="data.test.gold.txt",
    train_file="data.train.json",
    tables_file="tables.json",
    db_dir="database",
    dataset_type="beaver"
)

BEAVER_SMALL = DatasetConfig(
    dataset_dir="data/beaver",
    test_file="data.test.small.json",
    gold_file="data.test.small.gold.txt",
    train_file="data.train.small.json",
    tables_file="tables.json",
    db_dir="database",
    dataset_type="beaver"
)

AGG_SMALL = [
    SPIDER_SMALL, BEAVER_SMALL
]

DATASETS = {
    "agg": {
        "small": AGG_SMALL
    },
    "bird": {
        "small": [BIRD_SMALL],
        "all": [BIRD_ALL]
        #     "dev": BIRD_DEV,
        #     "train": BIRD_TRAIN
    },
    "spider": {
        "small": [SPIDER_SMALL],
        "500": [SPIDER_500],
        # "dev": SPIDER_DEV,
        # "test": SPIDER_TEST,
        # "train": SPIDER_TRAIN,
        "all": [SPIDER_ALL]
    },
    "beaver": {
        "all": [BEAVER_ALL],
        "small": [BEAVER_SMALL]
    }
}

DatasetName = Literal["spider", "bird", "beaver", "agg"]
DatasetSize = Literal["small", "dev", "train", "test", "all", "500"]
