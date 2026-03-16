import asyncio

import tqdm
from dotenv import load_dotenv
from loguru import logger

from src.cat.catter import Catter
from src.eval.dataset_config import DatasetConfig
from src.util.file_utils import read_json, write_json

load_dotenv()
from src.configs.datasets import AUG_SMALL


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
    all_test_path = small_test_path.replace(".small", "")
    all_data = read_json(all_test_path)
    sub_counts = {
        "s8": 10,
        "s4": 40
    }
    collect_data = []

    current_counts = {sub: 0 for sub in sub_counts}
    for row in all_data:
        sub = row["sub"]
        if sub in sub_counts and current_counts[sub] < sub_counts[sub]:
            collect_data.append(row)
            current_counts[sub] += 1

        if all(current_counts[s] >= sub_counts[s] for s in sub_counts):
            break

    logger.info(f"New counts: {current_counts}")
    logger.info(f"Saving to: {ds.get_test_path()}")
    write_json(ds.get_test_path(), collect_data)
    gold_path = ds.get_test_path().replace(".json", ".gold.txt")
    with open(gold_path, "w") as f:
        for row in collect_data:
            f.write(f"{row['query']}\t{row['db_id']}\n")
    logger.info(f"Data size: {len(collect_data)}")


async def main():
    ds = AUG_SMALL
    await collect_small_data(ds)
    # extract_cats(ds.get_test_path())
    # extract_cats(ds.get_train_path())


if __name__ == '__main__':
    asyncio.run(main())
