from src.eval.dataset_config import DatasetConfig

BIRD_SMALL = DatasetConfig(
    dataset_dir="data/bird",
    data_file="dev.conv.small.json",
    gold_file="dev.conv.small.gold.txt",
    tables_file="dev_tables.json",
    db_dir="dev_databases"
)

BIRD_DEV = DatasetConfig(
    dataset_dir="data/bird",
    data_file="dev.conv.json",
    gold_file="dev.gold.txt",
    tables_file="dev_tables.json",
    db_dir="dev_databases"
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
