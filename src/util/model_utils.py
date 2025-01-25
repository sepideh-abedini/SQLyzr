import json
from typing import List, TypeVar, Type

from pydantic import BaseModel


def write_model(data: BaseModel, out_path: str):
    with open(out_path, 'w') as out_file:
        out_file.write(json.dumps(data.dict(), indent=4))


def write_jsonl(data: list[BaseModel], out_path: str):
    with open(out_path, "w") as out_file:
        for entry in data:
            out_file.write(f"{entry.json()}\n")


T = TypeVar('T', bound=BaseModel)


def read_jsonl(in_path: str, model_class: Type[T]) -> List[T]:
    with open(in_path) as in_file:
        data = []
        for line in in_file.readlines():
            res = model_class.model_validate_json(line)
            data.append(res)
        return data
