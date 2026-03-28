import asyncio
import os
import sys
import time
from typing import List, Optional

import numpy as np

from src.configs.datasets import SPIDER_ALL, SPIDER_SMALL, BIRD_SMALL, BEAVER_SMALL
from src.eval.dataset_config import DatasetConfig
from src.eval.lib import Timer
from src.db.db_factory import DatabaseFactory
from src.util.async_utils import apply_async
from src.util.file_utils import read_json
from src.util.log_util import configure_logging


async def run_query(conf: DatasetConfig, db_id: str, sql: str, k: int) -> List[float]:
    dbf = DatabaseFactory.get_instance(conf)

    async def _run_query(sql) -> Optional[float]:
        timer = Timer.start()
        res = dbf.exec_query_sync(db_id, sql)
        t = timer.lap()
        return t

    times = await apply_async(_run_query, [sql] * k)

    return times


async def calculate_R(confs: List[DatasetConfig], k: int, p: int):
    cvs = []
    for conf in confs:
        data = read_json(conf.get_test_path())
        for e in data:
            times = await run_query(conf, e['db_id'], e['query'], k)
            times = np.array(times, dtype=float)
            cv = times.std() / times.mean()
            cvs.append(cv)
    cvs = np.array(cvs, dtype=float)
    cvs += 1

    percentile = np.percentile(cvs, p)

    return round(percentile, 2)


if __name__ == "__main__":
    configure_logging()
    r = asyncio.run(calculate_R([SPIDER_SMALL], 100, 95))
    print(r)
