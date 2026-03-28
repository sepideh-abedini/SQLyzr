import os.path

from src.cat.catter import Catter
from src.configs.datasets import SPIDER_ALL, BIRD_ALL, BEAVER_ALL
from src.util.file_utils import read_json, write_json

test_data = []
train_data = []

tables = []

catter = Catter()

for ds in [SPIDER_ALL, BIRD_ALL, BEAVER_ALL]:
    test = read_json(ds.get_test_path())
    test_data.extend(test)

    tab_data = read_json(ds.get_tables_path())
    tables.extend(tab_data)

    train = read_json(ds.get_train_path())
    train_data.extend(train)

for row in test_data:
    sql = row['query']
    cat = catter.get_category(sql)
    sub = catter.get_sub_category(sql)
    row['cat'] = cat.name
    row['sub'] = sub.name

out_dir = "data/agg"

write_json(os.path.join(out_dir, "data.test.json"), test_data)
write_json(os.path.join(out_dir, "data.train.json"), train_data)
write_json(os.path.join(out_dir, "tables.json"), tables)
with open(os.path.join(out_dir, "data.test.gold.txt"), "w") as f:
    for row in test_data:
        f.write(f"{row['query']}\t{row['db_id']}\n")
