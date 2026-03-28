import os.path
import shutil

from src.util.file_utils import read_json, read_json_to_dict, write_json

test_data = read_json("sample_data/spider/data.test.small.v0.json")

train_data = read_json("sample_data/spider/data.train.json")

subs = set(map(lambda r: r['sub'], test_data))

tables = read_json_to_dict("sample_data/spider/tables.all.json", "db_id")
pick_rows = []
pick_dbs = set()
for row in train_data:
    sub = row["sub"]
    if sub in subs:
        pick_rows.append(row)
        pick_dbs.add(row['db_id'])

for row in test_data:
    pick_dbs.add(row['db_id'])


pick_tables = []
for db_id in pick_dbs:
    pick_tables.append(tables[db_id])
    if not os.path.exists("sample_data/spider/database/" + db_id):
        shutil.copytree("data/spider/database/" + db_id, "sample_data/spider/database/" + db_id)

write_json("sample_data/spider/tables.small.json", pick_tables)
write_json("sample_data/spider/data.train.small.json", pick_rows)

print(len(pick_tables))
print(len(pick_rows))

