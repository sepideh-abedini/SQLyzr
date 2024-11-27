import os
import time
from math import floor


def wait_for_file(file_path: str, timeout=5):
    while timeout > 0:
        time.sleep(1)
        if os.path.exists(file_path):
            return
        timeout -= 1
    raise TimeoutError(f"{file_path} not created!")


def get_chunks(total_len: int, num_chunks: int):
    chunk_size = floor(total_len / num_chunks)
    rem = total_len % num_chunks
    return [chunk_size + (1 if i < rem else 0) for i in range(num_chunks)]


def get_num_lines(file_path: str):
    with open(file_path) as f:
        return len(f.readlines())
