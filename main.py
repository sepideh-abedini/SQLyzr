from loguru import logger
from dotenv import load_dotenv

from src.util.log_util import configure_logging

load_dotenv()
configure_logging()

logger.info("Loading modules")
import argparse
import asyncio

from src.app_setup import setup_app
from src.assets.print_logo import print_logo
from src.sqlyzr.sqlyzr import Sqlyzr

logger.info("Python modules loaded!")


async def main(config_path: str):
    sqlyzr = Sqlyzr(config_path)
    logger.info("Starting SQLyzr")
    await sqlyzr.run()
    logger.info("Finished SQLyzr")


if __name__ == '__main__':
    setup_app()
    print_logo()
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", required=False, default="conf.json")
    args = parser.parse_args()
    asyncio.run(main(args.config))
