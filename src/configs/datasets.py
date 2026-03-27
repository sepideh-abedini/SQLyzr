import os
from typing import Literal

from src.eval.dataset_config import DatasetConfig

BASE_DIR = os.environ.get("SQLYZR_DATA_DIR", "data")

SPIDER_SMALL = DatasetConfig(
    dataset_dir=f"{BASE_DIR}/spider",
    test_file="data.test.small.json",
    gold_file="data.test.small.gold.txt",
    train_file="data.train.small.json",
    tables_file="tables.small.json",
    db_dir="database",
    ver="v0",
    aug_db_id="musical"
)

SPIDER_500 = DatasetConfig(
    dataset_dir=f"{BASE_DIR}/spider",
    test_file="data.500.json",
    gold_file="data.500.gold.txt",
    train_file="data.500.json",
    tables_file="tables.json",
    db_dir="database"
)

SPIDER_ALL = DatasetConfig(
    dataset_dir=f"{BASE_DIR}/spider",
    test_file="data.test.json",
    gold_file="data.test.gold.txt",
    train_file="data.train.json",
    tables_file="tables.json",
    db_dir="database"
)

SPIDER_ALL_CAT = DatasetConfig(
    dataset_dir=f"{BASE_DIR}/spider",
    test_file="data.test.cat.json",
    gold_file="data.test.gold.txt",
    train_file="data.train.cat.json",
    tables_file="tables.json",
    db_dir="database"
)

AUG_ALL = DatasetConfig(
    dataset_dir=f"{BASE_DIR}/spider_aug",
    test_file="data.test.cat.json",
    gold_file="data.test.cat.gold.txt",
    train_file="data.train.cat.json",
    tables_file="tables.json",
    db_dir="database"
)

AUG_SMALL = DatasetConfig(
    dataset_dir=f"{BASE_DIR}/spider_aug",
    test_file="data.test.small.json",
    gold_file="data.test.small.gold.txt",
    train_file="data.train.small.json",
    tables_file="tables.small.json",
    db_dir="database",
    ver="v0"
)

SPIDER_MASK = DatasetConfig(
    dataset_dir=f"{BASE_DIR}/mask/spider",
    test_file="test.json",
    gold_file="test.gold.txt",
    train_file="train.json",
    tables_file="tables.all.json",
    db_dir="databases"
)

BIRD_MASK = DatasetConfig(
    dataset_dir=f"{BASE_DIR}/mask/bird",
    test_file="test.json",
    gold_file="test.gold.txt",
    train_file="train.json",
    tables_file="tables.all.json",
    db_dir="databases",
    dataset_type="bird"
)

BIRD_SMALL = DatasetConfig(
    dataset_dir=f"{BASE_DIR}/bird",
    test_file="data.test.small.json",
    gold_file="data.test.small.gold.txt",
    train_file="data.train.small.json",
    tables_file="tables.small.json",
    db_dir="database",
    dataset_type="bird",
    ver="v0"
)

BIRD_BAD = DatasetConfig(
    dataset_dir=f"{BASE_DIR}/bird",
    test_file="data.test.small.bad.json",
    gold_file="data.test.small.bad.gold.txt",
    train_file="data.train.small.json",
    tables_file="tables.small.bad.json",
    db_dir="database",
    dataset_type="bird"
)

BIRD_ALL = DatasetConfig(
    dataset_dir=f"{BASE_DIR}/bird",
    test_file="data.test.json",
    gold_file="data.test.gold.txt",
    train_file="data.train.json",
    tables_file="tables.json",
    db_dir="database",
    dataset_type="bird"
)

BEAVER_ALL = DatasetConfig(
    dataset_dir=f"{BASE_DIR}/beaver",
    test_file="data.test.json",
    gold_file="data.test.gold.txt",
    train_file="data.train.json",
    tables_file="tables.json",
    db_dir="database",
    dataset_type="beaver"
)

BEAVER_SMALL = DatasetConfig(
    dataset_dir=f"{BASE_DIR}/beaver",
    test_file="data.test.small.json",
    gold_file="data.test.small.gold.txt",
    train_file="data.train.small.json",
    tables_file="tables.small.json",
    db_dir="database",
    dataset_type="beaver",
    ver="v0"
)

CUSTOM_SQLITE_DATASET = DatasetConfig(
    dataset_dir=f"{BASE_DIR}/custom",
    test_file="data.test.v0.json",
    gold_file="data.test.gold.v0.txt",
    train_file="data.train.json",
    tables_file="tables.json",
    db_dir="database",
    dataset_type="spider"
)

ALIGNED_ALL = DatasetConfig(
    dataset_dir=f"{BASE_DIR}/spider_aug",
    test_file="data.test.cat.json",
    gold_file="data.test.cat.gold.txt",
    train_file="data.train.cat.json",
    tables_file="tables.json",
    db_dir="database"
)

DATASETS = {
    "aggregate": {
        "small": [SPIDER_SMALL, BIRD_SMALL, BEAVER_SMALL],
        "full": [SPIDER_ALL, BIRD_ALL, BEAVER_ALL]
    },
    "bird": {
        "small": [BIRD_SMALL],
        "full": [BIRD_ALL],
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
        "full": [SPIDER_ALL]
    },
    "aug": {
        "small": [AUG_SMALL],
        "full": [AUG_ALL]
    },
    "aligned": {
        "full": [ALIGNED_ALL]
    },
    "beaver": {
        "full": [BEAVER_ALL],
        "small": [BEAVER_SMALL]
    },
    "custom": {
        "full": [SPIDER_SMALL]
    },
    'sqlyzr': {
        "s1": [SPIDER_SMALL],
        "s2": [BIRD_SMALL],
        "s3": [BEAVER_ALL],
        "full": [SPIDER_ALL, BIRD_ALL, BEAVER_ALL],
        "aligned": [SPIDER_SMALL]
    }
}

DatasetName = Literal["spider", "bird", "beaver", "aggregate", "aligned", "custom", "aug", "sqlyzr"]
DatasetSize = Literal["small", "dev", "train", "test", "full", "500", "bad", "mask", "s1", "s2", "s3", "aligned"]
