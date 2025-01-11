from src.eval.metrics import ExactMatch, ExecAcc, GoldNotEmpty

SPIDER_METRICS = {
    "em": ExactMatch,
    "ea": ExecAcc,
    "gne": GoldNotEmpty
    # TotalExecTime("et", config.dataset_config),
    # SpiderExactMatch("sem", config.dataset_config),
    # RelaxedExecAcc("rea", config.dataset_config),
}

BIRD_METRICS = {
    "em": ExactMatch,
    "ea": ExecAcc,
    # TotalExecTime("et", config.dataset_config),
    # SpiderExactMatch("sem", config.dataset_config),
    # RelaxedExecAcc("rea", config.dataset_config),
}

METRICS = {
    "spider": SPIDER_METRICS,
    "bird": BIRD_METRICS
}
