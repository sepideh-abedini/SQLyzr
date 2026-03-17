import argparse
import asyncio
import os
import shutil

import pandas as pd
from dotenv import load_dotenv
from loguru import logger
from matplotlib import pyplot as plt
from natsort import natsorted
import seaborn as sns

from src.cat.catter import Catter
from src.configs.sqlyzr_config import SQLyzrConfig
from src.util.file_utils import read_json

load_dotenv()

from src.chart.charter import draw_all_charts
from src.configs.config_loader import load_config, ConfigData
from src.sqlyzr.augment_data import DatasetAugmentor


def extract_cats(conf: SQLyzrConfig):
    stats = []
    catter = Catter()
    for ds_conf in conf.eval_conf.dataset_configs:
        data = read_json(ds_conf.get_test_path())
        for row in data:
            query = row['query']
            stat = {
                'ver': ds_conf.ver,
                'dataset': ds_conf.dataset_type,
                'cat': catter.get_category(query).name,
                'sub': catter.get_sub_category(query).name
            }
            stats.append(stat)
    return pd.DataFrame(stats)


def draw_cat_charts(conf_path: str):
    conf = load_config(conf_path)
    df = extract_cats(conf)
    subs = natsorted(df['sub'].unique())
    cats = natsorted(df['cat'].unique())
    vers = natsorted(df['ver'].unique())

    ax = sns.countplot(df, x="cat", hue="ver", hue_order=vers, order=cats)
    # plt.figure(figsize=(5, 5))

    plt.savefig(os.path.join(conf.eval_conf.charts_dir, f"cat_count.png"))
    plt.clf()

    sns.countplot(df, x="sub", hue="ver", hue_order=vers, order=subs)
    plt.savefig(os.path.join(conf.eval_conf.charts_dir, f"sub_cat_count.png"))


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to the config file")
    args = parser.parse_args()
    conf = load_config(args.config)
    augmentor = DatasetAugmentor(conf)
    logger.info("Starting Augmentation")
    new_ver = await augmentor.augment_data(expand=True)
    logger.info("Augmentation Done!")
    conf_data = ConfigData.load(args.config)
    conf_data.dataset_versions.append(new_ver)
    shutil.copy(args.config, f"{args.config}.bak")
    conf_data.save(args.config)
    draw_cat_charts(args.config)


if __name__ == "__main__":
    asyncio.run(main())
