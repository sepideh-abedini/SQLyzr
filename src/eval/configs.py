from src.eval.model_eval_config import ModelEvalConfig
from src.eval.dataset_config import DatasetConfig

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

EVAL_CONF = ModelEvalConfig(
    temps=[0.0, 0.2, 0.4, 0.7, 1.0],
    num_itrs=4,
    pred_dir="data/dum",
    eval_dir="data/eval",
    dataset_config=SPIDER_SMALL
)

SMALL_EVAL_CONF = ModelEvalConfig(
    temps=[0.0],
    num_itrs=1,
    pred_dir="data/dum",
    eval_dir="data/eval",
    dataset_config=SPIDER_SMALL
)

DIN_SMALL_CONF = ModelEvalConfig(
    temps=[0.0],
    num_itrs=3,
    pred_dir="data/din",
    eval_dir="data/eval",
    dataset_config=SPIDER_SMALL
)
