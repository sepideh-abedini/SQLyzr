from typing import Literal

from src.eval.dataset_config import DatasetConfig

SPIDER_SMALL = DatasetConfig(
    dataset_dir="data/spider_data",
    test_file="data.test.small.json",
    gold_file="data.test.small.gold.txt",
    train_file="data.train.small.json",
    tables_file="tables.all.json",
    db_dir="database"
)

SPIDER_ALL = DatasetConfig(
    dataset_dir="data/spider_data",
    test_file="data.test.json",
    gold_file="data.test.gold.txt",
    train_file="data.train.json",
    tables_file="tables.all.json",
    db_dir="database"
)

# BIRD_SMALL = DatasetConfig(
#     dataset_dir="data/bird/small",
#     test_file="data.json",
#     gold_file="data.gold.txt",
#     tables_file="tables.json",
#     db_dir="../database",
#     dataset_type="bird"
# )
#
# BIRD_ALL = DatasetConfig(
#     dataset_dir="data/bird/all",
#     test_file="data.json",
#     gold_file="data.gold.txt",
#     tables_file="tables.json",
#     db_dir="../database",
#     dataset_type="bird"
# )

# BEAVER_DEV = DatasetConfig(
#     dataset_dir="data/beaver",
#     test_file="non_dw.dev.conv.json",
#     gold_file="non_dw.dev.conv.gold.txt",
#     tables_file="non_dw.tables.json",
#     db_dir="database",
#     mysql=True
# )
#
# BEAVER_SMALL = DatasetConfig(
#     dataset_dir="data/beaver",
#     test_file="non_dw.dev.conv.small.json",
#     gold_file="non_dw.dev.conv.small.gold.txt",
#     tables_file="tables.conv.json",
#     db_dir="database",
#     mysql=True
# )

DATASETS = {
    # "bird": {
    #     "small": BIRD_SMALL,
    #     "dev": BIRD_DEV,
    #     "train": BIRD_TRAIN
    # },
    "spider": {
        "small": SPIDER_SMALL,
        # "dev": SPIDER_DEV,
        # "test": SPIDER_TEST,
        # "train": SPIDER_TRAIN,
        "all": SPIDER_ALL
    },
    # "beaver": {
    #     "small": BEAVER_SMALL
    # }
}

DatasetName = Literal["spider", "bird", "beaver"]
DatasetSize = Literal["small", "dev", "train", "test", "all"]
