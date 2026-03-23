import argparse
import asyncio
import hashlib
import os
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger
from ply.yacc import error_count

from src.eval.dataset_config import DatasetConfig
from src.new_scale.db_utils import get_total_row_count

load_dotenv()

from src.configs.config_loader import load_config
from src.new_scale.apply_sdv import apply_scaling
from src.util.file_utils import read_json, write_json


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
    db_dir = f"{ds_conf.get_db_path()}_{scale}"
    db_ids = os.listdir(db_dir)
    db_stats = dict()
    for db_id in db_ids:
        if not os.path.isdir(os.path.join(db_dir, db_id)):
            continue
        db_path = os.path.join(db_dir, db_id, f"{db_id}.sqlite")
        total_rows = get_total_row_count(db_path)
        db_stats[db_id] = total_rows
    return db_stats


def save_hash(ds_conf: DatasetConfig, scale: int):
    db_stats = hash_dbs(ds_conf, scale)
    db_dir = f"{ds_conf.get_db_path()}_{scale}"
    write_json(os.path.join(db_dir, "dbs.json"), db_stats)


def read_has(ds_conf: DatasetConfig, scale: int):
    db_dir = f"{ds_conf.get_db_path()}_{scale}"
    db_stats = read_json(os.path.join(db_dir, "dbs.json"))
    test_data = read_json(ds_conf.get_test_path())
    used_dbs = set(map(lambda x: x["db_id"], test_data))


def verify_hash(ds_conf: DatasetConfig, scale: int, db_ids: set[str]):
    db_dir = f"{ds_conf.get_db_path()}_{scale}"
    stats_path = os.path.join(db_dir, "dbs.json")
    if not os.path.exists(stats_path):
        return False
    actual_stats = read_json(stats_path)
    expected_stats = hash_dbs(ds_conf, scale)
    return db_ids.issubset(set(actual_stats.keys()))


def scale_dbs(conf_path: str):
    conf = load_config(conf_path)
    db_ids = set()
    ds_conf = max(conf.eval_conf.dataset_configs, key=lambda x: int(x.ver[1:]))
    # ds_conf = conf.eval_conf.dataset_configs[0]
    data = read_json(ds_conf.get_test_path())
    db_ids = db_ids.union(set(map(lambda x: x["db_id"], data)))
    db_ids = sorted(list(db_ids))
    scales = conf.eval_conf.scales
    for scale in scales:
        if scale <= 1:
            continue
        if verify_hash(ds_conf, scale, set(db_ids)):
            logger.info(f"Scaling for scale = {scale} exist, skipping!")
            continue

        logger.info(f"Starting scaling for scale = {scale}!")

        for db_id in db_ids:
            logger.info(f"Scaling {db_id} :")
            apply_scaling(ds_conf, db_id, scale)
            logger.info(f"Scaling {db_id} DONE!")
        save_hash(ds_conf, scale)
        logger.info(f"Scaling for scale = {scale} DONE!")
    return scales


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to the config file")
    args = parser.parse_args()
    scale_dbs(args.config)

    #


if __name__ == "__main__":
    asyncio.run(main())
