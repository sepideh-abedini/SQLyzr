from src.configs.datasets import SPIDER_ALL
from src.eval.metrics import SpiderExactMatch, ExactMatch
from src.util.log_util import configure_logging

SEM = SpiderExactMatch("sem", SPIDER_ALL)
EM = ExactMatch("em", SPIDER_ALL)


def check_if_sem_em_good(db_id, gold, pred):
    sem = SEM.calc(gold, pred, db_id)
    em = EM.calc(gold, pred, db_id)
    if em != sem:
        print(f"""
            \rSEM = {sem}
            \rEM = {em}
            \rdb_id = "{db_id}"
            \rgold = "{gold}"
            \rpred = "{pred}"
        """)
    return sem, em


configure_logging()

db_id = 'concert_singer'
gold = "SELECT name ,  country ,  age FROM singer ORDER BY age DESC"
pred = "select Age,Name,Country from singer order by Age desc"
res = check_if_sem_em_good(db_id, gold, pred)
print(res)
exit(0)
