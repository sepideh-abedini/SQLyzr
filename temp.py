import asyncio
import time

from loguru import logger

from src.app_setup import setup_app
from src.assets.print_logo import print_logo
from src.sqlyzr.sqlyzr import Sqlyzr


async def bar():
    logger.info("STARTING SQLYZR")
    print_logo()
    sqlyzr = Sqlyzr("gui.json")
    await sqlyzr.run()
    logger.info("FINISHED SQLYZR")


def main():
    setup_app()
    asyncio.run(bar())


if __name__ == '__main__':
    main()
