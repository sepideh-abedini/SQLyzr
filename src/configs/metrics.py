from src.eval.metrics import ExactMatch, ExecAcc, GoldNotEmpty, ExecTime, RelaxedExecAcc, SpiderExactMatch, \
    ComplexityConsistency, GoldExecTime

SPIDER_METRICS = {
    "em": ExactMatch,
    "ea": ExecAcc,
    "gne": GoldNotEmpty,
    "rea": RelaxedExecAcc,
    "et": ExecTime,
    "get": GoldExecTime,
    "sem": SpiderExactMatch,
    "cc": ComplexityConsistency,
}

BIRD_METRICS = {
    "em": ExactMatch,
    "ea": ExecAcc,
    "rea": RelaxedExecAcc,
    "et": ExecTime,
    "cc": ComplexityConsistency,
    "get": GoldExecTime,
}
METRICS = {
    "spider": SPIDER_METRICS,
    "bird": BIRD_METRICS,
    "beaver": BIRD_METRICS,
    "agg": BIRD_METRICS
}
