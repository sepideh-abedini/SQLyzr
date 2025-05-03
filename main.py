import argparse
import os
import platform

from loguru import logger

from monitor import MonitorProcess
from src.assets.print_logo import print_logo
from src.eval.lib import Timer
from src.sqlyzr.sqlyzr import Sqlyzr
from src.util.log_util import configure_logging
import asyncio
import multiprocessing as mp


# FIXME: No error on connection error


async def main(config_path: str):
    configure_logging()
    sqlyzr = Sqlyzr(config_path)
    logger.info("Starting SQLyzr")
    await sqlyzr.run()
    logger.info("Finished SQLyzr")


if __name__ == '__main__':
    if platform.system() == "Linux":
        mp.set_start_method("spawn", force=True)
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
