import asyncio
import os
from asyncio import Semaphore, get_running_loop

from tqdm.asyncio import tqdm

MAX_THREADS = os.getenv("MAX_THREADS", 32)


def partition_list(lst, size=MAX_THREADS):
    return [lst[i:i + size] for i in range(0, len(lst), size)]


async def apply_async(fun, l):
    semaphore = Semaphore(MAX_THREADS)

    async def worker(item):
        async with semaphore:
            return await fun(item)

    tasks = [worker(item) for item in l]
    return await tqdm.gather(*tasks)

# async def apply_async(fun, l):
#     parts = partition_list(l)
#     results = []
#     for part in parts:
#         res = await apply_async_chunk(fun, part)
#         results.extend(res)
#     return results
#
#
# async def apply_async_chunk(fun, l):
#     tasks = []
#     for e in l:
#         tasks.append(fun(e))
#
#     results = await tqdm.gather(*tasks)

# return results
