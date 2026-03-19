import argparse
import asyncio
import hashlib
import os
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

from src.eval.dataset_config import DatasetConfig

load_dotenv()

from src.configs.config_loader import load_config
from src.new_scale.apply_sdv import apply_scaling
from src.util.file_utils import read_json


def get_combined_hash(file_paths, algorithm="sha256"):
    master_hash = hashlib.new(algorithm)

    for path in sorted(file_paths):
        file_obj = Path(path)
        if not file_obj.is_file():
            continue

        with open(file_obj, "rb") as f:
            file_digest = hashlib.file_digest(f, algorithm).digest()

        master_hash.update(file_digest)

    return master_hash.hexdigest()


def hash_dbs(ds_conf, scale: int):
    data = read_json(ds_conf.get_test_path())
    db_ids = set(map(lambda x: x["db_id"], data))
    db_paths = list(map(lambda x: ds_conf.get_db_file_path(x, scale), db_ids))
    db_hash = get_combined_hash(db_paths)
    return db_hash


def save_hash(ds_conf: DatasetConfig, scale: int):
    h = hash_dbs(ds_conf, scale)
    db_dir = f"{ds_conf.get_db_path()}_{scale}"
    with open(os.path.join(db_dir, f"dbs.hash"), "w") as f:
        f.write(h)


def verify_hash(ds_conf: DatasetConfig, scale: int):
    actual_hash = hash_dbs(ds_conf, scale)
    db_dir = f"{ds_conf.get_db_path()}_{scale}"
    hash_path = os.path.join(db_dir, f"dbs.hash")
    if not os.path.exists(hash_path):
        return False
    with open(hash_path, "r") as f:
        expected_hash = f.read()
    return actual_hash == expected_hash


def scale_dbs(conf_path: str):
    conf = load_config(conf_path)
    db_ids = set()
    ds_conf = conf.eval_conf.dataset_configs[0]
    data = read_json(ds_conf.get_test_path())
    db_ids = db_ids.union(set(map(lambda x: x["db_id"], data)))
    db_ids = sorted(list(db_ids))
    scales = conf.eval_conf.scales
    for scale in scales:
        if scale <= 1:
            continue
        if verify_hash(ds_conf, scale):
            logger.info(f"Scaling for scale = {scale} exist, skipping!")
            continue

        logger.info(f"Starting scaling for scale = {scale}!")

        for db_id in db_ids:
            logger.info(f"Scaling {db_id} :")
            apply_scaling(ds_conf, db_id, scale)
            logger.info(f"Scaling {db_id} DONE!")
        save_hash(ds_conf, scale)
        logger.info(f"Scaling for scale = {scale} DONE!")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to the config file")
    args = parser.parse_args()
    scale_dbs(args.config)

    #


if __name__ == "__main__":
    asyncio.run(main())
