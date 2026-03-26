from src.eval.metrics import ExactMatch, ExecAcc, GoldNotEmpty, ExecTime, RelaxedExecAcc, SpiderExactMatch, \
    GoldExecTime

SPIDER_METRICS = {
    "em": ExactMatch,
    "ea": ExecAcc,
    "gne": GoldNotEmpty,
    "rea": RelaxedExecAcc,
    "et": ExecTime,
    "get": GoldExecTime,
    "sem": SpiderExactMatch,
}

BIRD_METRICS = {
    "em": ExactMatch,
    "ea": ExecAcc,
    "rea": RelaxedExecAcc,
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
