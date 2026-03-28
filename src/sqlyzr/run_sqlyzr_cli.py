import argparse
import asyncio
import os
import time

from dotenv import load_dotenv
from loguru import logger

from src.configs.config_loader import load_config
from src.util.monitor import MonitorProcess

load_dotenv()

from src.sqlyzr.sqlyzr import Sqlyzr


async def run_sqlyzr_once(conf_path: str, allow_aug: bool = True):
    sqlyzr = Sqlyzr(conf_path)
    logger.info("Starting Sqlyzr")
    await sqlyzr.run(allow_aug=allow_aug)
    logger.info("Sqlyzr Done!")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to the config file")
    args = parser.parse_args()
    await run_sqlyzr_once(args.config)
    conf = load_config(args.config)
    if conf.pipeline.augment:
        logger.info("Running second evaluation iteration after augmentation")
        await run_sqlyzr_once(args.conf_path, allow_aug=False)
    # monitor.stop()


if __name__ == "__main__":
    asyncio.run(main())
