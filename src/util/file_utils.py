import json
from typing import Iterable, List

from src.util.multi_thread_utils import chunk_list, NUM_PROC_CHUNKS


def read_json(path: str):
    with open(path) as f:
        return json.load(f)


def write_json(path: str, data):
    with open(path, "w") as f:
        f.write(json.dumps(data, indent=4))


def get_num_lines(file_path: str):
    with open(file_path) as f:
        return len(f.readlines())


def concat_files(files: Iterable[str], out_path: str):
    with open(out_path, 'w') as out_file:
        for file in files:
            with open(file, 'r') as in_file:
                out_file.write(in_file.read())
                # out_file.write("\n")


def concat_jsons(files: Iterable[str], out_path: str):
    data = []
    for file in files:
        with open(file, 'r') as in_file:
            in_data = json.load(in_file)
            data.extend(in_data)
    with open(out_path, 'w') as out_file:
        out_file.write(json.dumps(data, sort_keys=True, indent=4))


def chunk_jsonl(in_path: str) -> List[str]:
    with open(in_path) as in_file:
        in_lines = in_file.readlines()
    chunks = chunk_list(in_lines, NUM_PROC_CHUNKS)
    chunk_paths = []
    for i, chunk in enumerate(chunks):
        chunk_path = f"{in_path}.chunk_{i}.jsonl"
        with open(chunk_path, "w") as chunk_file:
            chunk_file.writelines(chunk)
        chunk_paths.append(chunk_path)
    return chunk_paths
