import argparse
import asyncio
import os.path
import time
from loguru import logger

from src.configs.config_loader import load_config
from src.new_scale.apply_sdv import apply_scaling
from src.new_scale.insert import backup_and_revert
from src.scalar.tmp import scale_db
from src.sqlyzr.augment_data import DatasetAugmentor
from src.sqlyzr.sqlyzr import Sqlyzr
from src.util.file_utils import read_json


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to the config file")
    args = parser.parse_args()
    conf = load_config(args.config)
    db_ids = set()
    ds_conf = conf.eval_conf.dataset_configs[0]
    # for ds_conf in conf.eval_conf.dataset_configs:
    data = read_json(ds_conf.get_test_path())
    db_ids = db_ids.union(set(map(lambda x: x["db_id"], data)))
    db_ids = sorted(list(db_ids))
    scale = 1
    for db_id in db_ids:
        if scale == 0:
            logger.info(f"Reverting {db_id} :")
            backup_and_revert(ds_conf.get_db_file_path(db_id))
        else:
            logger.info(f"Scaling {db_id} :")
            apply_scaling(ds_conf, db_id, 1)
            logger.info(f"Scaling {db_id} DONE!")
    print(db_ids)


if __name__ == "__main__":
    asyncio.run(main())
