import argparse
import asyncio

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

from src.sqlyzr.sqlyzr import Sqlyzr


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to the config file")
    args = parser.parse_args()
    sqlyzr = Sqlyzr(args.config)
    logger.info("Starting Sqlyzr")
    await sqlyzr.run()
    logger.info("Sqlyzr Done!")


if __name__ == "__main__":
    asyncio.run(main())
