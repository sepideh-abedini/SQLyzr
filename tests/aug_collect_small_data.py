import asyncio
import os
import shutil
from random import shuffle

import tqdm
from dotenv import load_dotenv
from loguru import logger

from src.cat.catter import Catter
from src.eval.dataset_config import DatasetConfig
from src.util.file_utils import read_json, write_json

load_dotenv()
from src.configs.datasets import AUG_SMALL, SPIDER_SMALL

# skip_dbs = ['bike_1', "student_assessment", "flight_1", "journal_committee", "department_management", "store_1",
#             "chinook_1", "insurance_fnol", "medicine_enzyme_interaction"]

include_dbs = ["book_2", "allergy_1", "phone_1", "twitter_1", "race_track", "twitter_1", "university_basketball",
               "product_catalog", "match_season"]


def extract_cats(data_file):
    catter = Catter()
    data = read_json(data_file)
    for item in tqdm.tqdm(data, total=len(data)):
        sql = item['query']
        if "cat" in item and "sub" in item:
            continue
        cat = catter.get_category(sql)
        sub = catter.get_sub_category(sql)
        item['cat'] = cat.name
        item['sub'] = sub.name
    write_json(data_file, data)


async def collect_small_data(ds: DatasetConfig):
    small_test_path = ds.get_test_path()
    all_test_path = small_test_path.replace(".small.v0", "")
    ref_path = small_test_path.replace(".small.v0", ".ref")
    ref_data = read_json(ref_path)
    goods = list(filter(lambda x: x['sub'] == "s8", ref_data))
    all_data = read_json(all_test_path)
    sub_counts = {
        # "s8": 5,
        "s4": 15
    }
    collect_data = goods

    current_counts = {sub: 0 for sub in sub_counts}
    shuffle(all_data)
    for row in all_data:
        if row['db_id'] not in include_dbs:
            continue

        sub = row["sub"]
        if sub in sub_counts and current_counts[sub] < sub_counts[sub]:
            collect_data.append(row)
            current_counts[sub] += 1

        if all(current_counts[s] >= sub_counts[s] for s in sub_counts):
            break

    logger.info(f"New counts: {current_counts}")
    logger.info(f"Saving to: {ds.get_test_path()}")
    write_json(ds.get_test_path(), collect_data)
    gold_path = ds.get_test_path().replace(".v0.json", ".gold.v0.txt")
    pick_db_ids = set()
    with open(gold_path, "w") as f:
        for row in collect_data:
            f.write(f"{row['query']}\t{row['db_id']}\n")
            pick_db_ids.add(row['db_id'])
    logger.info(f"Data written to: {ds.get_test_path()}")
    logger.info(f"Gold written to: {gold_path}")
    logger.info(f"DBs: {set(map(lambda x: x['db_id'], collect_data))}")
    logger.info(f"Data size: {len(collect_data)}")
    tables = read_json(ds.get_tables_path().replace(".small", ""))
    pick_tables = dict()
    for table in tables:
        if table['db_id'] in pick_db_ids:
            pick_tables[table['db_id']] = table

    write_json(ds.get_tables_path(), list(pick_tables.values()))
    shutil.rmtree(ds.get_db_path() + "_small")
    os.makedirs(ds.get_db_path() + "_small", exist_ok=True)
    for db_id in pick_db_ids:
        shutil.copytree(os.path.join(ds.get_db_path(), db_id), os.path.join(f"{ds.get_db_path()}_small", db_id))


async def main():
    ds = SPIDER_SMALL
    await collect_small_data(ds)
    # extract_cats(ds.get_test_path())
    # extract_cats(ds.get_train_path())


if __name__ == '__main__':
    asyncio.run(main())
