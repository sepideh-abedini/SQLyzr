import os
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures.process import ProcessPoolExecutor
from typing import Callable, TypeVar, List
from multiprocessing import Pool

from loguru import logger
from torchgen.gen_functionalization_type import return_str
from tqdm import tqdm

from src.util.log_util import configure_logging

NUM_THREADS = int(os.environ.get("NUM_THREADS", 1))
NUM_PROC_CHUNKS = int(os.environ.get("NUM_PROC_CHUNKS"), 1)

logger.info(f"NUM_THREADS={NUM_THREADS}")

TMP_DIR = "./tmp"

try:
    shutil.rmtree(TMP_DIR, ignore_errors=True)
    if not os.path.exists(TMP_DIR):
        os.mkdir(TMP_DIR)
except Exception:
    pass


def flatten(lst):
    flat = [item for sublist in lst for item in sublist]
    return flat


def chunk_list(lst, k):
    size = len(lst) // k + (len(lst) % k > 0)
    return [lst[i:i + size] for i in range(0, len(lst), size)]


def get_thread_pool(num_threads: int = NUM_THREADS):
    return ThreadPoolExecutor(max_workers=num_threads)


T = TypeVar('T')
U = TypeVar('U')


def process_initializer():
    configure_logging()


def exec_multi_process(fun: Callable[[List[T]], List[U]], vals: List[T], num_procs: int = NUM_PROC_CHUNKS):
    chunks = chunk_list(vals, num_procs)
    with Pool(num_procs, initializer=process_initializer) as pool:
        result_chunks = list(pool.map(fun, chunks))
    results = flatten(result_chunks)
    return results


def exec_multi_process_flat(fun: Callable[[List[T]], List[U]], vals: List[T], num_procs: int):
    results = []
    with Pool(num_procs, initializer=process_initializer) as p, tqdm(total=len(vals)) as pbar:
        for result in p.imap(fun, vals):
            pbar.update()
            pbar.refresh()
            results.append(result)
    return results


def exec_multi_thread(fun: Callable[[List[T]], List[U]], vals: List[T], num_threads: int = NUM_THREADS):
    chunks = chunk_list(vals, num_threads)
    with get_thread_pool(num_threads) as executor:
        result_chunks = list(executor.map(fun, chunks))
    results = flatten(result_chunks)
    return results


def exec_multi_thread_flat(fun: Callable[[T], U], vals: List[T], num_threads: int = NUM_THREADS) -> List[U]:
    with get_thread_pool(num_threads) as executor:
        results = list(executor.map(fun, vals))
    return results


def write_thread_log(msg):
    with open(f"tmp/thread_{threading.get_ident()}.log", 'a') as file:
        file.write(msg)
