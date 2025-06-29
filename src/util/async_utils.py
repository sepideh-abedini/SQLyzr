import asyncio
import os

from tqdm.asyncio import tqdm_asyncio
from tqdm import tqdm

ASYNC_BATCH = int(os.environ.get("ASYNC_BATCH", 1))


async def apply_async(fun, items, desc=""):
    semaphore = asyncio.Semaphore(ASYNC_BATCH)
    progress = tqdm(total=len(items), desc=desc)

    async def sem_task(item):
        async with semaphore:
            result = await fun(item)
            progress.update(1)
            return result

    tasks = [asyncio.create_task(sem_task(item)) for item in items]
    results = await tqdm_asyncio.gather(*tasks, total=len(items), desc=desc)
    progress.close()
    return results
