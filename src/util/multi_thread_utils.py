import os
import threading
from multiprocessing import Pool
from typing import Callable, TypeVar, List

from loguru import logger
from tqdm import tqdm

from src.util.log_util import configure_logging

NUM_PROCS = int(os.environ.get("NUM_PROCS", 1))
NUM_PROC_CHUNKS = int(os.environ.get("NUM_PROC_CHUNKS", 1))


def flatten(lst):
    flat = [item for sublist in lst for item in sublist]
    return flat


T = TypeVar('T')
U = TypeVar('U')


def chunk_list(lst: List[T], k: int) -> List[List[T]]:
    size = len(lst) // k + (len(lst) % k > 0)
    return [lst[i:i + size] for i in range(0, len(lst), size)]


def process_initializer():
    configure_logging()
    logger.info(f"Started new process: {os.getpid()}")


def exec_multi_process(fun: Callable[[T], U], vals: List[T], num_procs: int = NUM_PROCS, desc: str = "") -> List[U]:
    if num_procs < 2:
        return __exec_with_map(fun, vals, desc)
    else:
        return __exec_multi_process(fun, vals, num_procs, desc)


def exec_multi_process_chunked(fun: Callable[[List[T]], List[U]], vals: List[T], num_procs: int = NUM_PROC_CHUNKS,
                               desc: str = "") -> List[U]:
    if num_procs < 2:
        return __exec_with_map_chunked(fun, vals, desc)
    else:
        return __exec_multi_process_chunked(fun, vals, num_procs, desc)


def __exec_with_map(fun: Callable[[T], U], vals: List[T], desc: str = "") -> List[U]:
    return list(tqdm(map(fun, vals), total=len(vals), desc=desc))


def __exec_with_map_chunked(fun: Callable[[List[T]], List[U]], vals: List[T], desc: str = "") -> List[U]:
    return fun(vals)
    # return list(tqdm(map(fun, vals), total=len(vals), desc=desc))


def __exec_multi_process_chunked(fun: Callable[[List[T]], List[U]], vals: List[T], num_procs: int = NUM_PROC_CHUNKS,
                                 desc: str = "") -> List[U]:
    chunks = chunk_list(vals, num_procs)
    with Pool(num_procs, initializer=process_initializer) as pool:
        result_chunks = list(pool.map(fun, chunks))
    results = flatten(result_chunks)
    return results


def __exec_multi_process(fun: Callable[[T], U], vals: List[T], num_procs: int = NUM_PROCS, desc: str = "") -> List[U]:
    results = []
    with Pool(num_procs, initializer=process_initializer) as p, tqdm(total=len(vals), desc=desc) as pbar:
        for result in p.imap(fun, vals):
            pbar.update()
            pbar.refresh()
            results.append(result)
    return results


def write_thread_log(msg):
    with open(f"tmp/thread_{threading.get_ident()}.log", 'a') as file:
        file.write(msg)
