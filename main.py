import argparse

from src.assets.print_logo import print_logo
from src.sqlyzr.sqlyzr import Sqlyzr
from src.util.log_util import configure_logging
import asyncio


# FIXME: No error on connection error


async def main(config_path: str):
    configure_logging()
    sqlyzr = Sqlyzr(config_path)
    await sqlyzr.run()


if __name__ == '__main__':
    print_logo()
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", required=False, default="conf.json")
    args = parser.parse_args()
    asyncio.run(main(args.config))
