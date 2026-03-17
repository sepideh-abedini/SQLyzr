import argparse
import asyncio
import time
from dataclasses import replace

from loguru import logger

from src.configs.config_loader import load_config, ConfigData
from src.sqlyzr.sqlyzr import Sqlyzr
from tests.aug_collect_small_data import collect_small_data


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to the config file")
    args = parser.parse_args()
    conf_data = ConfigData.load(args.config)
    conf_data = conf_data.model_copy(update={
        "dataset_versions": [conf_data.dataset_versions[0]]
    })
    conf_data.save(args.config)


if __name__ == "__main__":
    asyncio.run(main())
