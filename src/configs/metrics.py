from src.eval.metrics import ExactMatch, ExecAcc, GoldNotEmpty, TotalExecTime, RelaxedExecAcc, SpiderExactMatch, \
    ComplexityConsistency

SPIDER_METRICS = {
    "em": ExactMatch,
    "ea": ExecAcc,
    "gne": GoldNotEmpty,
    "rea": RelaxedExecAcc,
    "et": TotalExecTime,
    "sem": SpiderExactMatch,
    "cc": ComplexityConsistency
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
METRICS = {
    "spider": SPIDER_METRICS,
    "bird": BIRD_METRICS,
    "beaver": BIRD_METRICS
}
