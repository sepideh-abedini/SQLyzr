from concurrent.futures import ThreadPoolExecutor
from typing import TypeVar, Callable, List, Any

from tqdm import tqdm

NUM_THREADS = 6
T = TypeVar('T')


def process_multi_thread(f: Callable[[T], Any], iter: List[T], desc=""):
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = list(
            tqdm(
                executor.map(f, iter),
                total=len(iter),
                desc=desc
            )
        )
    return futures
