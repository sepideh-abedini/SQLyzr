import os.path
import shutil
from pathlib import Path

from src.configs.datasets import SPIDER_SMALL, BIRD_SMALL
from src.eval.dataset_config import DatasetConfig
from src.util.file_utils import read_json

ds_confs = [SPIDER_SMALL, BIRD_SMALL]

SAMPLE_DIR = "sample_data"


def copy_to_sample_dir(src_path):
    path = Path(src_path)
    segments = path.parts
    dst_segments = (SAMPLE_DIR, *segments[1:])
    dst_path = "/".join(dst_segments)
    print(f"Copying: {src_path} -> {dst_path}")
    Path(dst_path).parent.mkdir(parents=True, exist_ok=True)
    if os.path.isdir(src_path):
        shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
    else:
        shutil.copy(src_path, dst_path)
    return dst_path


def copy_dbs(ds_conf: DatasetConfig):
    data = read_json(ds_conf.get_tables_path())
    db_ids = set(map(lambda x: x["db_id"], data))
    for db_id in db_ids:
        copy_to_sample_dir(os.path.join(ds_conf.get_db_path(), db_id))


shutil.rmtree(SAMPLE_DIR, ignore_errors=True)

for ds_conf in ds_confs:
    for f in [
        ds_conf.get_train_path(),
        ds_conf.get_tables_path(),
    ]:
        copy_to_sample_dir(f)

    for f in [
        ds_conf.get_test_path(),
        ds_conf.get_gold_path(),
    ]:
        dst_path = copy_to_sample_dir(f)
    copy_dbs(ds_conf)
