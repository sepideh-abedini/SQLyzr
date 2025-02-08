import asyncio
import os
import sys

from src.assets.print_logo import print_logo
from src.sqlyzr.sqlyzr import Sqlyzr
from loguru import logger

logger.remove(0)
logger.add(sys.stderr, level=os.environ.get("LOG_LEVEL", "INFO").upper(), colorize=True,
           format="<green>{time:HH:mm:ss} | </green><cyan>[{module}:{function}:{line}]</cyan><level> {level}: {message}</level>")


async def main():
    sqlyzr = Sqlyzr()
    await sqlyzr.run()


if __name__ == '__main__':
    print_logo()
    asyncio.run(main())
