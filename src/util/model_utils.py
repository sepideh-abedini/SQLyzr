import json
from typing import List, TypeVar, Type

from pydantic import BaseModel


def write_model(data: BaseModel, out_path: str):
    with open(out_path, 'w') as out_file:
        out_file.write(json.dumps(data.dict(), indent=4))


T = TypeVar('T', bound=BaseModel)


def read_model(in_path: str, model_class: Type[T]):
    with open(in_path) as in_file:
        res = model_class.model_validate_json(in_file.read())
        return res


def write_jsonl(data: list[BaseModel], out_path: str):
    with open(out_path, "w") as out_file:
        for entry in data:
            out_file.write(f"{entry.json()}\n")


def read_jsonl(in_path: str, model_class: Type[T] = None) -> List[T]:
    with open(in_path) as in_file:
        data = []
        for line in in_file.readlines():
            if model_class:
                res = model_class.model_validate_json(line)
            else:
                res = json.loads(line)
            data.append(res)
        return data
