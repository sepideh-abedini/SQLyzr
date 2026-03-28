from src.util.file_utils import read_json, write_json

all_tables = read_json("sample_data/spider/tables.all.json")
train_data = read_json("sample_data/spider/data.train.json")
test_data = read_json("sample_data/spider/data.test.small.v0.json")

db_ids = set(map(lambda x: x["db_id"], train_data))
db_ids_test = set(map(lambda x: x["db_id"], test_data))


pick_tables = []
for row in all_tables:
    if row["db_id"] in db_ids or row["db_id"] in db_ids_test:
        pick_tables.append(row)

write_json("sample_data/spider/tables.small.json", pick_tables)
