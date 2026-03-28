import json
import os
from typing import Iterable, List

from src.util.multi_thread_utils import chunk_list, NUM_PROC_CHUNKS

FORCE = bool(int(os.environ.get("FORCE", 0)))


def file_exists_not_forced(path: str):
    return os.path.exists(path) and not FORCE


def read_json(path: str):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Error reading JSON file: {path}") from e


def read_json_to_dict(path, key_field):
    data = read_json(path)
    return {item[key_field]: item for item in data}


def write_json(path: str, data):
    with open(path, "w") as f:
        f.write(json.dumps(data, indent=4))


def write_golds(input_path: str, output_path: str):
    data = read_json(input_path)
    with open(output_path, "w") as f:
        for row in data:
            db_id = row["db_id"]
            sql = row["query"]
            f.write(f"{sql}\t{db_id}\n")


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


def get_dir_size(folder):
    total_size = os.path.getsize(folder)
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += get_dir_size(itempath)
    return total_size
