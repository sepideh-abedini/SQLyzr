import asyncio
import os
import shutil

import tqdm
from dotenv import load_dotenv

load_dotenv()

from src.configs.config_loader import load_config, ConfigData
from src.sqlyzr.augment_data import DatasetAugmentor
from src.util.log_util import configure_logging

from src.cat.catter import Catter
from src.sqlyzr.sqlyzr import Sqlyzr
from src.util.file_utils import read_json, write_json

from src.configs.datasets import AUG_ALL


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
    configure_logging()
    conf_path = "tests/aug.json"
    sqlyzr = Sqlyzr(conf_path)
    await sqlyzr.run()

    augmentor = DatasetAugmentor(sqlyzr.conf)
    conf_data = ConfigData.load(conf_path)
    new_ver = await augmentor.augment_data(expand=True)
    conf_data.dataset_versions.append(new_ver)
    shutil.copy(conf_path, f"{conf_path}.bak")
    conf_data.save(conf_path)
    # for ds_conf in conf.eval_conf.dataset_configs:
    #     conf.get_aug_out(ds_type)
    #     auger = Auger(conf, ds, [sub_cat], force=True)
    #     await auger.run()
    #     aug_data = read_jsonl(conf.get_aug_out(ds_type))
    # print(aug_data)

    # extract_cats(ds.get_train_path())

    # for ds_type in conf.eval_conf.datasets:
    #     conf.get_aug_out(ds_type)
    #     sub_cat = find_sub("s8")
    #     auger = Auger(conf, ds, [sub_cat], force=True)
    #     await auger.run()
    #     aug_data = read_jsonl(conf.get_aug_out(ds_type))
    # print(aug_data)


if __name__ == '__main__':
    asyncio.run(main())
