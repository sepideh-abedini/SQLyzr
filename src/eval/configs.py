from src.eval.model_eval_config import ModelEvalConfig
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

DIN_SPIDER_SMALL_EVAL = ModelEvalConfig(
    temps=[0.0],
    num_itrs=3,
    pred_dir="data/din",
    eval_dir="data/ev",
    dataset_config=SPIDER_SMALL
)

DAIL_SPIDER_SMALL_EVAL = ModelEvalConfig(
    temps=[0.0],
    num_itrs=3,
    pred_dir="data/dail",
    eval_dir="data/ev",
    dataset_config=SPIDER_SMALL
)

DIN_BIRD_SMALL_EVAL = ModelEvalConfig(
    temps=[0.0],
    num_itrs=3,
    pred_dir="data/din",
    eval_dir="data/ev",
    dataset_config=BIRD_SMALL
)
