import asyncio
import os
from loguru import logger

from tqdm.asyncio import tqdm_asyncio

ASYNC_BATCH = int(os.environ.get("ASYNC_BATCH", 10))

logger.info(f"ASYNC BATCH: {ASYNC_BATCH}")


async def apply_async(fun, items, desc=""):
    semaphore = asyncio.Semaphore(ASYNC_BATCH)

    async def sem_task(item):
        async with semaphore:
            res = await fun(item)
            # print("DONE!")
            return res

    tasks = [sem_task(item) for item in items]

    # tqdm_asyncio.gather handles the creation, update, and closing of the bar
    results = await tqdm_asyncio.gather(*tasks, desc=desc, total=len(items))

    return results
