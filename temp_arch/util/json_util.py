import json
from typing import List


def merge_jsons(paths: List[str], out: str):
    result = []
    for path in paths:
        file = open(path)
        data = json.load(file)
        result.extend(data)
        file.close()
    out_file = open(out, "w")
    out_file.write(json.dumps(result, indent=4))


def main():
    merge_jsons(["data/aug/gpt.c4.json", "data/aug/gpt.c6.json"], "data/aug/gpt.all.json")


if __name__ == '__main__':
    main()
