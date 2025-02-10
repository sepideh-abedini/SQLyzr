from typing import Literal

from src.eval.dataset_config import DatasetConfig

BIRD_SMALL = DatasetConfig(
    dataset_dir="data/bird/dev",
    data_file="dev.conv.small.json",
    gold_file="dev.conv.small.gold.txt",
    tables_file="dev_tables.json",
    db_dir="dev_databases"
)

BIRD_DEV = DatasetConfig(
    dataset_dir="data/bird/dev",
    data_file="dev.conv.json",
    gold_file="dev.gold.txt",
    tables_file="dev_tables.json",
    db_dir="dev_databases"
)

BIRD_TRAIN = DatasetConfig(
    dataset_dir="data/bird/train",
    data_file="train.conv.json",
    gold_file="train.conv.gold.txt",
    tables_file="train_tables.json",
    db_dir="train_databases"
)

SPIDER_SMALL = DatasetConfig(
    dataset_dir="data/spider/small",
    data_file="data.json",
    gold_file="data.gold.txt",
    tables_file="tables.json",
    db_dir="../database"
)

SPIDER_DEV = DatasetConfig(
    dataset_dir="data/spider/dev",
    data_file="data.json",
    gold_file="data.gold.txt",
    tables_file="tables.json",
    db_dir="../database"
)

SPIDER_TEST = DatasetConfig(
    dataset_dir="data/spider/test",
    data_file="data.json",
    gold_file="data.gold.txt",
    tables_file="tables.json",
    db_dir="../database"
)

SPIDER_TRAIN = DatasetConfig(
    dataset_dir="data/spider/train",
    data_file="data.json",
    gold_file="data.gold.txt",
    tables_file="tables.json",
    db_dir="../database"
)

SPIDER_ALL = DatasetConfig(
    dataset_dir="data/spider/all",
    data_file="data.json",
    gold_file="data.gold.txt",
    tables_file="tables.json",
    db_dir="../database"
)

BEAVER_DEV = DatasetConfig(
    dataset_dir="data/beaver",
    data_file="non_dw.dev.conv.json",
    gold_file="non_dw.dev.conv.gold.txt",
    tables_file="non_dw.tables.json",
    db_dir="database",
    mysql=True
)

BEAVER_SMALL = DatasetConfig(
    dataset_dir="data/beaver",
    data_file="non_dw.dev.conv.small.json",
    gold_file="non_dw.dev.conv.small.gold.txt",
    tables_file="tables.conv.json",
    db_dir="database",
    mysql=True
)

DATASETS = {
    "bird": {
        "small": BIRD_SMALL,
        "dev": BIRD_DEV,
        "train": BIRD_TRAIN
    },
    "spider": {
        "small": SPIDER_SMALL,
        "dev": SPIDER_DEV,
        "test": SPIDER_TEST,
        "train": SPIDER_TRAIN,
        "all": SPIDER_ALL
    },
    "beaver": {
        "small": BEAVER_SMALL
    }
}

DatasetName = Literal["spider", "bird", "beaver"]
DatasetSize = Literal["small", "dev", "train", "test", "all"]
