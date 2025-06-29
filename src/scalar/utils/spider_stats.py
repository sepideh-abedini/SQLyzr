from src.util.file_utils import read_json

data = read_json("data/spider/data.test.json")


db_ids = set(map(lambda r: r['db_id'], data))

print(len(db_ids))
