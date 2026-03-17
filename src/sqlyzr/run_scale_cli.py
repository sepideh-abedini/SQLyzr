import argparse
import asyncio

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

from src.configs.config_loader import load_config
from src.new_scale.apply_sdv import apply_scaling
from src.new_scale.insert import backup_and_revert
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
    # db_ids = db_ids[:1]
    scales = conf.eval_conf.scales
    for scale in scales:
        if scale <= 1:
            continue
        for db_id in db_ids:
            logger.info(f"Scaling {db_id} :")
            apply_scaling(ds_conf, db_id, scale)
            logger.info(f"Scaling {db_id} DONE!")
        logger.info(f"Scaling for scale = {scale} DONE!")
    print(db_ids)


if __name__ == "__main__":
    asyncio.run(main())
