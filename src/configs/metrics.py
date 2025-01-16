from src.eval.metrics import ExactMatch, ExecAcc, GoldNotEmpty, TotalExecTime, RelaxedExecAcc, SpiderExactMatch

SPIDER_METRICS = {
    "em": ExactMatch,
    "ea": ExecAcc,
    "gne": GoldNotEmpty,
    "rea": RelaxedExecAcc,
    "et": TotalExecTime,
    "sem": SpiderExactMatch
    # "et": TotalExecTime
    # TotalExecTime("et", config.dataset_config),
    # SpiderExactMatch("sem", config.dataset_config),
    # RelaxedExecAcc("rea", config.dataset_config),
}

BIRD_METRICS = {
    "em": ExactMatch,
    "ea": ExecAcc,
    "rea": RelaxedExecAcc,
    "et": TotalExecTime
    # TotalExecTime("et", config.dataset_config),
    # SpiderExactMatch("sem", config.dataset_config),
    # RelaxedExecAcc("rea", config.dataset_config),
}
