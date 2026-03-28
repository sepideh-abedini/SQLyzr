import asyncio

from loguru import logger
from pydash import assign_with

from src.app_setup import setup_app
from src.assets.print_logo import print_logo
from src.configs.config_loader import load_config
from src.sqlyzr.sqlyzr import Sqlyzr

CONF_PATH = "confs/gui.json"


async def run_gui(allow_aug: bool = True):
    logger.info("STARTING SQLYZR")
    print_logo()
    sqlyzr = Sqlyzr(CONF_PATH)
    await sqlyzr.run(allow_aug=allow_aug)
    logger.info("FINISHED SQLYZR")


async def main():
    setup_app()
    await run_gui()
    conf = load_config(CONF_PATH)
    if conf.pipeline.augment:
        logger.info("Running SQLYZR for second time after augmentation")
        await run_gui(allow_aug=False)
        logger.info("Second SQLYZR fun finished!")


if __name__ == '__main__':
    asyncio.run(main())
