import asyncio
import time

from src.app_setup import setup_app
from src.sqlyzr.sqlyzr import Sqlyzr


async def bar():
    sqlyzr = Sqlyzr("gui.json")
    await sqlyzr.run()
    try:
        print("STARTING SQLYZR")
        time.sleep(20)
        print("FINISHED SQLYZR")
    except InterruptedError:
        print("INTERRUPTED SQLYZR")


def main():
    setup_app()
    asyncio.run(bar())


if __name__ == '__main__':
    main()
