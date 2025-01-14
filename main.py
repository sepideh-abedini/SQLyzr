import asyncio

from assets.print_logo import print_logo
from src.sqlyzr.sqlyzr import Sqlyzr


async def main():
    sqlyzr = Sqlyzr()
    await sqlyzr.run()


if __name__ == '__main__':
    print_logo()
    asyncio.run(main())
