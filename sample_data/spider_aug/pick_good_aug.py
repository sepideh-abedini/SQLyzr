from src.util.file_utils import read_json

data = read_json("data.test.small.v0.json")

for row in data:
    print(row)