import os
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, TypeVar, List

from loguru import logger

NUM_THREADS = int(os.environ.get("NUM_THREADS", 1))

logger.info(f"NUM_THREADS={NUM_THREADS}")


def flatten(lst):
    flat = [item for sublist in lst for item in sublist]
    return flat


def chunk_list(lst, k):
    size = len(lst) // k + (len(lst) % k > 0)
    return [lst[i:i + size] for i in range(0, len(lst), size)]


def get_thread_pool():
    return ThreadPoolExecutor(max_workers=NUM_THREADS)


T = TypeVar('T')
U = TypeVar('U')


def exec_multi_thread(fun: Callable[[List[T]], List[U]], vals: List[T]):
    chunks = chunk_list(vals, NUM_THREADS)
    with get_thread_pool() as executor:
        result_chunks = list(executor.map(fun, chunks))
    results = flatten(result_chunks)
    return results
