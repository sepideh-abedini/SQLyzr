import argparse
import asyncio
import os

from loguru import logger

from src.app_setup import setup_app
from src.assets.print_logo import print_logo
from src.eval.lib import Timer
from src.sqlyzr.sqlyzr import Sqlyzr
from src.util.monitor import MonitorProcess


async def main(config_path: str):
    sqlyzr = Sqlyzr(config_path)
    logger.info("Starting SQLyzr")
    await sqlyzr.run()
    logger.info("Finished SQLyzr")


if __name__ == '__main__':
    setup_app()
    timer = Timer.start()
    monitor = MonitorProcess(os.getpid())
    print_logo()
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", required=False, default="conf.json")
    args = parser.parse_args()
    monitor.start()
    asyncio.run(main(args.config))
    monitor.terminate()
    print("TOTAL TIME: ", timer.lap())
