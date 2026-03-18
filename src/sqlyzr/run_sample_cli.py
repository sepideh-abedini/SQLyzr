import argparse
import asyncio
import os.path
from random import shuffle

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

from src.cat.catter import Catter
from src.configs.config_loader import load_config
from src.eval.dataset_config import DatasetConfig
from src.util.file_utils import read_json, write_json, get_dir_size


def assign_cats(rows):
    catter = Catter()
    new_rows = []
    for row in rows:
        sql = row['query']
        cat = catter.get_category(sql)
        sub = catter.get_sub_category(sql)
        row['cat'] = cat.name
        row['sub'] = sub.name
        new_rows.append(row)
    return new_rows


import re


def replace_small_json(path: str) -> str:
    return re.sub(r'\.small.*\.json$', '.json', path)


def sample_data(conf, small_data_path, num_dbs, data_per_db):
    all_test_path = replace_small_json(small_data_path)
    all_data = read_json(all_test_path)
    collect_data = dict()
    for row in all_data:
        db_id = row['db_id']
        collect_data.setdefault(db_id, []).append(row)

    pick_dbs = set()
    candidate_dbs = list(collect_data.keys())
    shuffle(candidate_dbs)
    for db_id in candidate_dbs:
        if len(collect_data[db_id]) >= data_per_db:
            db_size = os.path.getsize(conf.get_db_file_path(db_id)) / (1024 * 1024)
            logger.info(f"DB Size {db_id}: {db_size:.2f} MB")
            if db_size > 50:
                continue
            pick_dbs.add(db_id)
        if len(pick_dbs) >= num_dbs:
            break

    rows = []
    for db_id in pick_dbs:
        rows.extend(collect_data[db_id][:data_per_db])

    rows = assign_cats(rows)
    write_json(small_data_path, rows)
    logger.info(f"{small_data_path} -> {len(rows)}")

    if ".v0" in small_data_path:
        gold_path = small_data_path.replace(".v0.json", ".gold.v0.txt")
    else:
        gold_path = small_data_path.replace(".json", ".gold.txt")
    with open(gold_path, "w") as f:
        for row in rows:
            f.write(f"{row['query']}\t{row['db_id']}\n")
    return pick_dbs


async def collect_small_data(ds: DatasetConfig, num_dbs: int, data_per_db: int):
    test_dbs = sample_data(ds, ds.get_test_path(), num_dbs, data_per_db)
    train_dbs = sample_data(ds, ds.get_train_path(), num_dbs, data_per_db)
    all_dbs = test_dbs.union(train_dbs)
    pick_tables = dict()
    tables = read_json(ds.get_tables_path().replace(".small", ""))
    for table in tables:
        if table['db_id'] in all_dbs:
            pick_tables[table['db_id']] = table
    logger.info(f"DBs: {pick_tables.keys()}")
    write_json(ds.get_tables_path(), list(pick_tables.values()))


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to the config file")
    parser.add_argument("--dbs", type=int, required=True, help="Num of dbs")
    parser.add_argument("--samples", type=int, required=True, help="Samples per db")
    args = parser.parse_args()
    conf = load_config(args.config)
    ds_conf = conf.eval_conf.dataset_configs[0]
    await collect_small_data(ds_conf, args.dbs, args.samples)
    # extract_cats(ds.get_train_path())


if __name__ == '__main__':
    asyncio.run(main())
