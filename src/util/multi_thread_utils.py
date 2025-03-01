import os
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor
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


def chunk_list(lst, k):
    size = len(lst) // k + (len(lst) % k > 0)
    return [lst[i:i + size] for i in range(0, len(lst), size)]


T = TypeVar('T')
U = TypeVar('U')


def process_initializer():
    configure_logging()
    logger.info(f"Started new process: {os.getpid()}")


def exec_multi_process(fun: Callable[[List[T]], List[U]], vals: List[T], num_procs: int = NUM_PROC_CHUNKS,
                       desc: str = ""):
    chunks = chunk_list(vals, num_procs)
    with Pool(num_procs, initializer=process_initializer) as pool:
        result_chunks = list(pool.map(fun, chunks))
    results = flatten(result_chunks)
    return results


def exec_multi_process_flat(fun: Callable[[T], List[U]], vals: List[T], num_procs: int = NUM_PROCS, desc: str = ""):
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
