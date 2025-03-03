import json
from typing import Iterable


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
