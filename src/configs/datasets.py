from typing import Literal

from src.eval.dataset_config import DatasetConfig

SPIDER_SMALL = DatasetConfig(
    dataset_dir="data/spider",
    test_file="data.test.small.json",
    gold_file="data.test.small.gold.txt",
    train_file="data.train.small.json",
    tables_file="tables.small.json",
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

SPIDER_ALL_CAT = DatasetConfig(
    dataset_dir="data/spider",
    test_file="data.test.cat.json",
    gold_file="data.test.gold.txt",
    train_file="data.train.cat.json",
    tables_file="tables.json",
    db_dir="database"
)

SPIDER_MASK = DatasetConfig(
    dataset_dir="data/mask/spider",
    test_file="test.json",
    gold_file="test.gold.txt",
    train_file="train.json",
    tables_file="tables.all.json",
    db_dir="databases"
)

BIRD_MASK = DatasetConfig(
    dataset_dir="data/mask/bird",
    test_file="test.json",
    gold_file="test.gold.txt",
    train_file="train.json",
    tables_file="tables.all.json",
    db_dir="databases",
    dataset_type="bird"
)

BIRD_SMALL = DatasetConfig(
    dataset_dir="data/bird",
    test_file="data.test.small.json",
    gold_file="data.test.small.gold.txt",
    train_file="data.train.small.json",
    tables_file="tables.small.json",
    db_dir="database",
    dataset_type="bird"
)

BIRD_BAD = DatasetConfig(
    dataset_dir="data/bird",
    test_file="data.test.small.bad.json",
    gold_file="data.test.small.bad.gold.txt",
    train_file="data.train.small.json",
    tables_file="tables.small.bad.json",
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
    tables_file="tables.small.json",
    db_dir="database",
    dataset_type="beaver"
)

CUSTOM_SQLITE_DATASET = DatasetConfig(
    dataset_dir="data/custom",
    test_file="data.test.json",
    gold_file="data.test.gold.txt",
    train_file="data.train.json",
    tables_file="tables.json",
    db_dir="database",
    dataset_type="spider"
)

DATASETS = {
    "agg": {
        "small": [SPIDER_SMALL, BEAVER_SMALL]
    },
    "bird": {
        "small": [BIRD_SMALL],
        "all": [BIRD_ALL],
        "bad": [BIRD_BAD],
        "mask": [BIRD_MASK],
        #     "dev": BIRD_DEV,
        #     "train": BIRD_TRAIN
    },
    "spider": {
        "small": [SPIDER_SMALL],
        "500": [SPIDER_500],
        # "dev": SPIDER_DEV,
        # "test": SPIDER_TEST,
        # "train": SPIDER_TRAIN,
        "mask": [SPIDER_MASK],
        "all": [SPIDER_ALL]
    },
    "beaver": {
        "all": [BEAVER_ALL],
        "small": [BEAVER_SMALL]
    },
    "custom": {
        "all": [CUSTOM_SQLITE_DATASET]
    }
}

DatasetName = Literal["spider", "bird", "beaver", "agg", "custom"]
DatasetSize = Literal["small", "dev", "train", "test", "all", "500", "bad", "mask"]
