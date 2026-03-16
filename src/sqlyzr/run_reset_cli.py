import argparse
import asyncio
import time
from loguru import logger

from src.configs.config_loader import load_config
from src.sqlyzr.sqlyzr import Sqlyzr
from tests.aug_collect_small_data import collect_small_data


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to the config file")
    args = parser.parse_args()
    conf = load_config(args.config)
    logger.info("Starting Reset")
    for ds in conf.eval_conf.dataset_configs:
        await collect_small_data(ds)
    logger.info("Reset Done!")


if __name__ == "__main__":
    asyncio.run(main())
