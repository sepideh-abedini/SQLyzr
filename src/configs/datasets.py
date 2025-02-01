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
    dataset_dir="data/spider",
    data_file="dev.small.json",
    gold_file="dev.small.gold.txt",
    tables_file="tables.json",
    db_dir="database"
)

SPIDER_DEV = DatasetConfig(
    dataset_dir="data/spider",
    data_file="dev.json",
    gold_file="dev.gold.txt",
    tables_file="tables.json",
    db_dir="database"
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
        "dev": SPIDER_DEV
    },
    "beaver": {
        "small": BEAVER_SMALL
    }
}


DatasetName = Literal["spider", "bird", "beaver"]
DatasetSize = Literal["small", "dev", "train", "all"]
