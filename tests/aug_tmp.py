import asyncio

import tqdm
from dotenv import load_dotenv

from src.cat.catter import Catter
from src.eval.dataset_config import DatasetConfig
from src.util.file_utils import read_json, write_json

load_dotenv()
from src.configs.datasets import SPIDER_ALL, SPIDER_ALL_CAT


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


async def main():
    ds = SPIDER_ALL_CAT
    extract_cats(ds.get_test_path())
    extract_cats(ds.get_train_path())
    # conf = load_config("tests/aug.json")

    # sub_cat = find_sub("s8")
    # auger = Auger(conf, ds_conf, [sub_cat])
    # await auger.run()
    # aug_data = conf.get_aug_out()
    # prompt = auger.get_prompt_for_sub_cat(sub_cat)


if __name__ == '__main__':
    asyncio.run(main())
