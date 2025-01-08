from src.configs.dataset import SPIDER_SMALL, BIRD_SMALL, SPIDER_DEV, BIRD_DEV
from src.eval.metrics import ExactMatch, Count, ExecAcc
from src.eval.model_eval_config import ModelEvalConfig

SPIDER_METRICS = {
    "em": ExactMatch,
    "ea": ExecAcc,
    # TotalExecTime("et", config.dataset_config),
    # SpiderExactMatch("sem", config.dataset_config),
    # RelaxedExecAcc("rea", config.dataset_config),
}

DIN_SPIDER_SMALL_EVAL = ModelEvalConfig(
    temps=[0.0],
    num_itrs=3,
    pred_dir="data/small_din",
    eval_dir="data/ev",
    dataset_config=SPIDER_SMALL,
    metrics=SPIDER_METRICS
)

DIN_SPIDER_DEV_EVAL = ModelEvalConfig(
    temps=[0.2],
    # temps=[0.0, 0.7, 1.0],
    # num_itrs=3,
    num_itrs=2,
    pred_dir="data/din",
    eval_dir="data/ev",
    dataset_config=SPIDER_DEV,
    metrics=SPIDER_METRICS
)

DAIL_SPIDER_SMALL_EVAL = ModelEvalConfig(
    temps=[0.0],
    num_itrs=3,
    pred_dir="data/dail",
    eval_dir="data/ev",
    dataset_config=SPIDER_SMALL,
    metrics=SPIDER_METRICS
)

DAIL_SPIDER_DEV_EVAL = ModelEvalConfig(
    temps=[0.0],
    num_itrs=3,
    pred_dir="data/dail",
    eval_dir="data/ev",
    dataset_config=SPIDER_DEV,
    metrics=SPIDER_METRICS
)

DIN_BIRD_SMALL_EVAL = ModelEvalConfig(
    temps=[0.0],
    num_itrs=3,
    pred_dir="data/din",
    eval_dir="data/ev",
    dataset_config=BIRD_SMALL,
    metrics=SPIDER_METRICS
)

DIN_BIRD_DEV_EVAL = ModelEvalConfig(
    temps=[0.0],
    num_itrs=3,
    pred_dir="data/din",
    eval_dir="data/ev",
    dataset_config=BIRD_DEV,
    metrics=SPIDER_METRICS
)
