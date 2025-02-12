from src.assets.print_logo import print_logo
from src.sqlyzr.sqlyzr import Sqlyzr
from src.util.log_util import configure_logging
import asyncio


# FIXME: No error on connection error

async def main():
    configure_logging()
    sqlyzr = Sqlyzr()
    await sqlyzr.run()


if __name__ == '__main__':
    print_logo()
    asyncio.run(main())
