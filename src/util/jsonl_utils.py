from typing import Literal

from pydantic import BaseModel, PositiveInt, Field



def read_jsonl(path):
    file = open(path)
    for line in file.readlines():
        person = GptMessage.model_validate_json(line)
        print(person)


def main():
    read_jsonl("data/din/classif.in.jsonl")


if __name__ == '__main__':
    main()
