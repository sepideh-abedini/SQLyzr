from src.eval.metrics import ExactMatch, ExecAcc, GoldNotEmpty, ExecTime, SpiderExactMatch, \
    GoldExecTime, NewRelaxedExecAcc

SPIDER_METRICS = {
    "em": ExactMatch,
    "ea": ExecAcc,
    "gne": GoldNotEmpty,
    "rea": NewRelaxedExecAcc,
    "et": ExecTime,
    "get": GoldExecTime,
    "sem": SpiderExactMatch,
}

BIRD_METRICS = {
    "em": ExactMatch,
    "ea": ExecAcc,
    "rea": NewRelaxedExecAcc,
    "et": ExecTime,
    "get": GoldExecTime,
}
METRICS = {
    "spider": SPIDER_METRICS,
    "aug": SPIDER_METRICS,
    "bird": BIRD_METRICS,
    "beaver": BIRD_METRICS,
    "aggregate": BIRD_METRICS,
    "custom": SPIDER_METRICS,
    "aligned": BIRD_METRICS,
    "sqlyzr": BIRD_METRICS
}
