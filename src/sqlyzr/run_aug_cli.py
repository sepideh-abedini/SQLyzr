import argparse
import asyncio
import time
from loguru import logger

from src.configs.config_loader import load_config
from src.sqlyzr.augment_data import DatasetAugmentor
from src.sqlyzr.sqlyzr import Sqlyzr


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to the config file")
    args = parser.parse_args()
    conf = load_config(args.config)
    augmentor = DatasetAugmentor(conf)
    logger.info("Starting Augmentation")
    await augmentor.augment_data()
    logger.info("Augmentation Done!")


if __name__ == "__main__":
    asyncio.run(main())
