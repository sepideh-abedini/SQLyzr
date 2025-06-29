from src.cat.catter import Catter
from src.configs.datasets import SPIDER_SMALL
from src.eval.lib import Timer
from src.eval.metrics import ExactMatch, SpiderExactMatch, RelaxedExecAcc, ExecAcc, NewRelaxedExecAcc
from src.util.log_util import configure_logging

configure_logging()

conf = SPIDER_SMALL

# em = ExactMatch("bar", conf)
# em = SpiderExactMatch("bar", conf)
# m = RelaxedExecAcc("rea", conf)
e = ExecAcc("ea", conf)
m = NewRelaxedExecAcc("rea", conf)

q1 = "SELECT name, age FROM singer ORDER BY age DESC "

q2 = "SELECT age, name FROM singer"

timer = Timer.start()
print(e.calc(q1, q2, "concert_singer"))
print(m.calc(q1, q2, "concert_singer"))
print(timer.lap())
