import argparse
import asyncio
import os
import time

from dotenv import load_dotenv
from loguru import logger

from src.util.monitor import MonitorProcess

load_dotenv()

from src.sqlyzr.sqlyzr import Sqlyzr


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to the config file")
    args = parser.parse_args()
    # monitor = MonitorProcess(os.getpid())
    # monitor.start()
    sqlyzr = Sqlyzr(args.config)
    logger.info("Starting Sqlyzr")
    await sqlyzr.run()
    # time.sleep(100)
    logger.info("Sqlyzr Done!")
    # monitor.stop()


if __name__ == "__main__":
    asyncio.run(main())
