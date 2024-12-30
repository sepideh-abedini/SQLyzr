import json

from pandas import DataFrame, read_csv


def load_json(in_path: str) -> DataFrame:
    with open(in_path) as in_file:
        data = json.load(in_file)
    return DataFrame(data)


def load_csv(in_path: str) -> DataFrame:
    return read_csv(in_path)


def save_csv(data: DataFrame, out_path: str):
    df = DataFrame(data)
    df.to_csv(out_path, header=True, index=False)
