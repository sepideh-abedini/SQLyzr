from src.configs.dataset import SPIDER_SMALL, BIRD_SMALL, SPIDER_DEV
from src.eval.model_eval_config import ModelEvalConfig

DIN_SPIDER_SMALL_EVAL = ModelEvalConfig(
    temps=[0.0],
    num_itrs=3,
    pred_dir="data/din",
    eval_dir="data/ev",
    dataset_config=SPIDER_SMALL
)

DIN_SPIDER_DEV_EVAL = ModelEvalConfig(
    temps=[0.0, 0.2, 0.5, 0.7, 1.0],
    num_itrs=5,
    pred_dir="data/din",
    eval_dir="data/ev",
    dataset_config=SPIDER_DEV
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
